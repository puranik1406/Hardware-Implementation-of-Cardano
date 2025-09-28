// Test authentication with Masumi services
import axios from 'axios'

const PAYMENT_API = 'http://localhost:3001/api/v1'
const REGISTRY_API = 'http://localhost:3000/api/v1'
const ADMIN_KEY = '8d6b3c5f8fca31d4a72f5e8897a1c9c9b4a7d8f03e1f82a35a3f9f7b6a6d2a1c'

async function testAuth() {
  console.log('🎯 Testing authentication with Masumi services\n')

  try {
    // Test health endpoint first (no auth required)
    console.log('🏥 Testing health endpoint (no auth)...')
    const healthResponse = await axios.get(`${PAYMENT_API}/health`)
    console.log('✅ Health check passed:', healthResponse.data)
  } catch (error) {
    console.error('❌ Health check failed:', error.message)
  }

  try {
    // Test an authenticated endpoint to verify our auth token
    console.log('\n🔑 Testing authentication with payment service...')
    const authResponse = await axios.get(`${PAYMENT_API}/wallet`, {
      headers: {
        'token': ADMIN_KEY
      }
    })
    console.log('✅ Authentication successful:', authResponse.data)
  } catch (error) {
    console.error('❌ Authentication failed:')
    console.error('   Status:', error.response?.status)
    console.error('   Data:', error.response?.data)
    
    if (error.response?.status === 401) {
      console.error('\n💡 This means the API key is not valid or not in the database.')
      console.error('   We need to check if the API key exists in the Masumi database.')
    }
  }

  try {
    // Test registry service authentication
    console.log('\n🔑 Testing authentication with registry service...')
    const registryResponse = await axios.get(`${REGISTRY_API}/api-key-status`, {
      headers: {
        'token': ADMIN_KEY
      }
    })
    console.log('✅ Registry authentication successful:', registryResponse.data)
  } catch (error) {
    console.error('❌ Registry authentication failed:')
    console.error('   Status:', error.response?.status) 
    console.error('   Data:', error.response?.data)
  }
}

testAuth().catch(console.error)