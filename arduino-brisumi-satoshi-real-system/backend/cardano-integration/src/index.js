import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { Lucid, Blockfrost } from 'lucid-cardano';
import { fetch } from 'undici';

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 4002;
const RAW_NETWORK = (process.env.CARDANO_NETWORK || 'preprod').toLowerCase();
const NETWORK = RAW_NETWORK === 'mainnet' ? 'Mainnet' : RAW_NETWORK === 'preview' ? 'Preview' : 'Preprod';
const BLOCKFROST_PROJECT_ID = process.env.BLOCKFROST_PROJECT_ID;
const BLOCKFROST_BASE_URL = process.env.BLOCKFROST_BASE_URL || 'https://cardano-preprod.blockfrost.io/api/v0';


let lucid;
async function getLucid() {
  if (!lucid) {
    lucid = await Lucid.new(new Blockfrost(BLOCKFROST_BASE_URL, BLOCKFROST_PROJECT_ID), NETWORK);
    try { await lucid.provider.getTimeSettings(); } catch {}
  }
  return lucid;
}

app.get('/health', (_req, res) => res.json({ ok: true, network: NETWORK }));

app.get('/balance/:address', async (req, res) => {
  try {
    const addr = req.params.address;
    const r = await fetch(`${BLOCKFROST_BASE_URL}/addresses/${addr}/utxos`, { headers: { project_id: BLOCKFROST_PROJECT_ID }});
    if (r.status === 404) {
      // Address not seen on chain yet (never funded) — treat as 0 balance on testnet
      return res.json({ address: addr, lovelace: 0, ada: 0 });
    }
    if (!r.ok) return res.status(r.status).json({ error: `Blockfrost ${r.status}` });
    const utxos = await r.json();
    const lovelace = utxos.reduce((sum, u) => sum + Number((u.amount || []).find(a => a.unit === 'lovelace')?.quantity || 0), 0);
    res.json({ address: addr, lovelace, ada: lovelace / 1_000_000 });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

app.get('/transaction/:txId', async (req, res) => {
  try {
    const r = await fetch(`${BLOCKFROST_BASE_URL}/txs/${req.params.txId}`, { headers: { project_id: BLOCKFROST_PROJECT_ID }});
    if (!r.ok) return res.status(r.status).json({ error: `Blockfrost ${r.status}` });
    const tx = await r.json();
    res.json(tx);
  } catch (e) {
    res.status(404).json({ error: e.message });
  }
});

// Transfer ADA: requires sender signing key (mnemonic, file path or CBOR) and from/to/amount
app.post('/transfer', async (req, res) => {
  try {
    const { fromAddress, toAddress, amountLovelace, skeyCbor, skeyJsonPath, mnemonic, metadata } = req.body || {};
    console.log('[transfer] incoming', { fromAddress, toAddress, amountLovelace: Number(amountLovelace) });
    if (!fromAddress || !toAddress || !amountLovelace) return res.status(400).json({ error: 'fromAddress,toAddress,amountLovelace required' });

  const l = await getLucid();
    // Ensure provider time settings are initialized (prevents zeroTime undefined)
    try { await l.provider.getTimeSettings(); } catch {}
    
    // Try mnemonic first (most reliable)
    const providedMnemonic = mnemonic || process.env.AGENT1_MNEMONIC || process.env.WALLET_MNEMONIC;
    if (providedMnemonic) {
      try {
        l.selectWalletFromSeed(providedMnemonic.trim());
        const wAddr = await l.wallet.address();
        console.log('[transfer] wallet selected from mnemonic; derived address', wAddr);
        // Continue to transaction below
      } catch (e) {
        console.error('[transfer] mnemonic failed', e);
        return res.status(400).json({ error: `Invalid mnemonic: ${e?.message || e}` });
      }
    } else {
      // Fall back to private key methods (legacy)

    // Load signing key
    function stripCbor(hex) {
      if (!hex) return hex;
      const h = hex.toLowerCase().replace(/[^0-9a-f]/g, '');
      if (h.startsWith('5820') && h.length >= 4 + 64) return h.slice(4, 4 + 64); // 32 bytes
      if (h.startsWith('5840') && h.length >= 4 + 128) return h.slice(4, 4 + 128); // 64 bytes (extended)
      return h;
    }

    function firstNonEmpty(...vals) {
      for (const v of vals) { if (v && String(v).trim().length > 0) return v; }
      return undefined;
    }

  const providedKey = firstNonEmpty(skeyCbor, process.env.AGENT1_SKEY_CBOR);
    if (providedKey) {
      const raw = providedKey.toString().trim();
      // Try multiple formats
      const rawStripped = stripCbor(raw);
     
      // For simple ed25519 keys, we need to create a full extended key (32 bytes key + 32 bytes chaincode)
      // If we only have 32 bytes, we'll pad with zeros for the chaincode
      let extendedKey = rawStripped;
      if (rawStripped.length === 64) {
        // 32 bytes (64 hex chars) - need to extend to 64 bytes (128 hex chars) with chaincode
        extendedKey = rawStripped + '0'.repeat(64); // Add 32 zero bytes as chaincode
      }
      
      const candidates = [
        raw,                              // Original (might have CBOR prefix)
        rawStripped,                      // Stripped (just the 32-byte key)
        extendedKey,                      // Extended with chaincode
        `5840${extendedKey}`             // CBOR prefix for 64-byte extended key
      ];
      let selected = false;
      for (const c of candidates) {
        try {
          l.selectWalletFromPrivateKey(c);
          // Smoke test: derive address, will throw if invalid
          // eslint-disable-next-line no-await-in-loop
          const wAddr = await l.wallet.address();
          console.log('[transfer] wallet selected; derived address', wAddr, 'using key format:', c.substring(0, 10) + '...');
          selected = true;
          break;
        } catch (e) {
          console.warn('[transfer] key candidate failed, trying next', { format: c.substring(0, 10), err: e?.message || String(e) });
        }
      }
      if (!selected) {
        console.error('[transfer] All key formats failed. Raw key:', raw.substring(0, 20) + '...', 'Stripped:', rawStripped.substring(0, 20) + '...', 'Extended:', extendedKey.substring(0, 20) + '...');
        return res.status(400).json({ error: 'Failed to use provided signing key - tried multiple formats including extended key' });
      }
    } else if (skeyJsonPath) {
      // In container, mounting secrets file recommended; left as TODO to read
      return res.status(400).json({ error: 'skeyJsonPath reading not implemented in container' });
    } else {
      return res.status(400).json({ error: 'No signing key or mnemonic provided. Set AGENT1_MNEMONIC or AGENT1_SKEY_CBOR environment variable.' });
    }
  } // End of else block for non-mnemonic

    // Validate derived wallet address matches the provided fromAddress (at least payment key hash)
    try {
      const walletAddr = await l.wallet.address();
      // If mismatch, continue but include a warning
      if (walletAddr !== fromAddress) {
        console.warn('Warning: Wallet address derived by key differs from fromAddress', { walletAddr, fromAddress });
      }
    } catch {}

    // Prefetch UTxOs to surface clear errors if empty
    let utxos;
    try {
      utxos = await l.wallet.getUtxos();
      if (!utxos || utxos.length === 0) {
        console.error('[transfer] no utxos for wallet');
        return res.status(400).json({ error: 'No UTxOs available for fromAddress. Ensure the address is funded and on Preprod.' });
      }
    } catch (e) {
      console.error('[transfer] getUtxos failed', e);
      return res.status(500).json({ error: `Failed to fetch UTxOs: ${e?.message || e}` });
    }

  let tx = l.newTx().payToAddress(toAddress, { lovelace: BigInt(amountLovelace) });
  // Optional: set short validity to avoid stale txs on slow dev networks (5 minutes)
  try { tx = tx.validTo(Date.now() + 5 * 60 * 1000); } catch {}
    if (metadata) {
      tx = tx.attachMetadata(674, metadata);
    }
    try {
      const unsigned = await tx.complete();
      const signed = await unsigned.sign().complete();
      const txHash = await signed.submit();
      return res.status(200).json({ txHash });
    } catch (e) {
      console.error('[transfer] submit failed', e);
      return res.status(500).json({ error: `Submit failed: ${e?.message || e}` });
    }
  } catch (e) {
    console.error('[transfer] unhandled error', e);
    res.status(500).json({ error: e?.message || String(e) });
  }
});

app.listen(PORT, () => console.log(`Cardano Integration on :${PORT}`));
