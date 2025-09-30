import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { createServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';
import pkg from 'pg';
import Redis from 'ioredis';
import { fetch } from 'undici';

const { Pool } = pkg;

const app = express();
app.use(cors());
app.use(express.json());

const httpServer = createServer(app);
const io = new SocketIOServer(httpServer, { cors: { origin: '*' } });

const PORT = Number(process.env.PORT || 3001);
const pool = new Pool({ connectionString: process.env.DATABASE_URL });
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');
const CARDANO_SVC = process.env.MASUMI_CARDANO_INTEGRATION_URL || 'http://localhost:4002';
const AGENTS_SVC = process.env.AI_AGENTS_URL || 'http://localhost:6001';

// Align canonical agent IDs for demo
const DEFAULT_AGENT1_ID = process.env.AGENT1_ID || 'satoshi_alpha_001';
const DEFAULT_AGENT2_ID = process.env.AGENT2_ID || 'satoshi_beta_002';
const AGENT_MAP = {
  [DEFAULT_AGENT1_ID]: { id: DEFAULT_AGENT1_ID, address: process.env.AGENT1_ADDRESS },
  [DEFAULT_AGENT2_ID]: { id: DEFAULT_AGENT2_ID, address: process.env.AGENT2_ADDRESS },
};

function getAgentAddress(agentId) {
  const a = AGENT_MAP[agentId];
  return a?.address;
}

// Wallet roles mapping (Masumi Preprod model)
const PURCHASE_WALLET_ADDRESS = process.env.PURCHASE_WALLET_ADDRESS || process.env.AGENT1_ADDRESS || null;
const SELLING_WALLET_ADDRESS = process.env.SELLING_WALLET_ADDRESS || process.env.AGENT2_ADDRESS || null;
const COLLECTION_WALLET_ADDRESS = process.env.COLLECTION_WALLET_ADDRESS || null;
const PURCHASE_WALLET_MNEMONIC = process.env.PURCHASE_WALLET_MNEMONIC || null;
const SELLING_WALLET_MNEMONIC = process.env.SELLING_WALLET_MNEMONIC || null;

// DB bootstrap
await pool.query(`CREATE TABLE IF NOT EXISTS transactions (
  id SERIAL PRIMARY KEY,
  tx_id TEXT,
  from_agent TEXT,
  to_agent TEXT,
  amount NUMERIC,
  status TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);`);

// Events
function broadcast(event, payload) {
  io.emit(event, payload);
}

// Health
app.get('/health', (_req, res) => res.json({ ok: true }));

// Wallets API (preprod): expose addresses and balances for admin UI
app.get('/api/wallets', async (_req, res) => {
  try {
    const network = 'preprod';
    const wallets = [];
    if (PURCHASE_WALLET_ADDRESS) wallets.push({ role: 'purchase', address: PURCHASE_WALLET_ADDRESS });
    if (SELLING_WALLET_ADDRESS) wallets.push({ role: 'selling', address: SELLING_WALLET_ADDRESS });
    if (COLLECTION_WALLET_ADDRESS) wallets.push({ role: 'collection', address: COLLECTION_WALLET_ADDRESS });

    // fetch balances
    const results = [];
    for (const w of wallets) {
      try {
        const r = await fetch(`${CARDANO_SVC}/balance/${w.address}`);
        const data = await r.json();
        results.push({ ...w, balance: data });
      } catch (e) {
        results.push({ ...w, balance: { error: String(e?.message || e) } });
      }
    }
    res.json({ network, wallets: results });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

// Export mnemonics (if configured) — behind admin token
app.get('/api/wallets/export', (req, res) => {
  const adminToken = process.env.ADMIN_TOKEN;
  if (!adminToken || req.headers['x-admin-token'] !== adminToken) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  const { type } = req.query || {};
  if (!type) return res.status(400).json({ error: 'type required (purchase|selling)' });
  if (type === 'purchase' && PURCHASE_WALLET_MNEMONIC) return res.json({ mnemonic: PURCHASE_WALLET_MNEMONIC });
  if (type === 'selling' && SELLING_WALLET_MNEMONIC) return res.json({ mnemonic: SELLING_WALLET_MNEMONIC });
  return res.status(404).json({ error: 'Not configured' });
});

// Minimal Admin UI (preprod)
app.get('/admin', async (_req, res) => {
  const esc = (s) => (s || '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
  const rows = [];
  const wallets = [
    { role: 'Purchasing Wallet', key: 'purchase', address: PURCHASE_WALLET_ADDRESS },
    { role: 'Selling Wallet', key: 'selling', address: SELLING_WALLET_ADDRESS },
    { role: 'Collection Wallet', key: 'collection', address: COLLECTION_WALLET_ADDRESS },
  ];
  for (const w of wallets) {
    if (!w.address) continue;
    rows.push(`<tr><td>${w.role}</td><td><code>${esc(w.address)}</code></td>
      <td><button onclick="copy('${esc(w.address)}')">Copy</button></td>
      <td>${w.key !== 'collection' ? `<button onclick="exportMnemonic('${w.key}')">Export Mnemonic</button>` : '-'}</td>
    </tr>`);
  }
  const html = `<!doctype html>
  <html><head><meta charset="utf-8"/><title>Masumi Admin (Preprod)</title>
  <style>body{font-family:system-ui;margin:24px;} table{border-collapse:collapse} td,th{border:1px solid #ddd;padding:8px}</style>
  </head><body>
  <h2>Masumi Admin — Wallets (Preprod)</h2>
  <p>Use faucets to fund wallets for testing: 
    <a href="https://docs.cardano.org/cardano-testnet/tools/faucet/" target="_blank">Cardano Faucet</a> · 
    <a href="https://faucet.masumi.network" target="_blank">Masumi Faucet</a>
  </p>
  <table><thead><tr><th>Role</th><th>Address</th><th>Copy</th><th>Export</th></tr></thead>
  <tbody>${rows.join('')}</tbody></table>
  <h3>Balances</h3>
  <pre id="balances">Loading...</pre>
  <script>
    async function copy(text){ await navigator.clipboard.writeText(text); alert('Copied'); }
    async function exportMnemonic(type){ 
      const r = await fetch('/api/wallets/export?type='+type, { headers: { 'x-admin-token': '${process.env.ADMIN_TOKEN || ''}' } });
      if(!r.ok){ alert('Not configured'); return; }
      const j = await r.json(); alert(j.mnemonic);
    }
    (async ()=>{
      const r = await fetch('/api/wallets'); const j = await r.json();
      document.getElementById('balances').textContent = JSON.stringify(j, null, 2);
    })();
  </script>
  </body></html>`;
  res.setHeader('content-type', 'text/html').send(html);
});

// Cardano endpoints via integration service
app.post('/api/cardano/transfer', async (req, res) => {
  try {
    const { fromAgent, toAgent, amountAda, metadata, skeyCbor, skeyJsonPath } = req.body || {};
    if (!fromAgent || !toAgent || !amountAda) return res.status(400).json({ error: 'fromAgent,toAgent,amountAda required' });

    const fromAddress = getAgentAddress(fromAgent);
    const toAddress = getAgentAddress(toAgent);
    if (!fromAddress || !toAddress) return res.status(400).json({ error: 'Unknown agent mapping to address' });

    const amountLovelace = Math.round(Number(amountAda) * 1_000_000);
    // Ask Agent 1 to approve
    const d = await fetch(`${AGENTS_SVC}/decide`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ fromAgent, toAgent, amountAda }) });
    const decision = await d.json();
    if (!d.ok || decision.approve !== true) {
      return res.status(403).json({ error: 'Agent denied transfer', decision });
    }

    const r = await fetch(`${CARDANO_SVC}/transfer`, {
      method: 'POST', headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ fromAddress, toAddress, amountLovelace, metadata, skeyCbor, skeyJsonPath })
    });
    const data = await r.json();
    if (!r.ok) return res.status(r.status).json(data);

    const txId = data.txHash;
    await pool.query('INSERT INTO transactions(tx_id,from_agent,to_agent,amount,status) VALUES($1,$2,$3,$4,$5)', [txId, fromAgent, toAgent, amountAda, 'submitted']);
    const payload = { tx_id: txId, from_agent: fromAgent, to_agent: toAgent, amount: amountAda, status: 'submitted' };
    broadcast('transaction:new', payload);
    // Notify Agent 2 of incoming tx (acknowledgment task)
    try {
      await fetch(`${AGENTS_SVC}/on-receive`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ toAgent, txId }) });
    } catch (e) {
      console.warn('Agent on-receive notify failed', e?.message || e);
    }
    res.status(200).json(payload);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/api/cardano/balance/:address', async (req, res) => {
  try {
    const r = await fetch(`${CARDANO_SVC}/balance/${req.params.address}`);
    const data = await r.json();
    res.status(r.ok ? 200 : r.status).json(data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/api/cardano/transaction/:txId', async (req, res) => {
  try {
    const r = await fetch(`${CARDANO_SVC}/transaction/${req.params.txId}`);
    const data = await r.json();
    res.status(r.ok ? 200 : r.status).json(data);
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/api/latest-transaction', async (_req, res) => {
  const { rows } = await pool.query('SELECT * FROM transactions ORDER BY created_at DESC LIMIT 1');
  res.json(rows[0] || null);
});

io.on('connection', (socket) => {
  socket.emit('hello', { ts: Date.now() });
});

httpServer.listen(PORT, () => console.log(`Masumi Payment Service on :${PORT}`));
