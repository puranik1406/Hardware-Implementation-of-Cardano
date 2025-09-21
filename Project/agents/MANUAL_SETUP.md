# 🔧 Manual Setup Guide for Agent A

## Quick Start (Easiest Method)

### Option 1: Run the Batch File
```cmd
# Double-click this file or run in command prompt:
setup_manual.bat
```

### Option 2: PowerShell Commands (Copy & Paste)

```powershell
# 1. Navigate to agents directory
cd C:\Users\H.P\project\agents

# 2. Set environment variables
$env:AWS_ACCESS_KEY_ID = "YOUR_AWS_ACCESS_KEY_ID"
$env:AWS_SECRET_ACCESS_KEY = "YOUR_AWS_SECRET_ACCESS_KEY"
$env:AWS_REGION = "us-east-1"
$env:USE_MOCK_BEDROCK = "true"
$env:BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
$env:LOG_LEVEL = "INFO"
$env:HOST = "0.0.0.0"
$env:PORT = "8001"

# 3. Install dependencies
pip install fastapi uvicorn boto3 pydantic requests python-multipart python-json-logger

# 4. Test imports
python -c "import fastapi, uvicorn, boto3; print('All packages imported successfully')"

# 5. Start the service
python start_with_aws.py
```

## Step-by-Step Manual Setup

### Step 1: Open PowerShell
- Press `Win + R`
- Type `powershell`
- Press Enter

### Step 2: Navigate to Project
```powershell
cd C:\Users\H.P\project\agents
```

### Step 3: Set Environment Variables
Copy and paste these commands one by one:

```powershell
$env:AWS_ACCESS_KEY_ID = "YOUR_AWS_ACCESS_KEY_ID"
$env:AWS_SECRET_ACCESS_KEY = "YOUR_AWS_SECRET_ACCESS_KEY"
$env:AWS_REGION = "us-east-1"
$env:USE_MOCK_BEDROCK = "true"
$env:BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"
$env:LOG_LEVEL = "INFO"
$env:HOST = "0.0.0.0"
$env:PORT = "8001"
```

### Step 4: Install Dependencies
```powershell
pip install fastapi uvicorn boto3 pydantic requests python-multipart python-json-logger
```

### Step 5: Verify Installation
```powershell
python -c "import fastapi, uvicorn, boto3; print('All packages imported successfully')"
```

### Step 6: Start Agent A Service
```powershell
python start_with_aws.py
```

## Testing the Service

### Test 1: Health Check
Open a new PowerShell window and run:
```powershell
cd C:\Users\H.P\project\agents
Invoke-WebRequest -Uri "http://localhost:8001/" -Method GET
```

### Test 2: Create Offer
```powershell
$body = @{
    trigger_type = "arduino"
    amount = 1000000
    source = "arduino_a"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8001/agentA/propose" -Method POST -Body $body -ContentType "application/json"
```

### Test 3: Evaluate Decision
```powershell
$decisionBody = @{
    offer_id = "test-123"
    counter_offer = @{
        amount = 1500000
    }
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8001/agentA/decide" -Method POST -Body $decisionBody -ContentType "application/json"
```

### Test 4: Run Automated Tests
```powershell
python test_agent_a.py
```

## Expected Results

### ✅ Successful Setup Should Show:
1. **Environment variables set** correctly
2. **All packages imported** successfully
3. **Service starts** on http://localhost:8001
4. **Health check** returns status 200
5. **API endpoints** respond correctly
6. **Automated tests** pass

### 🔍 Service Information:
- **Main Service**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/
- **Propose Offer**: POST http://localhost:8001/agentA/propose
- **Decide Offer**: POST http://localhost:8001/agentA/decide

## Troubleshooting

### Issue 1: Python not found
**Solution**: Make sure Python is installed and added to PATH

### Issue 2: Package installation fails
**Solution**: Run `pip install --upgrade pip` first

### Issue 3: Service won't start
**Solution**: Check if port 8001 is already in use

### Issue 4: API tests fail
**Solution**: Make sure the service is running before testing

## Next Steps After Setup

1. **Test the service** with the provided commands
2. **Share API documentation** with Vansh for Router integration
3. **Coordinate schema** alignment with Router service
4. **Plan integration testing** session
5. **Deploy to production** when ready

## API Schema for Router Integration

### Offer Schema:
```json
{
  "offer_id": "uuid",
  "agent_id": "agent_a",
  "amount": 1000000,
  "status": "accepted",
  "decision_reason": "AI decision",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Decision Schema:
```json
{
  "offer_id": "uuid",
  "agent_id": "agent_a",
  "status": "accepted",
  "amount": 1000000,
  "decision_reason": "Counter offer accepted",
  "timestamp": "2024-01-01T00:00:00Z"
}
```
