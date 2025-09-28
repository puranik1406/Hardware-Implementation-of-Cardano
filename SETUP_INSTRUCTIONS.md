# Quick Setup for Production-Ready Masumi Integration

This script follows the exact workflow from your instructions to get a production-ready Masumi setup.

## Prerequisites Check

Before starting, ensure you have:
- [x] Docker & Docker Compose installed
- [x] Node.js v18+ and npm/yarn
- [x] Git
- [ ] Blockfrost account with project ID (get from https://docs.blockfrost.io)

## Step 1: Clone Masumi Repos (Optional - for custom builds)

```powershell
# Optional: Clone official Masumi repos if you want to build from source
git clone https://github.com/masumi-network/masumi-payment-service.git
git clone https://github.com/masumi-network/masumi-registry-service.git
```

## Step 2: Configure Environment

Update your `.env` file (already created) with real values:

```env
# Required for production
BLOCKFROST_PROJECT_ID=your_blockfrost_project_id_here
MASUMI_ADMIN_SECRET=your_secure_secret_here

# Optional: Use your own Blockfrost project for frontend
VITE_BLOCKFROST_PROJECT_ID=your_blockfrost_project_id_here
VITE_MASUMI_ADMIN_SECRET=your_secure_secret_here
```

## Step 3: Start Masumi Services

```powershell
# Start the full stack (Postgres + Payment Service + Registry)
npm run compose:up

# Monitor logs to ensure services start correctly
npm run compose:logs
```

## Step 4: Quick Health Checks

```powershell
# Test agent registration (replace super_secret_here with your actual secret)
curl -X POST http://localhost:4000/v1/agents/register `
  -H "Content-Type: application/json" `
  -H "x-admin-secret: super_secret_here" `
  -d '{\"name\":\"agent_001\",\"description\":\"test agent\",\"wallet\":{\"type\":\"managed\"}}'

# Check if registry service is running
curl http://localhost:3000/health
```

## Step 5: Test WebSocket + Payment Example

```powershell
# Install additional dependencies and run the Node.js example
npm install
npm run example:node
```

## Step 6: Start Frontend

```powershell
# Start the React app (connects to local Masumi services)
npm run dev
```

## Step 7: Test End-to-End Flow

1. Open http://localhost:5173
2. Use the payment panel to send ADA between agents
3. Watch the Agent Status panel for real-time updates
4. Check Docker logs for backend activity: `npm run compose:logs`

## Troubleshooting

### Services won't start
- Check Docker is running
- Ensure ports 3000, 4000, 5432 are available
- Check `npm run compose:logs` for error details

### API 401/403 errors
- Verify `MASUMI_ADMIN_SECRET` matches in .env and Docker compose
- Check header format: `x-admin-secret` (not `Authorization: Bearer`)

### Blockfrost errors
- Verify `BLOCKFROST_PROJECT_ID` is correct for your network (preprod/testnet)
- Check project permissions at https://blockfrost.io

### WebSocket connection issues
- Ensure WebSocket URL uses `ws://` (not `wss://`) for local development
- Check firewall/antivirus blocking WebSocket connections

## Production Deployment

For production, use Railway/Fly/DigitalOcean:

1. Set environment variables as secrets in your platform
2. Use `wss://` and `https://` URLs
3. Consider running your own Cardano node for high throughput
4. Enable proper logging and monitoring

## Next Steps

- Add real Blockfrost project ID to enable Cardano transactions
- Fund test wallets using Cardano testnet faucet
- Deploy to staging environment (Railway has one-click Masumi deploy)
- Implement error handling and retry logic for production use