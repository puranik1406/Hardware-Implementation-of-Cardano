# Emotional AI Integration Testing Guide

## Architecture Flow

```
Arduino Button → Arduino Bridge → Emotional AI → Masumi Payment → Cardano → LCD Display
   (COM6)            (Port 5001)     (Port 7002)      (Port 3001)    (Testnet)   (COM3)
```

## Quick Test Commands

### 1. Test Emotional AI Service Directly

```powershell
# Positive emotion (should approve)
Invoke-RestMethod -Uri http://localhost:7002/api/check -Method POST -ContentType "application/json" -Body '{"text":"I am so happy and excited about this amazing transaction!"}'

# Negative emotion (should reject)
Invoke-RestMethod -Uri http://localhost:7002/api/check -Method POST -ContentType "application/json" -Body '{"text":"I am very angry and frustrated about this terrible situation"}'
```

### 2. Test Arduino Bridge with Emotional Context

```powershell
# Set positive emotional context
Invoke-RestMethod -Uri http://localhost:5001/emotion -Method POST -ContentType "application/json" -Body '{"text":"I am so happy and excited!"}'

# Trigger payment simulation (will use emotional context)
Invoke-RestMethod -Uri http://localhost:5001/simulate -Method POST
```

### 3. Test Full Flow with Negative Emotion

```powershell
# Set negative emotional context (should reject)
Invoke-RestMethod -Uri http://localhost:5001/emotion -Method POST -ContentType "application/json" -Body '{"text":"I am very angry and frustrated"}'

# Try to trigger payment (should be rejected)
Invoke-RestMethod -Uri http://localhost:5001/simulate -Method POST
```

## Arduino Serial Protocol

### From Arduino to Bridge (Trigger)
```
TRIGGER_PAYMENT
FROM_AGENT:satoshi_alpha_001
TO_AGENT:satoshi_beta_002
AMOUNT:1
EMOTION:I am so happy and excited about this transaction!
END_COMMAND
```

### From Bridge to Arduino (Response)
```
TX:abc123def456...  (on success)
REJECTED            (on rejection)
STATUS:REJECTED
REASON:Negative...
```

## Expected Results

### Positive Emotion Test
```json
{
  "approved": true,
  "positiveScore": "100.00",
  "negativeScore": "0.00",
  "overallSentiment": "positive",
  "emotions": ["joy"],
  "reason": "Positive emotion (100.00%) exceeds negative (0.00%) - Transaction approved!"
}
```

### Negative Emotion Test
```json
{
  "approved": false,
  "positiveScore": "0.00",
  "negativeScore": "100.00",
  "overallSentiment": "negative",
  "emotions": ["anger", "fear"],
  "reason": "Negative emotion (100.00%) detected - Transaction rejected for safety"
}
```

## Docker Services Status Check

```powershell
# Check all services health
docker-compose ps

# Check emotion-ai logs
docker-compose logs emotion-ai

# Check arduino-bridge logs
docker-compose logs arduino-bridge

# Check masumi-payment logs
docker-compose logs masumi-payment
```

## Troubleshooting

### Emotion AI Not Responding
```powershell
# Check if service is running
curl http://localhost:7002/health

# Restart emotion-ai service
docker-compose restart emotion-ai
```

### Arduino Bridge Not Connected
- Check `SERIAL_PATH=COM6` and `DISPLAY_SERIAL_PATH=COM3` in `.env`
- Verify Arduino IDE shows correct COM ports
- Check if other programs are using the serial ports

### Payment Not Triggering
- Ensure Masumi service is running on port 3001
- Verify Cardano preprod testnet wallet has funds
- Check `AGENT1_SKEY_CBOR` is set correctly in `.env`

## Hardware Setup

1. **Arduino Uno #1 (COM6 - Trigger)**
   - Button on pin 2
   - Green LED on pin 8 (transaction success)
   - Red LED on pin 9 (transaction rejected)

2. **Arduino Uno #2 (COM3 - Display)**
   - 16x2 LCD display
   - Shows transaction hash after success
   - Shows rejection reason on failure

## Real-Time Monitoring

Open web dashboard:
```powershell
# Start frontend
cd frontend/web-dashboard
npm start
```

Then open: http://localhost:8080

You'll see:
- Real-time emotional analysis scores
- Transaction approval/rejection decisions
- Cardano transaction hashes
- Arduino serial communication logs
