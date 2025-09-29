# Setup Guide

This guide boots the scaffold, then you can wire real Satoshi/NEAR integration.

## Prerequisites
- Docker Desktop
- Node.js 18+ (for local dev)
- Arduino IDE (for Uno + ESP8266)
- COM port for Arduino (Windows e.g., COM3)

## Configure
Create `.env` files as needed:

- backend/arduino-bridge/.env
  - SERIAL_PATH=COM3
  - SERIAL_BAUD=9600
  - MASUMI_PAYMENT_URL=http://localhost:3001/api/cardano/transfer

- backend/cardano-integration/.env
  - CARDANO_NETWORK=preprod
  - BLOCKFROST_PROJECT_ID=...
  - BLOCKFROST_BASE_URL=https://cardano-preprod.blockfrost.io/api/v0
  - AGENT1_SKEY_CBOR=... # Private key CBOR of Agent 1 (sender)

## Start Infra

1. docker compose up -d
2. Install and start backend services (if running outside Docker):
   - npm ci && npm start in each service folder

## Flash Hardware
- Arduino Uno: upload `hardware/arduino-uno/payment_trigger.ino`
- ESP8266: update WiFi + API URL and upload `hardware/esp8266/transaction_display.ino`

## Dashboard
- cd frontend/web-dashboard; npm ci; npm start
- Open http://localhost:8080

## Test Flow
- Press Uno button
- Bridge reads serial and calls Masumi Payment → Cardano Integration (returns real tx hash)
- Dashboard shows serial lines and tx + CardanoScan link
- ESP8266 fetches latest tx_id and shows it

## Wire Real Satoshi
- Replace TODOs in `backend/satoshi-integration/src/index.js`
- Update `backend/masumi-services/src/index.js` to call integration service for real transfers and update tx record with returned hash.
