# API Documentation

## Masumi Payment Service (port 3001)

  - body: { fromAgent, toAgent, amount }
  - returns: { tx_id, status }
 GET /health
 POST /api/cardano/transfer
  - body: { fromAgent, toAgent, amountAda, metadata? }
  - returns: { tx_id, from_agent, to_agent, amount, status }
 GET /api/cardano/balance/:address
 GET /api/cardano/transaction/:txId
 GET /api/latest-transaction → returns last persisted tx row { tx_id, ... }

## Satoshi Integration Service (port 4001)

  - body: { fromWalletId, toWalletId, amount }
 GET /health → { ok, network }
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
