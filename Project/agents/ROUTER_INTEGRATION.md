# 🔗 Agent A Router Integration Guide

## Overview
Agent A now integrates with Vansh's Router service to send payment offers in the correct format.

## Router Service Details
- **URL**: http://localhost:5000
- **Endpoint**: POST /send_offer
- **Format**: JSON with specific schema

## Integration Flow

### 1. Agent A receives trigger
```json
{
  "trigger_type": "arduino",
  "amount": 2500000,  // lovelace
  "context": {
    "button_type": "button_1",
    "priority": "high"
  },
  "source": "arduino_a"
}
```

### 2. Agent A converts and sends to Router
```json
{
  "from_agent": "agent_a",
  "to_agent": "agent_b",
  "amount": 2.5,  // ADA
  "currency": "ADA",
  "description": "Agent A payment offer",
  "timestamp": "2024-01-15T10:30:00Z",
  "metadata": {
    "arduino_trigger": true,
    "button_type": "button_1",
    "priority": "medium",
    "agent_a_offer_id": "uuid"
  }
}
```

## New Agent A Endpoints

### 1. Send to Router
```
POST /agentA/send_to_router
```
Converts lovelace to ADA and sends to Router service.

### 2. Router Status
```
GET /agentA/router_status
```
Checks Router service connectivity.

## Testing the Integration

### Step 1: Start Agent A
```bash
cd agents
python start_with_aws.py
```

### Step 2: Test Router Integration
```bash
python test_router_integration.py
```

### Step 3: Manual Test
```bash
# Test Agent A health
curl http://localhost:8001/

# Test Router status
curl http://localhost:8001/agentA/router_status

# Send offer to Router
curl -X POST http://localhost:8001/agentA/send_to_router \
  -H "Content-Type: application/json" \
  -d '{
    "trigger_type": "arduino",
    "amount": 2500000,
    "context": {"button_type": "button_1", "priority": "high"},
    "source": "arduino_a"
  }'
```

## Schema Mapping

| Agent A Field | Router Field | Conversion |
|---------------|--------------|------------|
| trigger.amount (lovelace) | amount (ADA) | ÷ 1,000,000 |
| trigger.trigger_type | metadata.arduino_trigger | boolean |
| trigger.context.button_type | metadata.button_type | direct |
| trigger.context.priority | metadata.priority | direct |
| trigger.source | metadata.source | direct |

## Error Handling

- **Router offline**: Agent A logs error, continues with fallback
- **Invalid response**: Agent A retries with exponential backoff
- **Network timeout**: Agent A uses cached responses if available

## Next Steps

1. **Test with Vansh**: Ensure Router service is running
2. **Coordinate testing**: Run integration tests together
3. **Production setup**: Configure production URLs
4. **Monitor integration**: Set up logging and monitoring
