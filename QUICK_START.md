# Quick Start Scripts

## 1. Run the setup script to configure your environment:

```bash
node setup-masumi.js
```

## 2. For development with mock APIs (if real APIs not available):

```bash
# Install json-server globally
npm install -g json-server

# Start mock API server
json-server --watch mock-api-db.json --port 3001 --routes routes.json
```

## 3. Start the development server:

```bash
npm run dev
```

## Available Endpoints (Mock API)

When running the mock API on localhost:3001:

- `GET /agents` - Get all agents
- `POST /agents` - Register new agent  
- `GET /agents/:id` - Get specific agent
- `GET /agents/:id/balance` - Get agent balance
- `GET /transactions` - Get all transactions
- `POST /transactions` - Create new transaction
- `GET /payments` - Get payments
- `POST /payments` - Send payment
- `GET /networkStats` - Get network statistics
- `GET /wallets` - Get wallets

## Environment Variables Reference

After running the setup script, check your `.env` file and update with real API credentials:

```env
# Replace these with real values:
VITE_MASUMI_API_KEY=your_real_api_key
VITE_BLOCKFROST_PROJECT_ID=your_blockfrost_project_id  
VITE_SOKOSUMI_API_KEY=your_sokosumi_api_key
```

## Testing the Integration

1. **Mock Mode**: Set `VITE_USE_MOCK_API=true` for development
2. **Real API Mode**: Set `VITE_USE_MOCK_API=false` with real credentials
3. **Check Console**: Look for connection logs and error messages
4. **Network Tab**: Monitor API calls in browser dev tools

## Troubleshooting

- **CORS Errors**: Use a proxy or configure CORS on your API server
- **WebSocket Issues**: Check firewall and network settings  
- **API Key Errors**: Verify credentials and account status
- **Rate Limiting**: Check API usage limits and implement retry logic