# Cookbook: Basic Agentic Payment

This example demonstrates how to trigger a payment between two Arduino agents using the Masumi service.

## Steps

1. Initialize service
2. Register agents (if not already registered)
3. Send a payment
4. Listen for payment events

```js
import { masumiService } from '../src/services/MasumiNetworkService'

async function run() {
  await masumiService.initialize()

  await masumiService.registerAgent({
    agentId: 'agent_a_001',
    walletAddress: 'addr1q...',
  })
  await masumiService.registerAgent({
    agentId: 'agent_b_001',
    walletAddress: 'addr1q...',
  })

  const result = await masumiService.sendPayment({
    fromAgentId: 'agent_a_001',
    toAgentId: 'agent_b_001',
    amount: 25
  })

  console.log('Payment result:', result)
}

run()
```
