# Architecture Overview

This document describes the architecture of the Arduino Masumi Network Simulator, inspired by patterns from awesome-llm-apps and agno/cookbook.

## High-Level Diagram

- UI (React + Vite)
  - Components: ArduinoBoard, MasumiPaymentPanel, AgentStatusPanel
  - Services: MasumiNetworkService (REST + WebSocket)
- Agent Layer
  - Arduino Agents: Sender (A), Receiver (B)
  - Optional LLM/Decision Layer: Policy hooks (future)
- Integrations
  - Masumi REST API (payments, agents, stats)
  - Masumi WebSocket (network stats)
  - Sokosumi WebSocket (agent/payment events)
  - Cardano (Blockfrost or Cardano Wallet backend)

## Data Flows

1. UI -> Service -> Masumi REST: register agents, send payments, fetch balances, history
2. WS -> Service -> UI Events: network stats, payment notifications, agent status
3. Agents -> UI: local state for code, status, and serial output

## Event Bus

- CustomEvent channels:
  - `masumi:networkStats` — updates AgentStatusPanel
  - `masumi:payment` — updates App payment history
  - `masumi:agentStatus` — future agent lifecycle updates

## Environments

- Mock: json-server for rapid prototyping
- Real: Masumi + Sokosumi + Blockfrost

## Security

- Environment-driven config via Vite `import.meta.env`
- Do not commit secrets
- HTTPS/WSS in production
