import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { SerialPort } from 'serialport';
import { ReadlineParser } from '@serialport/parser-readline';
import { fetch } from 'undici';
import { createServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';

const app = express();
app.use(cors());
app.use(express.json());

const httpServer = createServer(app);
const io = new SocketIOServer(httpServer, { cors: { origin: '*' } });

const PORT = process.env.PORT || 5001;
const SERIAL_PATH = process.env.SERIAL_PATH || ''; // e.g. COM3 on Windows
const SERIAL_BAUD = Number(process.env.SERIAL_BAUD || 9600);

let port; let parser;

async function connectSerial() {
  if (!SERIAL_PATH) {
    console.warn('No SERIAL_PATH set. Set env SERIAL_PATH=COM3 (Windows)');
    return;
  }
  try {
    port = new SerialPort({ path: SERIAL_PATH, baudRate: SERIAL_BAUD });
    parser = port.pipe(new ReadlineParser({ delimiter: '\n' }));
    parser.on('data', onSerialLine);
    port.on('error', (e) => io.emit('serial:error', { message: e.message }));
    port.on('close', () => io.emit('serial:close', {}));
    io.emit('serial:open', { path: SERIAL_PATH, baud: SERIAL_BAUD });
  } catch (e) {
    io.emit('serial:error', { message: e.message });
  }
}

function onSerialLine(lineRaw) {
  const line = lineRaw.trim();
  io.emit('serial:line', { line });
  if (line === 'TRIGGER_PAYMENT') {
    state.currentCommand = { from: null, to: null, amount: null };
  } else if (line.startsWith('FROM_AGENT:')) {
    state.currentCommand.from = line.replace('FROM_AGENT:', '').trim();
  } else if (line.startsWith('TO_AGENT:')) {
    state.currentCommand.to = line.replace('TO_AGENT:', '').trim();
  } else if (line.startsWith('AMOUNT:')) {
    state.currentCommand.amount = Number(line.replace('AMOUNT:', '').trim());
  } else if (line === 'END_COMMAND') {
    triggerPayment(state.currentCommand).catch(err => io.emit('payment:error', { error: err.message }));
    state.currentCommand = null;
  }
}

const state = { currentCommand: null };

async function triggerPayment(cmd) {
  io.emit('payment:trigger', cmd);
  // Forward to Masumi Payment Service
  const url = process.env.MASUMI_PAYMENT_URL || 'http://localhost:3001/api/cardano/transfer';
  const body = { fromAgent: cmd.from, toAgent: cmd.to, amountAda: cmd.amount };
  if (process.env.AGENT1_SKEY_CBOR) {
    body.skeyCbor = process.env.AGENT1_SKEY_CBOR.trim();
  }
  let data;
  try {
    const res = await fetch(url, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
    });
    data = await res.json();
    if (!res.ok) {
      throw new Error(data?.error || `HTTP ${res.status}`);
    }
  } catch (err) {
    data = { error: err.message };
  }
  io.emit('payment:response', data);
  // Optionally, write back to Arduino
  if (port && port.writable) {
    const tx = data.tx_id || data.txHash || 'ERR';
    port.write(`TX:${tx}\n`);
  }
}

app.get('/health', (_req, res) => res.json({ ok: true }));

// Optional test endpoint to trigger payment without serial hardware
app.post('/simulate', async (req, res) => {
  try {
    const payload = req.body?.fromAgent ? req.body : {
      fromAgent: process.env.AGENT1_ID || 'satoshi-1',
      toAgent: process.env.AGENT2_ID || 'satoshi-2',
      amountAda: Number(process.env.SIM_AMOUNT || 1)
    };
    await triggerPayment(payload);
    res.json({ ok: true });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

io.on('connection', (socket) => {
  socket.emit('hello', { ts: Date.now() });
});

httpServer.listen(PORT, () => {
  console.log(`Arduino Bridge on :${PORT}`);
  connectSerial();
});
