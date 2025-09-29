import 'dotenv/config';
import express from 'express';
import cors from 'cors';

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 6001;

// Simple decision engine placeholder
// Accepts a proposed transfer, returns approve/deny with confidence
app.post('/decide', (req, res) => {
  const { fromAgent, toAgent, amountAda } = req.body || {};
  if (!fromAgent || !toAgent || !amountAda) return res.status(400).json({ error: 'fromAgent,toAgent,amountAda required' });
  // TODO: market, risk, identity, balances
  const approve = Number(amountAda) <= 5; // trivial example rule
  res.json({ approve, confidence: approve ? 0.9 : 0.2, strategy: 'conservative' });
});

app.post('/on-receive', (req, res) => {
  const { toAgent, txId } = req.body || {};
  if (!toAgent || !txId) return res.status(400).json({ error: 'toAgent,txId required' });
  // TODO: update agent state, analytics, acknowledgments
  res.json({ ok: true, toAgent, txId });
});

app.get('/health', (_req, res) => res.json({ ok: true }));

app.listen(PORT, () => console.log(`AI Agents service on :${PORT}`));
