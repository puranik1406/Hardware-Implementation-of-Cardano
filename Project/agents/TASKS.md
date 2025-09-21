# Agent A (Buyer Logic) - Implementation Tasks

## Project Context
**Arduino-to-Cardano AI Agents with Masumi Payments**
- Building a prototype system where AI agents communicate and perform payment transactions
- Agent A (Buyer Logic) decides whether to make, accept, or reject offers
- Uses AWS Bedrock for LLM decision-making with rule-based fallback
- Integrates with Arduino triggers and blockchain payment service

## Implementation Steps

### Phase 1: Setup & Foundation
- [x] Create project structure with agents folder
- [ ] Set up Python environment with Flask/FastAPI
- [ ] Install AWS Bedrock SDK and dependencies
- [ ] Create basic project structure for Agent A

### Phase 2: Core Service Development
- [ ] Build Agent A service with Flask/FastAPI
- [ ] Create offer.json schema (coordinate with Vansh)
- [ ] Implement structured prompt templates for Bedrock
- [ ] Add JSON schema validation for inputs/outputs

### Phase 3: API Endpoints
- [ ] Create `POST /agentA/propose` endpoint
  - Takes trigger input
  - Generates offer JSON using Bedrock
  - Returns structured offer response
- [ ] Create `POST /agentA/decide` endpoint
  - Evaluates counter-offers
  - Returns accept/reject decision
  - Includes transaction details

### Phase 4: AWS Bedrock Integration
- [ ] Set up AWS Bedrock client configuration
- [ ] Create prompt templates for different scenarios
- [ ] Implement JSON parsing and validation
- [ ] Add error handling for Bedrock failures

### Phase 5: Fallback Logic
- [ ] Implement rule-based decision logic
- [ ] Add threshold-based acceptance rules
- [ ] Create fallback when Bedrock is unavailable
- [ ] Add comprehensive logging

### Phase 6: Testing & Integration
- [ ] Create mock Bedrock endpoint for testing
- [ ] Test API endpoints with Postman/curl
- [ ] Validate JSON schema compliance
- [ ] Test fallback scenarios
- [ ] Coordinate with Vansh on offer schema

### Phase 7: Documentation & Deployment
- [ ] Add comprehensive logging (input prompt, raw LLM output, parsed JSON)
- [ ] Create API documentation
- [ ] Set up environment configuration
- [ ] Prepare for integration with Router service

## Success Criteria
- Agent A generates valid offers that flow into Router
- Decisions are made consistently using Bedrock or fallback
- API endpoints are tested and documented
- Schema alignment with Vansh's Router service
- Comprehensive logging for debugging

## Dependencies
- AWS Bedrock access and configuration
- Coordination with Vansh on offer.json schema
- Integration with Router service (Vansh)
- Arduino trigger system (hardware team)

