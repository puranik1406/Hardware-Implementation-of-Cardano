# Agent B (Seller Logic) & Arduino B (Transaction Display) - Tasks

## Overview
Ishita is responsible for Agent B (Seller Logic) and Arduino B (transaction display). The goal is to listen for offers, decide whether to accept, and display the transaction hash when payment is confirmed.

## Task Breakdown

### 1. Setup Agent B API
- [ ] Create Python Flask/FastAPI application
- [ ] Implement `/respond` endpoint to receive offers from Router
- [ ] Implement `/confirm_tx` endpoint to handle transaction confirmations
- [ ] Add proper JSON request/response handling
- [ ] Add error handling and logging

### 2. Implement Decision Logic
- [ ] Create rule-based decision engine
- [ ] Implement accept logic: accept if amount > cost
- [ ] Add reject logic for insufficient offers
- [ ] Add counter-offer logic (optional enhancement)
- [ ] Make decision logic configurable

### 3. Integrate with Payments API
- [ ] Implement `/send_payment` call to Blockchain Service
- [ ] Add polling mechanism for `/tx_status` endpoint
- [ ] Handle payment confirmation workflow
- [ ] Add timeout handling for payment confirmation
- [ ] Implement retry logic for failed payments

### 4. Build Arduino B Sketch
- [ ] Create Arduino sketch for Wokwi simulation
- [ ] Implement Serial communication listener
- [ ] Add LCD display functionality
- [ ] Display transaction hash in format: "✅ CONFIRMED: [tx_hash]"
- [ ] Add Serial Monitor output as backup
- [ ] Test with mock data

### 5. Testing & Integration
- [ ] Test Agent B API endpoints independently
- [ ] Test with mock payment responses
- [ ] Test Arduino B with dummy transaction hashes
- [ ] Test complete workflow: offer → accept → payment → display
- [ ] Add unit tests for decision logic
- [ ] Add integration tests for API endpoints

### 6. Documentation & Deployment
- [ ] Document API endpoints and request/response formats
- [ ] Create setup instructions for Arduino B
- [ ] Add configuration options for decision logic
- [ ] Prepare for integration with Router and Blockchain Service

## Technical Stack
- **Backend**: Python (Flask/FastAPI)
- **Communication**: JSON over HTTP
- **Hardware**: Arduino (Wokwi simulation)
- **Display**: LCD + Serial Monitor

## Success Criteria
- Agent B reliably accepts offers based on decision logic
- Payment confirmation triggers Arduino B display
- Transaction hash is clearly displayed on Arduino B
- Complete workflow works with mock data
- Ready for integration with real blockchain services

## Dependencies
- Router service for receiving offers
- Blockchain Service for payment processing
- Arduino B for transaction display
- Mock payment service for testing
