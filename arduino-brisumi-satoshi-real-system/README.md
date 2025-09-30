# Arduino × Masumi × Cardano (Preprod) — Hardware-triggered Payments

A production-quality demo showcasing Arduino button-triggered ADA payments on Cardano Preprod, orchestrated by Masumi services and Satoshi agents, with live dashboards and an ESP8266 LCD displaying the real transaction hash.

## Quickstart

- Prereqs: Docker Desktop, Node.js 18+, Arduino IDE, Blockfrost Preprod key
- Configure: edit `env` with your Blockfrost key, agent addresses, AGENT1_SKEY_CBOR, and SERIAL_PATH
- Start stack:
  - docker compose up -d --build
  - cd frontend/web-dashboard; npm ci; npm start → http://localhost:8090
- Flash hardware:
  - Arduino: `hardware/arduino-uno/payment_trigger.ino`
  - ESP8266: set WiFi/PC IP in `hardware/esp8266/transaction_display.ino`
- Press the button. Watch the dashboard and LCD show the transaction hash; verify on CardanoScan.

## Services

- Masumi Payment (:3001) — APIs and orchestration; persists transactions
- Cardano Integration (:4002) — Lucid + Blockfrost based ADA transfer and queries
- AI Agents (:6001) — Decision engine approving transfers (pluggable strategies)
- Arduino Bridge (:5001) — Serial-to-API gateway, Socket.IO events for dashboard

## Security Notes

- Never commit real keys. `env` is git-ignored. Use ADMIN_TOKEN to protect sensitive endpoints.
- Use testnet (preprod) only. For mainnet, perform a full security review and audit.

See `docs/setup-guide.md` and `docs/api-documentation.md` for details.