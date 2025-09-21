# Agent A (Buyer Logic) - Arduino-to-Cardano AI Agents

## Overview
Agent A is responsible for making and evaluating payment offers in the Arduino-to-Cardano AI Agents system. It uses AWS Bedrock for intelligent decision-making with rule-based fallback logic.

## Features
- **Offer Creation**: Creates payment offers based on Arduino triggers
- **Decision Making**: Evaluates counter-offers using AI or fallback logic
- **AWS Bedrock Integration**: Uses Claude 3 Sonnet for intelligent decisions
- **Fallback Logic**: Rule-based decisions when Bedrock is unavailable
- **Mock Mode**: Testing without AWS Bedrock access
- **Comprehensive Logging**: Tracks all decisions and reasoning

## Quick Start

### 1. Install Dependencies
```bash
cd agents
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# For mock mode (default)
export USE_MOCK_BEDROCK=true

# For real Bedrock (requires AWS credentials)
export USE_MOCK_BEDROCK=false
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

### 3. Run the Service
```bash
python agent_a/main.py
```

The service will start on `http://localhost:8001`

### 4. Test the Service
```bash
python test_agent_a.py
```

## API Endpoints

### Health Check
```bash
GET /
```

### Create Offer
```bash
POST /agentA/propose
Content-Type: application/json

{
  "trigger_type": "arduino",
  "amount": 1000000,
  "context": {"test": true},
  "timestamp": "2024-01-01T00:00:00Z",
  "source": "arduino_a"
}
```

### Evaluate Counter Offer
```bash
POST /agentA/decide
Content-Type: application/json

{
  "offer_id": "uuid-here",
  "counter_offer": {"amount": 1500000},
  "context": {"test": true},
  "agent_b_response": {"status": "counter_offer"}
}
```

## Configuration

### Environment Variables
- `USE_MOCK_BEDROCK`: Use mock mode (default: true)
- `BEDROCK_MODEL_ID`: Bedrock model ID (default: claude-3-sonnet)
- `FALLBACK_THRESHOLD`: Minimum amount for fallback logic (default: 1000000)
- `MIN_OFFER_AMOUNT`: Minimum valid offer amount (default: 100000)
- `MAX_OFFER_AMOUNT`: Maximum valid offer amount (default: 10000000)
- `LOG_LEVEL`: Logging level (default: INFO)

### AWS Bedrock Setup
1. Configure AWS credentials
2. Ensure Bedrock access in your AWS account
3. Set `USE_MOCK_BEDROCK=false`

## Architecture

### Decision Flow
1. **Trigger Received**: Arduino or manual trigger
2. **AI Decision**: Bedrock evaluates the trigger
3. **Fallback Check**: If Bedrock fails, use rule-based logic
4. **Response**: Return structured offer/decision

### Integration Points
- **Router Service**: Receives offers and decisions
- **Arduino Hardware**: Triggers and responses
- **Blockchain Service**: Transaction execution
- **Agent B**: Counter-offer evaluation

## Testing

### Manual Testing
```bash
# Test offer creation
curl -X POST http://localhost:8001/agentA/propose \
  -H "Content-Type: application/json" \
  -d '{"trigger_type": "arduino", "amount": 1000000}'

# Test decision evaluation
curl -X POST http://localhost:8001/agentA/decide \
  -H "Content-Type: application/json" \
  -d '{"offer_id": "test-123", "counter_offer": {"amount": 1500000}}'
```

### Automated Testing
```bash
python test_agent_a.py
```

## Logging

The service logs:
- Input prompts to Bedrock
- Raw LLM responses
- Parsed JSON decisions
- Fallback logic triggers
- API request/response details

## Schema Coordination

### Offer Schema (with Vansh)
```json
{
  "offer_id": "uuid",
  "agent_id": "agent_a",
  "amount": 1000000,
  "status": "accepted",
  "decision_reason": "AI decision",
  "timestamp": "2024-01-01T00:00:00Z",
  "transaction_hash": null
}
```

### Decision Schema
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

## Troubleshooting

### Common Issues
1. **Bedrock Connection Failed**: Check AWS credentials and region
2. **JSON Parse Error**: Bedrock returned invalid JSON (check logs)
3. **Validation Error**: Input data doesn't match schema
4. **Port Already in Use**: Change PORT environment variable

### Debug Mode
```bash
export LOG_LEVEL=DEBUG
python agent_a/main.py
```

## Next Steps
1. Coordinate with Vansh on Router integration
2. Test with real Arduino triggers
3. Integrate with blockchain service
4. Deploy to production environment

