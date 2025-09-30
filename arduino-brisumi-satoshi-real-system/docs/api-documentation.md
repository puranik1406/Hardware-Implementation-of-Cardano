# API Documentation

## Masumi Payment Service (port 3001)

GET /health → { ok: true }

POST /api/cardano/transfer
- body: { fromAgent, toAgent, amountAda, metadata?, skeyCbor? }
- returns: { tx_id, from_agent, to_agent, amount, status }

GET /api/cardano/balance/:address → { address, lovelace, ada }

GET /api/cardano/transaction/:txId → raw tx from Blockfrost

GET /api/latest-transaction → last tx row { tx_id, from_agent, to_agent, amount, status, created_at }

GET /admin → minimal admin HTML page (balances, copy/export helpers)

GET /api/wallets → { network, wallets: [{ role, address, balance }] }

GET /api/wallets/export?type=purchase|selling
- headers: x-admin-token: <ADMIN_TOKEN>
- returns: { mnemonic }

## Cardano Integration Service (port 4002)

GET /health → { ok: true, network }

GET /balance/:address → { address, lovelace, ada }

GET /transaction/:txId → raw Blockfrost tx

POST /transfer
- body: { fromAddress, toAddress, amountLovelace, skeyCbor? , metadata? }
- uses env AGENT1_SKEY_CBOR if not provided
- returns: { txHash }

## Arduino Bridge (port 5001)

  - serial:open, serial:line, serial:error
  - payment:trigger, payment:response, payment:error
 GET /health → { ok }
 WebSocket events:
  - hello { ts }
  - serial:open { path, baud }
  - serial:line { line }
  - serial:error { message }
  - payment:trigger { from, to, amount }
  - payment:response { ...payload from Masumi }
