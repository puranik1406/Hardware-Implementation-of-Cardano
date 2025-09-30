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

const PORT = Number(process.env.PORT || 5001);
const SERIAL_PATH = process.env.SERIAL_PATH || ''; // e.g. COM3 on Windows - Payment Trigger Arduino
const SERIAL_BAUD = Number(process.env.SERIAL_BAUD || 9600);
const DISPLAY_SERIAL_PATH = process.env.DISPLAY_SERIAL_PATH || ''; // e.g. COM4 - Transaction Display Arduino
const DISPLAY_SERIAL_BAUD = Number(process.env.DISPLAY_SERIAL_BAUD || 9600);

let port; let parser;
let displayPort; let displayParser;

async function connectSerial() {
  // Connect to Payment Trigger Arduino
  if (!SERIAL_PATH) {
    console.warn('No SERIAL_PATH set. On Windows set env SERIAL_PATH=COM3 (check Arduino IDE → Tools → Port).');
  } else {
    try {
      port = new SerialPort({ path: SERIAL_PATH, baudRate: SERIAL_BAUD });
      parser = port.pipe(new ReadlineParser({ delimiter: '\n' }));
      parser.on('data', onSerialLine);
      port.on('error', (e) => io.emit('serial:error', { message: e.message }));
      port.on('close', () => io.emit('serial:close', {}));
      io.emit('serial:open', { path: SERIAL_PATH, baud: SERIAL_BAUD });
      console.log(`Payment Trigger Arduino connected on ${SERIAL_PATH}`);
    } catch (e) {
      io.emit('serial:error', { message: e.message });
      console.error('Payment Trigger Arduino connection failed:', e.message);
    }
  }

  // Connect to Transaction Display Arduino
  if (!DISPLAY_SERIAL_PATH) {
    console.warn('No DISPLAY_SERIAL_PATH set. On Windows set env DISPLAY_SERIAL_PATH=COM4 for transaction display.');
  } else {
    try {
      displayPort = new SerialPort({ path: DISPLAY_SERIAL_PATH, baudRate: DISPLAY_SERIAL_BAUD });
      displayParser = displayPort.pipe(new ReadlineParser({ delimiter: '\n' }));
      displayParser.on('data', onDisplaySerialLine);
      displayPort.on('error', (e) => io.emit('display:error', { message: e.message }));
      displayPort.on('close', () => io.emit('display:close', {}));
      io.emit('display:open', { path: DISPLAY_SERIAL_PATH, baud: DISPLAY_SERIAL_BAUD });
      console.log(`Transaction Display Arduino connected on ${DISPLAY_SERIAL_PATH}`);
    } catch (e) {
      io.emit('display:error', { message: e.message });
      console.error('Transaction Display Arduino connection failed:', e.message);
    }
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

function onDisplaySerialLine(lineRaw) {
  const line = lineRaw.trim();
  io.emit('display:line', { line });
  
  // Handle requests from display Arduino
  if (line === 'REQUEST_LATEST_TX') {
    // Send latest transaction to display
    if (state.lastTransaction) {
      sendToDisplay(`TX:${state.lastTransaction}`);
    } else {
      sendToDisplay('STATUS:No transactions');
    }
  }
}

function sendToDisplay(message) {
  if (displayPort && displayPort.writable) {
    displayPort.write(`${message}\n`);
    io.emit('display:sent', { message });
    console.log(`Sent to display: ${message}`);
  }
}

const state = { currentCommand: null, lastTransaction: null };

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
  
  // Store the transaction hash for display purposes
  const tx = data.tx_id || data.txHash || 'ERR';
  state.lastTransaction = tx;
  
  // Send to Payment Trigger Arduino (original behavior)
  if (port && port.writable) {
    port.write(`TX:${tx}\n`);
  }
  
  // Send to Transaction Display Arduino
  if (data.error) {
    sendToDisplay(`ERROR:${data.error.substring(0, 16)}`);
  } else {
    sendToDisplay(`TX:${tx}`);
    sendToDisplay(`STATUS:Transaction sent`);
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

// Convenience for browser testing: GET /simulate
app.get('/simulate', async (_req, res) => {
  try {
    const payload = {
      fromAgent: process.env.AGENT1_ID || 'satoshi-1',
      toAgent: process.env.AGENT2_ID || 'satoshi-2',
      amountAda: Number(process.env.SIM_AMOUNT || 1),
    };
    await triggerPayment(payload);
    res.json({ ok: true, note: 'Triggered payment simulation via GET' });
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
