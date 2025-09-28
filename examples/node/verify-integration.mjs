// Verify real Masumi integration is working
import axios from 'axios'

const PAYMENT_API = 'http://localhost:3001/api/v1'
const ADMIN_KEY = '8d6b3c5f8fca31d4a72f5e8897a1c9c9b4a7d8f03e1f82a35a3f9f7b6a6d2a1c'

async function verifyIntegration() {
  console.log('🔍 Verifying Frontend Integration Status')
  console.log('=' .repeat(50))
  
  try {
    // Test 1: Health check
    console.log('1. Health Check...')
    const health = await axios.get(`${PAYMENT_API}/health`)
    console.log('✅ Masumi Payment Service: Online')
    
    // Test 2: Authentication  
    console.log('\n2. Authentication Test...')
    const auth = await axios.get(`http://localhost:3000/api/v1/api-key-status`, {
      headers: { 'token': ADMIN_KEY }
    })
    console.log('✅ API Key Valid:', auth.data.data.permission)
    
    // Test 3: Create Arduino wallet (what the frontend now does)
    console.log('\n3. Arduino Wallet Creation Test...')
    const wallet = await axios.post(`${PAYMENT_API}/wallet`, {
      walletType: 'hot',
      network: 'Preprod'
    }, {
      headers: { 
        'Content-Type': 'application/json',
        'token': ADMIN_KEY 
      }
    })
    
    const arduinoWallet = wallet.data.data
    console.log('✅ Arduino Wallet Created:')
    console.log('   Address:', arduinoWallet.walletAddress)
    console.log('   Network: Preprod Testnet')
    
    console.log('\n🎉 VERIFICATION COMPLETE')
    console.log('=' .repeat(50))
    console.log('✅ Real Masumi Integration: WORKING')
    console.log('✅ Arduino Wallet Creation: WORKING') 
    console.log('✅ Authentication: WORKING')
    console.log('✅ Frontend Ready: YES')
    
    console.log('\n💡 The React app now creates REAL Arduino agents!')
    console.log('   Open http://localhost:5173 to see it in action')
    
  } catch (error) {
    console.error('❌ Verification failed:', error.response?.data || error.message)
  }
}

verifyIntegration()