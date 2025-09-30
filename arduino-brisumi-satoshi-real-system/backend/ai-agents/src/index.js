import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { fetch } from 'undici';

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 6001;
const SOKOSUMI_WEBHOOK_URL = process.env.SOKOSUMI_WEBHOOK_URL || '';
const SOKOSUMI_API_KEY = process.env.SOKOSUMI_API_KEY || '';

async function notifySokosumi(event, payload) {
  if (!SOKOSUMI_WEBHOOK_URL || !SOKOSUMI_API_KEY) return;
  try {
    await fetch(SOKOSUMI_WEBHOOK_URL, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'authorization': `Bearer ${SOKOSUMI_API_KEY}`
      },
      body: JSON.stringify({ source: 'ai-agents', event, payload, ts: Date.now() })
    });
  } catch (e) {
    // silent failure to avoid impacting core flow
  }
}

// Simple decision engine placeholder
// Accepts a proposed transfer, returns approve/deny with confidence
app.post('/decide', (req, res) => {
  const { fromAgent, toAgent, amountAda } = req.body || {};
  if (!fromAgent || !toAgent || !amountAda) return res.status(400).json({ error: 'fromAgent,toAgent,amountAda required' });
  // TODO: market, risk, identity, balances
  const approve = Number(amountAda) <= 5; // trivial example rule
  const decision = { approve, confidence: approve ? 0.9 : 0.2, strategy: 'conservative' };
  notifySokosumi('decision', { fromAgent, toAgent, amountAda, decision }).catch(()=>{});
  res.json(decision);
});

app.post('/on-receive', (req, res) => {
  const { toAgent, txId } = req.body || {};
  if (!toAgent || !txId) return res.status(400).json({ error: 'toAgent,txId required' });
  // TODO: update agent state, analytics, acknowledgments
  const ack = { ok: true, toAgent, txId };
  notifySokosumi('receipt', ack).catch(()=>{});
  res.json(ack);
});

app.get('/health', (_req, res) => res.json({ ok: true }));

app.listen(PORT, () => console.log(`AI Agents service on :${PORT}`));
