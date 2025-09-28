// Test real Masumi integration with Arduino agents
import axios from 'axios'

const PAYMENT_API = 'http://localhost:3001/api/v1'
const REGISTRY_API = 'http://localhost:3000/api/v1'
const ADMIN_KEY = '8d6b3c5f8fca31d4a72f5e8897a1c9c9b4a7d8f03e1f82a35a3f9f7b6a6d2a1c'

async function registerAgent(name, description = 'Arduino agent for agentic payments') {
  try {
    console.log(`🚀 Registering agent: ${name}`)
    
    const response = await axios.post(`${PAYMENT_API}/registry`, {
      name,
      description,
      type: 'arduino',
      metadata: {
        platform: 'Arduino Uno',
        version: '1.0.0',
        capabilities: ['payment_send', 'payment_receive']
      }
    }, {
      headers: {
        'Content-Type': 'application/json',
        'token': ADMIN_KEY
      }
    })
    
    console.log(`✅ Agent registered:`, response.data)
    return response.data
  } catch (error) {
    console.error(`❌ Failed to register agent ${name}:`)
    console.error('   Status:', error.response?.status)
    console.error('   Data:', error.response?.data)
    throw error
  }
}

async function sendPayment(fromAgent, toAgent, amount) {
  try {
    console.log(`💸 Sending payment: ${amount} ADA from ${fromAgent} to ${toAgent}`)
    
    const response = await axios.post(`${PAYMENT_API}/payment`, {
      from: fromAgent,
      to: toAgent,
      amount,
      currency: 'ADA'
    }, {
      headers: {
        'Content-Type': 'application/json',
        'token': ADMIN_KEY
      }
    })
    
    console.log(`✅ Payment sent:`, response.data)
    return response.data
  } catch (error) {
    console.error(`❌ Payment failed:`)
    console.error('   Status:', error.response?.status)
    console.error('   Data:', error.response?.data)
    throw error
  }
}

async function getAgentBalance(agentId) {
  try {
    console.log(`💰 Getting balance for agent: ${agentId}`)
    
    const response = await axios.get(`${PAYMENT_API}/wallet?agentId=${agentId}`, {
      headers: {
        'token': ADMIN_KEY
      }
    })
    
    console.log(`✅ Agent balance:`, response.data)
    return response.data
  } catch (error) {
    console.error(`❌ Failed to get balance for ${agentId}:`)
    console.error('   Status:', error.response?.status)
    console.error('   Data:', error.response?.data)
    throw error
  }
}

async function main() {
  console.log('🎯 Testing real Masumi Network integration with Arduino agents\n')
  
  try {
    // Register Arduino A (Sender)
    const arduinoA = await registerAgent('Arduino-A-Sender', 'Arduino A agent for sending payments')
    
    // Register Arduino B (Receiver) 
    const arduinoB = await registerAgent('Arduino-B-Receiver', 'Arduino B agent for receiving payments')
    
    console.log('\n📊 Getting initial balances...')
    
    // Get initial balances
    await getAgentBalance(arduinoA.id)
    await getAgentBalance(arduinoB.id)
    
    console.log('\n💸 Testing Arduino-to-Arduino payment...')
    
    // Send payment from Arduino A to Arduino B
    await sendPayment(arduinoA.id, arduinoB.id, 50)
    
    console.log('\n📊 Getting final balances...')
    
    // Check balances after payment
    await getAgentBalance(arduinoA.id)
    await getAgentBalance(arduinoB.id)
    
    console.log('\n🎉 Arduino-to-Arduino transaction completed successfully!')
    
  } catch (error) {
    console.error('\n💥 Test failed:', error.message)
    process.exit(1)
  }
}

main()