import 'dotenv/config';
import express from 'express';
import cors from 'cors';

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 4001;

// Placeholder for official Satoshi BTC Wallet toolkit integration
// When available, import and initialize the SDK with API keys and network.
// e.g., import { SatoshiClient } from 'btc-wallet';

app.get('/health', (_req, res) => res.json({ ok: true, network: process.env.SATOSHI_NETWORK || 'testnet' }));

app.post('/transfer', async (req, res) => {
  const { fromWalletId, toWalletId, amount } = req.body || {};
  if (!fromWalletId || !toWalletId || !amount) return res.status(400).json({ error: 'fromWalletId,toWalletId,amount required' });
  // TODO: call Satoshi SDK to perform transfer, return tx hash
  res.status(501).json({ error: 'Satoshi SDK wiring required' });
});

app.post('/deposit', async (req, res) => {
  // TODO: deposit using bridge
  res.status(501).json({ error: 'Not Implemented' });
});

app.get('/balance/:walletId', async (req, res) => {
  // TODO: fetch balance
  res.status(501).json({ error: 'Not Implemented' });
});

app.get('/transaction/:txId', async (req, res) => {
  // TODO: fetch tx details via SDK or explorer API
  res.status(501).json({ error: 'Not Implemented' });
});

app.listen(PORT, () => console.log(`Satoshi Integration on :${PORT}`));
