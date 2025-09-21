# Router and Serial Bridge - Vansh's Tasks

## Project Context
Building the Router and Serial Bridge component for the Arduino-to-Cardano AI Agents system. This component acts as the "traffic controller" ensuring smooth message flow between Arduino A, Agent A, Agent B, and the blockchain service.

## Detailed Implementation Steps

### Phase 1: Setup and Foundation
1. **Setup Router API**
   - Choose between Flask (simpler) or FastAPI (better docs/validation)
   - Initialize project structure with proper dependencies
   - Create main router application file

2. **Define JSON Schemas**
   - Create `schemas/offer.json` - structure for payment offers
   - Create `schemas/response.json` - structure for agent responses
   - Ensure compatibility with Imad and Ishita's implementations

3. **Create In-Memory Store**
   - Implement offer queue using Python dictionaries
   - Add transaction status tracking
   - Include offer ID generation and management

### Phase 2: Core Router Implementation
4. **Implement REST Endpoints**
   - `POST /send_offer` - Receive offers from Agent A
   - `GET /status/{offer_id}` - Check offer status
   - `POST /mock_agent_b` - Mock Agent B responses for testing
   - `GET /offers` - List all active offers (debugging)

5. **Build Message Flow Logic**
   - Forward offers from Agent A to Agent B
   - Handle responses from Agent B
   - Trigger payment service when needed
   - Send transaction hash to Arduino B

6. **Implement Mock Agent B**
   - Create mock responses for testing
   - Simulate realistic response delays
   - Allow configurable response patterns

### Phase 3: Serial Bridge Implementation
7. **Setup Serial Communication**
   - Install and configure pyserial
   - Create serial bridge service
   - Handle Arduino A button press detection

8. **Build Message Translation**
   - Convert Arduino signals to offer JSON
   - Implement proper error handling
   - Add retry logic for failed communications

9. **Integrate Serial Bridge with Router**
   - Connect serial input to router endpoints
   - Ensure proper message queuing
   - Handle concurrent serial and network requests

### Phase 4: Testing and Integration
10. **Unit Testing**
    - Test individual components separately
    - Mock serial input for testing
    - Validate JSON schema compliance

11. **Integration Testing**
    - Test complete flow: Arduino A → Router → Mock Agent B
    - Verify message logging and tracking
    - Test error scenarios and recovery

12. **Team Collaboration**
    - Provide mock endpoints for Imad and Ishita
    - Share JSON schemas and API documentation
    - Create integration test scenarios

### Phase 5: Production Readiness
13. **Add Comprehensive Logging**
    - Log all incoming/outgoing messages
    - Track offer lifecycle and status changes
    - Implement debug and error logging levels

14. **Error Handling and Recovery**
    - Handle network failures gracefully
    - Implement retry mechanisms
    - Add circuit breaker patterns

15. **Performance Optimization**
    - Optimize message processing
    - Implement proper async handling
    - Add monitoring and metrics

## Tech Stack
- **Backend**: Python with Flask/FastAPI
- **Serial Communication**: PySerial
- **Data Format**: JSON with defined schemas
- **Testing**: pytest with mocking
- **Logging**: Python logging module

## Success Criteria
- [ ] Router receives offers from Agent A via REST API
- [ ] Serial Bridge detects Arduino A button presses
- [ ] Messages flow correctly to mock Agent B
- [ ] Transaction hashes are properly tracked and logged
- [ ] Team members can test against mock endpoints
- [ ] All message flows are logged for debugging
- [ ] System handles errors gracefully

## Collaboration Points
- **With Imad**: Ensure offer JSON schema compatibility
- **With Ishita**: Align response JSON schema and mock data
- **With Dhanush**: Prepare for blockchain service integration
- **With Ishita (Frontend)**: Provide status endpoints for UI

## Next Steps
1. Start with Flask setup and basic endpoints
2. Create JSON schemas and share with team
3. Implement mock Agent B to unblock other developers
4. Build serial bridge with Arduino A integration
5. Test complete flow and iterate based on team feedback
