// Debug test to verify real Masumi integration in browser
console.log('🔍 DEBUGGING MASUMI INTEGRATION')
console.log('=' .repeat(50))

// Test environment variables
console.log('Environment Variables:')
console.log('VITE_MOCK_MODE:', import.meta.env.VITE_MOCK_MODE)
console.log('VITE_USE_MOCK_API:', import.meta.env.VITE_USE_MOCK_API) 

// Test if we can reach Masumi services
async function testMasumiConnection() {
  try {
    console.log('\n📡 Testing Masumi Service Connection...')
    
    const healthResponse = await fetch('http://localhost:3001/api/v1/health')
    if (healthResponse.ok) {
      const healthData = await healthResponse.json()
      console.log('✅ Payment Service Health:', healthData)
    } else {
      console.error('❌ Payment Service unreachable:', healthResponse.status)
    }
    
    const registryHealth = await fetch('http://localhost:3000/api/v1/health')  
    if (registryHealth.ok) {
      const registryData = await registryHealth.json()
      console.log('✅ Registry Service Health:', registryData)
    } else {
      console.error('❌ Registry Service unreachable:', registryHealth.status)
    }
    
  } catch (error) {
    console.error('❌ Connection test failed:', error.message)
  }
}

// Run the test
testMasumiConnection()

export { testMasumiConnection }