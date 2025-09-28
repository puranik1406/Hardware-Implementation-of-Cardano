/**
 * Arduino Agents registry and simple policy layer
 */

export const agents = [
  {
    id: 'agent_a_001',
    name: 'Arduino A (Sender)',
    role: 'sender',
    walletAddress: 'addr1q9...',
    policy: {
      // Simple policy: auto-send tiny payment if balance > threshold
      autoSendEnabled: false,
      minBalance: 50,
      amount: 5,
      intervalMs: 60000,
    }
  },
  {
    id: 'agent_b_001',
    name: 'Arduino B (Receiver)',
    role: 'receiver',
    walletAddress: 'addr1q8...',
    policy: {
      autoAcknowledge: true
    }
  }
]
