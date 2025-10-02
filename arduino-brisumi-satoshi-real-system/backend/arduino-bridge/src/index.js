import 'dotenv/config';
import express from 'express';
import cors from 'cors';
import { SerialPort } from 'serialport';
import { ReadlineParser } from '@serialport/parser-readline';
import { fetch } from 'undici';
import { createServer } from 'http';
import { Server as SocketIOServer } from 'socket.io';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// File logging to bypass terminal buffering
const logFilePath = path.join(__dirname, '..', 'debug.log');
// Clear previous log
fs.writeFileSync(logFilePath, `=== Arduino Bridge Debug Log (${new Date().toISOString()}) ===\n`);

function fileLog(message) {
  const timestamp = new Date().toISOString();
  const logMessage = `[${timestamp}] ${message}\n`;
  fs.appendFileSync(logFilePath, logMessage);
  console.log(message);
}

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
const EMOTION_AI_URL = process.env.EMOTION_AI_URL || 'http://localhost:7002';
const DEMO_MODE = process.env.DEMO_MODE === 'true'; // If true, skip real transactions and use mock hash

let port; let parser;
let displayPort; let displayParser;

async function connectSerial() {
  fileLog('=== Starting Serial Port Connections ===');
  
  // Connect to Payment Trigger Arduino
  if (!SERIAL_PATH) {
    fileLog('No SERIAL_PATH set. On Windows set env SERIAL_PATH=COM3 (check Arduino IDE → Tools → Port).');
  } else {
    try {
      port = new SerialPort({ path: SERIAL_PATH, baudRate: SERIAL_BAUD });
      parser = port.pipe(new ReadlineParser({ delimiter: '\n' }));
      parser.on('data', onSerialLine);
      port.on('error', (e) => {
        fileLog(`[COM6] Error: ${e.message}`);
        io.emit('serial:error', { message: e.message });
      });
      port.on('close', () => {
        fileLog('[COM6] Port closed');
        io.emit('serial:close', {});
      });
      io.emit('serial:open', { path: SERIAL_PATH, baud: SERIAL_BAUD });
      fileLog(`✓ Payment Trigger Arduino connected on ${SERIAL_PATH}`);
    } catch (e) {
      io.emit('serial:error', { message: e.message });
      fileLog(`✗ Payment Trigger Arduino connection failed: ${e.message}`);
    }
  }

  // Connect to Transaction Display Arduino
  if (!DISPLAY_SERIAL_PATH) {
    fileLog('No DISPLAY_SERIAL_PATH set. On Windows set env DISPLAY_SERIAL_PATH=COM4 for transaction display.');
  } else {
    try {
      displayPort = new SerialPort({ path: DISPLAY_SERIAL_PATH, baudRate: DISPLAY_SERIAL_BAUD });
      displayParser = displayPort.pipe(new ReadlineParser({ delimiter: '\n' }));
      displayParser.on('data', onDisplaySerialLine);
      
      // Wait for port to fully open
      displayPort.on('open', () => {
        fileLog(`✓ Transaction Display Arduino FULLY OPEN on ${DISPLAY_SERIAL_PATH}`);
        fileLog(`[COM3] Port ready: isOpen=${displayPort.isOpen}, writable=${displayPort.writable}`);
        io.emit('display:open', { path: DISPLAY_SERIAL_PATH, baud: DISPLAY_SERIAL_BAUD });
        // Send initial test message to verify LCD is working
        setTimeout(() => {
          sendToDisplay('STATUS:LCD Ready');
        }, 1000);
      });
      
      displayPort.on('error', (e) => {
        fileLog(`[COM3] Error: ${e.message}`);
        io.emit('display:error', { message: e.message });
      });
      displayPort.on('close', () => {
        fileLog('[COM3] Port closed');
        io.emit('display:close', {});
      });
      
      fileLog(`⏳ Opening Transaction Display Arduino on ${DISPLAY_SERIAL_PATH}...`);
    } catch (e) {
      io.emit('display:error', { message: e.message });
      fileLog(`✗ Transaction Display Arduino connection failed: ${e.message}`);
    }
  }
  
  fileLog('=== Serial Port Connection Complete ===');
}

function onSerialLine(lineRaw) {
  const line = lineRaw.trim();
  io.emit('serial:line', { line });
  
  // NEW: Plant health data parsing
  if (line === 'PLANT_HEALTH_DATA') {
    state.inPlantDataMode = true;
    state.plantData = { timestamp: new Date().toISOString() };
    fileLog('[PLANT] Receiving plant health data...');
    return;
  } else if (state.inPlantDataMode) {
    if (line === 'END_PLANT_DATA') {
      state.inPlantDataMode = false;
      fileLog(`[PLANT] Data complete: ${JSON.stringify(state.plantData)}`);
      handlePlantHealthData(state.plantData).catch(err => 
        fileLog(`[PLANT] Error processing: ${err.message}`)
      );
      return;
    } else if (line.startsWith('PLANT_TYPE:')) {
      state.plantData.plantType = line.replace('PLANT_TYPE:', '').trim();
    } else if (line.startsWith('MOISTURE_RAW:')) {
      state.plantData.moistureRaw = parseInt(line.replace('MOISTURE_RAW:', '').trim());
    } else if (line.startsWith('MOISTURE_PERCENT:')) {
      state.plantData.moisturePercent = parseInt(line.replace('MOISTURE_PERCENT:', '').trim());
    } else if (line.startsWith('MOISTURE_THRESHOLD:')) {
      state.plantData.moistureThreshold = line.replace('MOISTURE_THRESHOLD:', '').trim();
    } else if (line.startsWith('TEMPERATURE:')) {
      state.plantData.temperature = parseFloat(line.replace('TEMPERATURE:', '').trim());
    } else if (line.startsWith('HUMIDITY:')) {
      state.plantData.humidity = parseInt(line.replace('HUMIDITY:', '').trim());
    } else if (line.startsWith('PLANT_STATUS:')) {
      // Sent with payment trigger
      const status = line.replace('PLANT_STATUS:', '').trim();
      fileLog(`[PLANT] Status with payment: ${status}`);
    }
    return;
  }
  
  // EXISTING: Payment trigger parsing (UNCHANGED)
  if (line === 'TRIGGER_PAYMENT') {
    state.currentCommand = { from: null, to: null, amount: null };
    state.emotionalContext = ''; // Reset emotional context
  } else if (line.startsWith('FROM_AGENT:')) {
    state.currentCommand.from = line.replace('FROM_AGENT:', '').trim();
  } else if (line.startsWith('TO_AGENT:')) {
    state.currentCommand.to = line.replace('TO_AGENT:', '').trim();
  } else if (line.startsWith('AMOUNT:')) {
    state.currentCommand.amount = Number(line.replace('AMOUNT:', '').trim());
  } else if (line.startsWith('EMOTION:')) {
    // Capture emotional context from Arduino
    state.emotionalContext = line.replace('EMOTION:', '').trim();
    console.log(`Received emotional context: "${state.emotionalContext}"`);
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
  fileLog(`[DISPLAY] === SEND TO DISPLAY CALLED ===`);
  fileLog(`[DISPLAY] Message: "${message}"`);
  fileLog(`[DISPLAY] displayPort exists: ${!!displayPort}`);
  fileLog(`[DISPLAY] displayPort isOpen: ${displayPort?.isOpen}`);
  fileLog(`[DISPLAY] displayPort writable: ${displayPort?.writable}`);
  fileLog(`[DISPLAY] displayPort path: ${displayPort?.path}`);
  
  // CRITICAL FIX: Check isOpen AND writable
  if (displayPort && displayPort.isOpen && displayPort.writable) {
    const fullMessage = `${message}\n`;
    fileLog(`[DISPLAY] ✓ Port is OPEN and WRITABLE - sending data...`);
    fileLog(`[DISPLAY] Writing to port: "${fullMessage.trim()}"`);
    
    displayPort.write(fullMessage, (err) => {
      if (err) {
        fileLog(`[DISPLAY] ❌ Write error: ${err.message}`);
      } else {
        fileLog(`[DISPLAY] ✓ Write successful!`);
      }
    });
    
    // Force drain to ensure data is sent
    displayPort.drain((err) => {
      if (err) {
        fileLog(`[DISPLAY] ❌ Drain error: ${err.message}`);
      } else {
        fileLog(`[DISPLAY] ✓ Data drained to serial port`);
      }
    });
    
    io.emit('display:sent', { message });
  } else {
    fileLog(`[DISPLAY] ✗ Cannot send - port not fully ready (must be OPEN and WRITABLE)`);
    fileLog(`[DISPLAY] Port state: ${JSON.stringify({
      exists: !!displayPort,
      isOpen: displayPort?.isOpen,
      writable: displayPort?.writable,
      path: displayPort?.path
    })}`);
  }
}

const state = { 
  currentCommand: null, 
  lastTransaction: null, 
  emotionalContext: '',
  plantData: null,           // NEW: Store plant health data
  inPlantDataMode: false     // NEW: Flag for parsing plant data
};

async function checkEmotionalApproval(text) {
  try {
    const res = await fetch(`${EMOTION_AI_URL}/api/check`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await res.json();
    
    if (!res.ok) {
      throw new Error(data?.error || `Emotion AI returned ${res.status}`);
    }
    
    io.emit('emotion:analysis', data);
    console.log('Emotional Analysis:', data);
    
    return {
      approved: data.approved,
      reason: data.reason || 'Unknown',
      positiveScore: data.positiveScore,
      negativeScore: data.negativeScore
    };
  } catch (err) {
    console.error('Emotion AI check failed:', err.message);
    io.emit('emotion:error', { error: err.message });
    // Default to rejection on error for safety
    return {
      approved: false,
      reason: `Emotion AI unavailable: ${err.message}`,
      positiveScore: 0,
      negativeScore: 0
    };
  }
}

async function triggerPayment(cmd) {
  io.emit('payment:trigger', cmd);
  
  // Step 1: Get emotional context (from Arduino or default)
  const emotionalText = state.emotionalContext || 
    `Payment request from ${cmd.from} to ${cmd.to} for ${cmd.amount} ADA`;
  
  console.log(`Checking emotional approval for: "${emotionalText}"`);
  
  // Step 2: Check with Emotional AI
  const emotionResult = await checkEmotionalApproval(emotionalText);
  
  if (!emotionResult.approved) {
    const rejectMessage = `REJECTED: ${emotionResult.reason}`;
    console.log(rejectMessage);
    io.emit('payment:rejected', { 
      reason: emotionResult.reason,
      positiveScore: emotionResult.positiveScore,
      negativeScore: emotionResult.negativeScore
    });
    
    // Send rejection to displays
    if (port && port.writable) {
      port.write(`REJECTED\n`);
    }
    sendToDisplay(`STATUS:REJECTED`);
    sendToDisplay(`REASON:${emotionResult.reason.substring(0, 16)}`);
    
    return; // Stop here, do not proceed to payment
  }
  
  console.log(`Transaction APPROVED by Emotional AI (Positive: ${emotionResult.positiveScore}%, Negative: ${emotionResult.negativeScore}%)`);
  io.emit('payment:approved', emotionResult);
  
  // Step 3: Process payment (real or demo mode)
  let data;
  
  if (DEMO_MODE) {
    // DEMO MODE: Generate mock transaction hash for hardware testing
    const mockTxHash = '0x' + Array.from({length: 64}, () => Math.floor(Math.random() * 16).toString(16)).join('');
    console.log(`[DEMO MODE] Simulating successful transaction: ${mockTxHash}`);
    data = { 
      tx_id: mockTxHash,
      txHash: mockTxHash,
      status: 'demo_success',
      message: 'Demo mode - no real blockchain transaction'
    };
    io.emit('payment:response', data);
  } else {
    // REAL MODE: Forward to Masumi Payment Service
    const url = process.env.MASUMI_PAYMENT_URL || 'http://localhost:3001/api/cardano/transfer';
    const body = { fromAgent: cmd.from, toAgent: cmd.to, amountAda: cmd.amount };
    if (process.env.AGENT1_SKEY_CBOR) {
      body.skeyCbor = process.env.AGENT1_SKEY_CBOR.trim();
    }
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
  }
  
  // Step 4: Store the transaction hash for display purposes
  const tx = data.tx_id || data.txHash || 'ERR';
  state.lastTransaction = tx;
  fileLog(`[TRANSACTION] ==========================================`);
  fileLog(`[TRANSACTION] Received TX Hash: ${tx}`);
  fileLog(`[TRANSACTION] Data received: ${JSON.stringify(data, null, 2)}`);
  fileLog(`[TRANSACTION] ==========================================`);
  
  // Step 5: Send to Payment Trigger Arduino (original behavior)
  if (port && port.writable) {
    port.write(`TX:${tx}\n`);
    fileLog(`[TRIGGER] ✓ Sent TX to COM6: ${tx}`);
  } else {
    fileLog(`[TRIGGER] ✗ Cannot send to COM6 - port not writable`);
  }
  
  // Step 6: Send to Transaction Display Arduino
  fileLog(`[DISPLAY] ========== PREPARING TO SEND TO LCD ==========`);
  if (data.error) {
    fileLog(`[DISPLAY] Transaction has error: ${data.error}`);
    sendToDisplay(`ERROR:${data.error.substring(0, 16)}`);
  } else {
    fileLog(`[DISPLAY] Transaction successful, sending hash...`);
    sendToDisplay(`TX:${tx}`);
    fileLog(`[DISPLAY] Sent TX command, now sending STATUS...`);
    sendToDisplay(`STATUS:Transaction sent`);
    fileLog(`[DISPLAY] ========== COMPLETED DISPLAY SENDS ==========`);
  }
}

// NEW: Plant Health Data Handler
async function handlePlantHealthData(plantData) {
  fileLog(`[PLANT] Processing health data for ${plantData.plantType}`);
  
  // Create report directory if it doesn't exist
  const reportsDir = path.join(__dirname, '../../..', 'plant_reports');
  if (!fs.existsSync(reportsDir)) {
    fs.mkdirSync(reportsDir, { recursive: true });
  }
  
  // Generate report
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T');
  const dateStr = timestamp[0].replace(/-/g, '');
  const timeStr = timestamp[1].split('-')[0].replace(/-/g, '');
  const filename = `aloe_vera_report_${dateStr}_${timeStr}.txt`;
  const filepath = path.join(reportsDir, filename);
  
  let report = '=' + '='.repeat(69) + '\n';
  report += '🌱 ALOE VERA PLANT HEALTH REPORT\n';
  report += '=' + '='.repeat(69) + '\n\n';
  report += `Report Generated: ${new Date().toLocaleString()}\n`;
  report += `Plant Type: ${plantData.plantType}\n`;
  report += `Arduino Port: COM6\n\n`;
  report += '-'.repeat(70) + '\n';
  report += '📊 SENSOR READINGS\n';
  report += '-'.repeat(70) + '\n\n';
  
  // Moisture Analysis
  const moisture = plantData.moisturePercent;
  report += `💧 Soil Moisture: ${moisture}%\n`;
  if (moisture >= 60 && moisture <= 70) {
    report += '   Status: ✓ OPTIMAL - Perfect for Aloe Vera\n';
  } else if (moisture < 50) {
    report += '   Status: ⚠ DRY - Water needed!\n';
  } else if (moisture > 70) {
    report += '   Status: ⚠ WET - Risk of overwatering\n';
  } else {
    report += '   Status: OK\n';
  }
  report += `   Raw ADC Reading: ${plantData.moistureRaw}/1023\n`;
  report += `   Digital Threshold: ${plantData.moistureThreshold}\n\n`;
  
  // Temperature
  report += `🌡️ Temperature: ${plantData.temperature}°C\n`;
  if (plantData.temperature >= 18 && plantData.temperature <= 27) {
    report += '   Status: ✓ IDEAL RANGE\n\n';
  } else {
    report += '   Status: ⚠ OUT OF RANGE\n\n';
  }
  
  // Humidity
  report += `💨 Humidity: ${plantData.humidity}%\n`;
  if (plantData.humidity >= 40 && plantData.humidity <= 60) {
    report += '   Status: ✓ GOOD\n\n';
  } else {
    report += '   Status: ⚠ MONITOR\n\n';
  }
  
  report += '-'.repeat(70) + '\n';
  report += '💡 RECOMMENDATIONS\n';
  report += '-'.repeat(70) + '\n';
  if (moisture < 60) {
    report += '• Water the plant - soil is getting dry\n';
  } else if (moisture > 70) {
    report += '• Reduce watering - soil is too wet\n';
  } else {
    report += '• Continue current watering schedule\n';
  }
  
  report += '\n' + '='.repeat(70) + '\n';
  report += 'End of Report\n';
  report += '='.repeat(70) + '\n';
  
  fs.writeFileSync(filepath, report);
  fileLog(`[PLANT] ✓ Report saved: ${filepath}`);
  
  // Emit event
  io.emit('plant:report', { plantData, filepath: filename });
  
  return { success: true, filepath: filename };
}

app.get('/health', (_req, res) => res.json({ ok: true }));

// Set emotional context for testing
app.post('/emotion', (req, res) => {
  state.emotionalContext = req.body?.text || '';
  console.log(`Emotional context set to: "${state.emotionalContext}"`);
  res.json({ ok: true, emotionalContext: state.emotionalContext });
});

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

// NEW: Plant Health Monitoring Endpoint
app.get('/plant-status', (_req, res) => {
  res.json({ 
    ok: true, 
    lastPlantData: state.plantData,
    message: 'Send REQUEST_PLANT_DATA via serial to Arduino to refresh' 
  });
});

app.post('/request-plant-data', (_req, res) => {
  if (port && port.isOpen && port.writable) {
    port.write('REQUEST_PLANT_DATA\n');
    fileLog('[PLANT] Requested data from Arduino');
    res.json({ ok: true, message: 'Plant data requested from Arduino' });
  } else {
    res.status(503).json({ error: 'Arduino not connected' });
  }
});

io.on('connection', (socket) => {
  socket.emit('hello', { ts: Date.now() });
});

httpServer.listen(PORT, () => {
  console.log(`Arduino Bridge on :${PORT}`);
  connectSerial();
});
