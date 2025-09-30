# Setup Guide

This guide sets up a professional, end-to-end demo of hardware-triggered ADA transfers on Cardano Preprod using Masumi orchestration and Satoshi agents. Follow the steps carefully; real keys and faucets are required.

## Prerequisites
- Docker Desktop
- Node.js 18+ (for local dev)
- Arduino IDE (for Uno + ESP8266)
- A Blockfrost account and Preprod API key
- Windows: COM port for Arduino (e.g., COM3)

## Configure
Configure environment using the included `env` file at repo root (consumed by Docker):

- Edit `arduino-brisumi-satoshi-real-system/env` and set:
  - CARDANO_NETWORK=preprod
  - BLOCKFROST_PROJECT_ID=your_blockfrost_preprod_key
  - AGENT1_ADDRESS (sender), AGENT2_ADDRESS (receiver)
  - AGENT1_SKEY_CBOR=hex_of_private_key (for Preprod testing; do not commit)
  - SERIAL_PATH=COM3 (Windows) or /dev/ttyUSB0 (Linux/Mac via drivers)
  - Optional: ADMIN_TOKEN for guarding admin export endpoint

Generate or import test wallets:

- Option A (PowerShell, requires cardano-cli):
  - scripts/generate-cardano-preprod-wallet.ps1
  - scripts/export-cbor-from-skey.ps1 -SkeyPath .\keys\preprod.payment.skey
- Option B (Python):
  - pip install pycardano
  - python .\scripts\generate_preprod_wallet.py
  - Fund address using Cardano Preprod faucet.

## Start Infra

Windows PowerShell quickstart:

1. cd arduino-brisumi-satoshi-real-system
2. Verify `.\env` has your Blockfrost key and agent addresses
3. docker compose up -d --build
4. Optional: run the dashboard locally
  - cd frontend/web-dashboard; npm ci; npm start

## Flash Hardware
- Arduino Uno: upload `hardware/arduino-uno/payment_trigger.ino`
- ESP8266: update WiFi + API URL and upload `hardware/esp8266/transaction_display.ino`
  - Set WIFI_SSID, WIFI_PASS
  - Set PC_HOST to your PC LAN IP (where port 3001 is reachable)

## Dashboard
- cd frontend/web-dashboard; npm ci; npm start
- Open http://localhost:8090

## Test Flow
- Press Uno button
- Bridge reads serial and calls Masumi Payment → Cardano Integration (returns real tx hash)
- Dashboard shows serial lines and tx + CardanoScan link
- ESP8266 fetches latest tx_id and shows it

## Wire Real Satoshi
- Replace TODOs in `backend/satoshi-integration/src/index.js` once official SDK is available
- `backend/masumi-services/src/index.js` already calls Cardano Integration and persists the tx
- Protect admin endpoints using ADMIN_TOKEN (set in env)
