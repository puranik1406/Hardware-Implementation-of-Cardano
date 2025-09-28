# Production-Ready Setup (Masumi Payment & Registry + Cardano)

This guide provides a tested, production-oriented workflow using Docker, Blockfrost, and Masumi services (Payment + Registry). It includes exact commands, env configuration, REST + WebSocket examples, and deployment notes.

## 0) Prerequisites

- Docker + Docker Compose
- Node.js 18+
- Git
- Blockfrost account and Project ID (testnet/preprod)

## 1) Clone Masumi Services

```bash
git clone https://github.com/masumi-network/masumi-payment-service.git
git clone https://github.com/masumi-network/masumi-registry-service.git
```

## 2) Create docker-compose.yml

```yaml
version: "3.8"
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: masumi
      POSTGRES_PASSWORD: masumi_pass
      POSTGRES_DB: masumi_db
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  masumi-payment:
    image: masumi/payment-service:latest   # or build: ./masumi-payment-service
    depends_on:
      - postgres
    environment:
      NODE_ENV: development
      DATABASE_URL: postgres://masumi:masumi_pass@postgres:5432/masumi_db
      BLOCKFROST_PROJECT_ID: ${BLOCKFROST_PROJECT_ID}
      BLOCKFROST_API_URL: https://cardano-preprod.blockfrost.io/api/v0
      MASUMI_REGISTRY_URL: http://masumi-registry:3000
      MASUMI_ADMIN_SECRET: ${MASUMI_ADMIN_SECRET}
    ports:
      - "4000:4000" # REST API

  masumi-registry:
    image: masumi/registry-service:latest  # or build: ./masumi-registry-service
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgres://masumi:masumi_pass@postgres:5432/masumi_db
      BLOCKFROST_PROJECT_ID: ${BLOCKFROST_PROJECT_ID}
    ports:
      - "3000:3000"

volumes:
  pgdata:
```

## 3) Environment (.env)

Use the root `.env` created in this project, or create a new one beside docker-compose.yml:

```env
BLOCKFROST_PROJECT_ID=your_blockfrost_project_id_here
BLOCKFROST_API_URL=https://cardano-preprod.blockfrost.io/api/v0
MASUMI_ADMIN_SECRET=super_secret_here
MASUMI_API_URL=http://localhost:4000/v1
MASUMI_WS_URL=ws://localhost:4000/ws
DATABASE_URL=postgres://masumi:masumi_pass@localhost:5432/masumi_db
```

## 4) Start services

```bash
docker-compose up -d
# View logs
docker-compose logs -f masumi-payment
```

## 5) Quick REST checks

```bash
# Register an agent (headers may differ per service config)
curl -X POST http://localhost:4000/v1/agents/register \
  -H "Content-Type: application/json" \
  -H "x-admin-secret: super_secret_here" \
  -d '{"name":"agent_001","description":"test agent","wallet":{"type":"managed"}}'

# Send payment (example payload — adjust to service spec)
curl -X POST http://localhost:4000/v1/payments/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <agent_token_if_required>" \
  -d '{"from":"agent_001","to":"addr_test1...","amount":1000000,"asset":"lovelace"}'
```

## 6) Node.js example (REST + WebSocket)

```js
// npm i axios ws dotenv
import axios from 'axios';
import WebSocket from 'ws';
import dotenv from 'dotenv';
dotenv.config();

const API = process.env.MASUMI_API_URL || 'http://localhost:4000/v1';
const WS = process.env.MASUMI_WS_URL || 'ws://localhost:4000/ws';
const ADMIN_SECRET = process.env.MASUMI_ADMIN_SECRET;

async function registerAgent(name) {
  const res = await axios.post(`${API}/agents/register`, {
    name,
    description: 'agent for demos',
    wallet: { type: 'managed' },
  }, {
    headers: { 'x-admin-secret': ADMIN_SECRET },
  });
  return res.data;
}

async function main() {
  const agent = await registerAgent('agent_001');
  console.log('Registered agent:', agent);

  const ws = new WebSocket(`${WS}/payments/${agent.agentId}?admin_secret=${ADMIN_SECRET}`);
  ws.on('open', () => console.log('WS open'));
  ws.on('message', (msg) => console.log('WS msg:', msg.toString()));
}

main().catch(console.error);
```

## 7) Frontend wiring (this project)

- Configure `.env` with `VITE_*` variables (see `.env.example` and root `.env`).
- The app uses `src/services/MasumiNetworkService.js` to call REST and connect to WebSockets.
- `AgentStatusPanel` listens for `masumi:networkStats` events; `App.jsx` listens for `masumi:payment`.

## 8) Deployment notes

- Prefer Railway/Fly/DigitalOcean for dockerized deployments.
- Set `BLOCKFROST_PROJECT_ID`, `DATABASE_URL`, `MASUMI_ADMIN_SECRET` as secrets in your platform.
- For production Cardano traffic, either:
  - Use Blockfrost with proper plan, or
  - Run `cardano-node` + `cardano-wallet` and point services to it.

## 9) Troubleshooting

- API 401/403: check auth headers (`x-admin-secret` or `Authorization: Bearer`).
- Blockfrost 403: confirm Project ID and correct network API URL.
- WebSocket disconnects: implement reconnection/backoff.
- DB issues: verify `DATABASE_URL` and DB migrations.

## References

- Masumi docs: https://docs.masumi.network/
- Masumi GitHub: https://github.com/masumi-network
- Blockfrost: https://docs.blockfrost.io/
- Lucid (Cardano JS): https://lucid.spacebudz.io/
