// Node example: register agent and listen to payments via WebSocket
// Usage: node examples/node/register-and-listen.mjs

import axios from 'axios'
import WebSocket from 'ws'
import dotenv from 'dotenv'
dotenv.config()

const API = process.env.MASUMI_API_URL || 'http://localhost:4000/v1'
const WS = process.env.MASUMI_WS_URL || 'ws://localhost:4000/ws'
const ADMIN_SECRET = process.env.MASUMI_ADMIN_SECRET || 'super_secret_here'

async function registerAgent(name) {
  const res = await axios.post(`${API}/agents/register`, {
    name,
    description: 'agent for demos',
    wallet: { type: 'managed' },
  }, {
    headers: { 'x-admin-secret': ADMIN_SECRET },
  })
  return res.data
}

async function main() {
  console.log('API:', API)
  console.log('WS :', WS)
  const agent = await registerAgent('agent_001')
  console.log('Registered agent:', agent)

  const url = `${WS}/payments/${agent.agentId}?admin_secret=${encodeURIComponent(ADMIN_SECRET)}`
  const ws = new WebSocket(url)
  ws.on('open', () => console.log('WS open'))
  ws.on('message', (msg) => console.log('WS msg:', msg.toString()))
  ws.on('close', () => console.log('WS closed'))
  ws.on('error', (e) => console.error('WS error:', e.message))
}

main().catch((e) => {
  console.error('Error:', e?.response?.data || e.message)
  process.exit(1)
})
