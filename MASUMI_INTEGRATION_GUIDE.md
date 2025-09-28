# Masumi Network Integration Guide

## Overview
This guide will help you obtain the necessary API endpoints, credentials, and documentation needed to integrate with the Masumi Network for agentic payments on the Cardano blockchain.

## 1. Masumi Network API Setup

### 1.1 Getting Access to Masumi Network

#### Option A: Official Masumi Network (Recommended)
1. **Visit the Masumi Network Developer Portal**
   - Go to: `https://developers.masumi.network` (if available)
   - Or check: `https://docs.masumi.network`

2. **Create a Developer Account**
   - Register with your email and project details
   - Verify your account via email confirmation
   - Complete KYC if required for mainnet access

3. **Generate API Credentials**
   - Navigate to "API Keys" or "Credentials" section
   - Create a new API key for your Arduino project
   - Note down your:
     - API Key ID
     - API Secret Key
     - Project ID (if applicable)

#### Option B: Cardano Testnet Integration
If Masumi Network has direct Cardano integration:

1. **Cardano Testnet Access**
   - Visit: `https://testnets.cardano.org`
   - Check for Masumi Network testnet endpoints
   - Look for: `https://masumi-testnet.cardano.org`

2. **Alternative Cardano APIs**
   - Blockfrost API: `https://blockfrost.io`
   - Cardano GraphQL: `https://cardano-graphql.api.cardano.org`
   - Koios API: `https://api.koios.rest`

### 1.2 API Endpoints Structure

Once you have access, the typical endpoint structure should be:

```
Base URL: https://api.masumi.network/v1
or: https://masumi-testnet.cardano.org/api/v1

Authentication: Bearer token or API key headers
Content-Type: application/json
```

**Expected Endpoints:**
- `POST /agents/register` - Agent registration
- `POST /payments/send` - Send payments
- `GET /payments/receive/{agentId}` - Check received payments
- `GET /agents/{agentId}/balance` - Check balance
- `GET /agents/{agentId}/transactions` - Transaction history
- `GET /network/stats` - Network statistics

## 2. WebSocket Endpoints

### 2.1 Real-time Connections

**Typical WebSocket URLs:**
```
Network Stats: wss://api.masumi.network/ws/stats
Payment Notifications: wss://api.masumi.network/ws/payments/{agentId}
Agent Status: wss://api.masumi.network/ws/agents/{agentId}
```

**Authentication Methods:**
1. **Token-based**: Include JWT token in connection headers
2. **API Key**: Pass API key as query parameter
3. **Session-based**: Authenticate via HTTP first, then use session

## 3. Cardano Integration Setup

### 3.1 Wallet Management

#### Option A: Use Cardano Wallet Backend
1. **Install Cardano Wallet**
   ```bash
   # Download from: https://github.com/input-output-hk/cardano-wallet
   # Or use Docker
   docker pull inputoutput/cardano-wallet
   ```

2. **API Endpoints**
   ```
   Base URL: http://localhost:8090/v2
   
   POST /wallets - Create wallet
   GET /wallets/{walletId} - Get wallet info
   POST /wallets/{walletId}/transactions - Send transaction
   GET /wallets/{walletId}/addresses - Get addresses
   ```

#### Option B: Use Third-party Services
1. **Blockfrost**
   - Sign up at: `https://blockfrost.io`
   - Get project ID for testnet/mainnet
   - Use their wallet APIs

2. **Cardano Serialization Library**
   - JavaScript: `@emurgo/cardano-serialization-lib-browser`
   - For transaction building and signing

### 3.2 Network Parameters

**Testnet Configuration:**
```json
{
  "networkId": 0,
  "protocolMagic": 1097911063,
  "networkMagic": 1097911063
}
```

**Mainnet Configuration:**
```json
{
  "networkId": 1,
  "protocolMagic": 764824073,
  "networkMagic": 764824073
}
```

## 4. Sokosumi Platform Integration

### 4.1 Getting Sokosumi Access

1. **Visit Sokosumi Platform**
   - Go to: `https://sokosumi.com` or `https://app.sokosumi.com`
   - Create developer account

2. **Developer Documentation**
   - Check: `https://docs.sokosumi.com`
   - Look for WebSocket API documentation

3. **Generate Credentials**
   - Create new application/project
   - Get WebSocket connection details
   - Note authentication method

### 4.2 WebSocket Connection Details

**Typical Sokosumi WebSocket:**
```
URL: wss://app.sokosumi.com/ws
or: wss://api.sokosumi.com/v1/ws

Authentication: 
- Bearer token in headers
- or API key in query params
```

**Message Format Example:**
```json
{
  "type": "payment_notification",
  "data": {
    "agentId": "agent_001",
    "amount": 100,
    "from": "addr1q...",
    "to": "addr1q...",
    "txHash": "abc123...",
    "timestamp": "2025-09-28T10:30:00Z"
  }
}
```

## 5. Alternative Solutions (If Official APIs Unavailable)

### 5.1 Create Mock APIs for Development

If you can't access the real APIs immediately, create local mock services:

1. **Local Mock Server**
   ```bash
   npm install -g json-server
   # Create db.json with mock data
   json-server --watch db.json --port 3001
   ```

2. **WebSocket Mock Server**
   ```bash
   npm install ws
   # Create simple WebSocket server for testing
   ```

### 5.2 Use Cardano Direct Integration

1. **Cardano CLI**
   - Install Cardano node and CLI
   - Direct blockchain interaction
   - Custom transaction building

2. **Cardano Submit API**
   ```
   https://cardano-submit-api-testnet.iohkdev.io
   https://cardano-submit-api-mainnet.iohkdev.io
   ```

## 6. Environment Configuration

### 6.1 Create Environment File

Create `.env` file in your project:

```env
# Masumi Network
MASUMI_API_URL=https://api.masumi.network/v1
MASUMI_API_KEY=your_api_key_here
MASUMI_WS_URL=wss://api.masumi.network/ws

# Cardano
CARDANO_NETWORK=testnet
CARDANO_WALLET_URL=http://localhost:8090/v2
BLOCKFROST_PROJECT_ID=your_blockfrost_project_id

# Sokosumi
SOKOSUMI_WS_URL=wss://app.sokosumi.com/ws
SOKOSUMI_API_KEY=your_sokosumi_key

# Development
NODE_ENV=development
DEBUG_MODE=true
```

### 6.2 Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment variables for all credentials**
3. **Implement proper error handling for API failures**
4. **Add rate limiting to prevent API abuse**
5. **Use HTTPS/WSS for all connections**

## 7. Testing Your Integration

### 7.1 API Testing Tools

1. **Postman/Insomnia**
   - Test REST API endpoints
   - Save environment configurations
   - Test authentication flows

2. **WebSocket Testing**
   - Use online WebSocket testers
   - Or browser developer tools

### 7.2 Integration Checklist

- [ ] API credentials obtained and configured
- [ ] Base URLs and endpoints identified
- [ ] Authentication working (401/403 errors resolved)
- [ ] WebSocket connections established
- [ ] Wallet creation/management working
- [ ] Test transactions successful
- [ ] Error handling implemented
- [ ] Rate limiting respected

## 8. Common Issues and Solutions

### 8.1 API Access Issues

**Problem**: 403 Forbidden or 401 Unauthorized
**Solution**: 
- Check API key format and headers
- Verify account status and permissions
- Ensure correct base URL

**Problem**: CORS errors in browser
**Solution**:
- Configure CORS properly on server
- Use proxy server for development
- Check browser security policies

### 8.2 WebSocket Issues

**Problem**: Connection drops frequently
**Solution**:
- Implement reconnection logic
- Check network stability
- Verify WebSocket URL and authentication

**Problem**: Message format errors
**Solution**:
- Check JSON schema validation
- Verify message structure with documentation
- Handle parsing errors gracefully

## 9. Next Steps

Once you have the API details:

1. **Update the environment configuration**
2. **Replace mock implementations with real API calls**
3. **Implement proper error handling and retry logic**
4. **Add comprehensive logging for debugging**
5. **Test thoroughly with small amounts on testnet**
6. **Deploy to production with mainnet credentials**

---

## Contact Information

If you need help obtaining these credentials:

1. **Masumi Network Support**: Check their official documentation or support channels
2. **Cardano Developer Resources**: https://developers.cardano.org
3. **Sokosumi Support**: Check their platform documentation
4. **Community Forums**: Cardano Stack Exchange, Reddit r/cardano

Remember to always start with testnet environments before moving to mainnet!