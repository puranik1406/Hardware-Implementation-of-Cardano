import { useState, useEffect } from 'react'
import { masumiService } from './services/MasumiNetworkService'
import ArduinoBoard from './components/ArduinoBoard'
import MasumiPaymentPanel from './components/MasumiPaymentPanel'
import AgentStatusPanel from './components/AgentStatusPanel'
import TransactionNotification from './components/TransactionNotification'
import RealArduinoPanel from './components/RealArduinoPanel'
import SatoshiAgentPanel from './components/SatoshiAgentPanel'
import './debug-masumi.js' // Debug Masumi integration
import './App.css'

function App() {
  const [arduinoA, setArduinoA] = useState({
    id: 'arduino_a',
    name: 'Arduino A (Sender)',
    code: `// Arduino A - Payment Sender
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "YourWiFi";
const char* password = "YourPassword";
const char* masumiEndpoint = "https://api.masumi.network";

String agentId = "agent_a_001";
String walletAddress = "addr1q9...";

void setup() {
  Serial.begin(115200);
  connectWiFi();
  initializeMasumiAgent();
}

void loop() {
  if (digitalRead(2) == HIGH) {
    sendPayment("agent_b_001", 100);
    delay(1000);
  }
  delay(100);
}

void connectWiFi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("WiFi connected");
}

void initializeMasumiAgent() {
  HTTPClient http;
  http.begin(masumiEndpoint + "/agents/register");
  http.addHeader("Content-Type", "application/json");
  
  String payload = "{\\"agentId\\":\\"" + agentId + "\\",\\"type\\":\\"arduino\\",\\"wallet\\":\\"" + walletAddress + "\\"}";
  
  int httpResponseCode = http.POST(payload);
  if (httpResponseCode > 0) {
    Serial.println("Agent registered successfully");
  }
  http.end();
}

void sendPayment(String recipientId, int amount) {
  HTTPClient http;
  http.begin(masumiEndpoint + "/payments/send");
  http.addHeader("Content-Type", "application/json");
  
  String payload = "{\\"from\\":\\"" + agentId + "\\",\\"to\\":\\"" + recipientId + "\\",\\"amount\\":" + String(amount) + "}";
  
  int httpResponseCode = http.POST(payload);
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("Payment sent: " + response);
  }
  http.end();
}`,
    status: 'idle',
    balance: 1000,
    lastAction: null
  })

  const [arduinoB, setArduinoB] = useState({
    id: 'arduino_b',
    name: 'Arduino B (Receiver)',
    code: `// Arduino B - Payment Receiver
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <WebSocketsClient.h>

const char* ssid = "YourWiFi";
const char* password = "YourPassword";
const char* masumiEndpoint = "https://api.masumi.network";
const char* sokosumi = "wss://app.sokosumi.com/ws";

String agentId = "agent_b_001";
String walletAddress = "addr1q8...";

WebSocketsClient webSocket;

void setup() {
  Serial.begin(115200);
  connectWiFi();
  initializeMasumiAgent();
  connectSokosumi();
}

void loop() {
  webSocket.loop();
  checkPendingPayments();
  delay(1000);
}

void connectWiFi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("WiFi connected");
}

void initializeMasumiAgent() {
  HTTPClient http;
  http.begin(masumiEndpoint + "/agents/register");
  http.addHeader("Content-Type", "application/json");
  
  String payload = "{\\"agentId\\":\\"" + agentId + "\\",\\"type\\":\\"arduino\\",\\"wallet\\":\\"" + walletAddress + "\\"}";
  
  int httpResponseCode = http.POST(payload);
  if (httpResponseCode > 0) {
    Serial.println("Agent registered successfully");
  }
  http.end();
}

void connectSokosumi() {
  webSocket.begin("app.sokosumi.com", 80, "/ws");
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_CONNECTED:
      Serial.println("Connected to Sokosumi");
      break;
    case WStype_TEXT:
      handleSokosumiMessage((char*)payload);
      break;
    default:
      break;
  }
}

void handleSokosumiMessage(String message) {
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, message);
  
  if (doc["type"] == "payment_received") {
    int amount = doc["amount"];
    String from = doc["from"];
    Serial.println("Received payment: " + String(amount) + " from " + from);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(1000);
    digitalWrite(LED_BUILTIN, LOW);
  }
}

void checkPendingPayments() {
  HTTPClient http;
  http.begin(masumiEndpoint + "/payments/pending/" + agentId);
  
  int httpResponseCode = http.GET();
  if (httpResponseCode > 0) {
    String response = http.getString();
    // Process pending payments
  }
  http.end();
}`,
    status: 'idle',
    balance: 500,
    lastAction: null
  })

  const [paymentHistory, setPaymentHistory] = useState([])
  const [agentNetwork, setAgentNetwork] = useState({
    connected: false,
    agents: [],
    totalTransactions: 0
  })
  const [notification, setNotification] = useState(null)
  
  // Real Arduino hardware state
  const [arduinoStatus, setArduinoStatus] = useState({
    connected: false,
    port: null,
    agentId: null
  })
  const [esp32Status, setEsp32Status] = useState({
    connected: false,
    port: null,
    wifiConnected: false,
    ipAddress: null
  })
  const [recentCommands, setRecentCommands] = useState([])
  
  // Satoshi AI Agents state
  const [satoshiAgents, setSatoshiAgents] = useState([])
  const [mcpConnected, setMcpConnected] = useState(false)

  useEffect(() => {
    // Initialize Masumi Network service and create real Arduino agents
    let mounted = true
    
    async function initializeRealMasumiAgents() {
      try {
        console.log('🚀 STARTING REAL MASUMI INITIALIZATION')
        console.log('Mounted state:', mounted)
        
        // Initialize Masumi service
        console.log('📡 Calling masumiService.initialize()...')
        await masumiService.initialize()
        
        if (!mounted) {
          console.log('⚠️ Component unmounted during init, aborting')
          return
        }
        
        console.log('✅ MASUMI SERVICE INITIALIZED SUCCESSFULLY')
        setAgentNetwork((prev) => {
          console.log('🔄 Setting network connected to true')
          return { ...prev, connected: true }
        })
        
        // Use your pre-funded wallet addresses instead of creating new ones
        console.log('🏦 Using pre-funded Arduino wallet addresses...')
        
        // Arduino A (Sender) - Your funded wallet
        const agentA = {
          id: `agent_${Date.now()}_a`,
          name: 'Arduino A (Sender)',
          description: 'Arduino Uno sender device for agentic payments',
          walletAddress: 'addr_test1qrffhpxs9ky88sxfm9788mr8a4924e0uhl4fexvy9z5pt084p3q2uhgh9wvft4ejrjhx5yes2xpmy2cuufmzljdwtf7qvgt5rz',
          network: 'Preprod',
          status: 'active',
          createdAt: new Date().toISOString()
        }
        
        // Arduino B (Receiver) - Your funded wallet
        const agentB = {
          id: `agent_${Date.now()}_b`,
          name: 'Arduino B (Receiver)',
          description: 'Arduino Uno receiver device for agentic payments',
          walletAddress: 'addr_test1qqxdsjedg0fpurjt345lymmyxrs2r4u7etwchfwze7fwvfx76eyhp6agt96xprlux3tgph0zm5degavwkge2f9jmszqqg3p703',
          network: 'Preprod',
          status: 'active',
          createdAt: new Date().toISOString()
        }
        
        if (!mounted) return
        
        console.log('✅ Real Arduino agents created!')
        console.log('Arduino A Wallet:', agentA.walletAddress)
        console.log('Arduino B Wallet:', agentB.walletAddress)
        
        // Fetch real wallet balances from Cardano blockchain
        console.log('💰 Fetching real wallet balances...')
        const [balanceA, balanceB] = await Promise.all([
          masumiService.getWalletBalance(agentA.walletAddress),
          masumiService.getWalletBalance(agentB.walletAddress)
        ])
        
        console.log('Balance A Result:', balanceA)
        console.log('Balance B Result:', balanceB)
        
        // Update Arduino A with real agent data and balance
        setArduinoA(prev => ({
          ...prev,
          id: agentA.id,
          agentId: agentA.id,
          walletAddress: agentA.walletAddress,
          walletVkey: agentA.walletVkey,
          balance: balanceA.success ? balanceA.balance : 0,
          network: agentA.network,
          status: 'connected',
          code: prev.code.replace('agent_a_001', agentA.id).replace('addr1q9...', agentA.walletAddress)
        }))
        
        // Update Arduino B with real agent data and balance
        setArduinoB(prev => ({
          ...prev,
          id: agentB.id,
          agentId: agentB.id,
          walletAddress: agentB.walletAddress,
          walletVkey: agentB.walletVkey,
          balance: balanceB.success ? balanceB.balance : 0,
          network: agentB.network,
          status: 'connected',
          code: prev.code.replace('agent_b_001', agentB.id).replace('addr1q8...', agentB.walletAddress)
        }))
        
        // Update agent network with real agents
        setAgentNetwork(prev => ({
          ...prev,
          connected: true,
          agents: [agentA, agentB],
          totalTransactions: 0
        }))
        
      } catch (error) {
        console.error('❌ MASUMI INITIALIZATION FAILED:', error)
        console.error('Error details:', error.message)
        console.error('Error stack:', error.stack)
        
        // Keep UI usable even if service init fails
        if (mounted) {
          console.log('🔄 Setting network connected to FALSE due to error')
          setAgentNetwork((prev) => ({ ...prev, connected: false }))
        }
      }
    }
    
    initializeRealMasumiAgents()

    const paymentListener = (evt) => {
      const data = evt.detail
      if (!data) return
      const { type, data: payload } = data
      if (type === 'payment_received' || type === 'payment_sent') {
        setPaymentHistory((prev) => [...prev, {
          id: payload?.txHash || Math.random().toString(36).slice(2, 9),
          from: payload?.from || 'unknown',
          to: payload?.to || 'unknown',
          amount: Number(payload?.amount || 0),
          timestamp: new Date().toISOString(),
          status: 'completed'
        }])
      }
    }
    window.addEventListener('masumi:payment', paymentListener)

    return () => {
      mounted = false
      window.removeEventListener('masumi:payment', paymentListener)
      masumiService.disconnect()
    }
  }, [])

  const handlePayment = async (fromId, toId, amount) => {
    try {
      console.log(`💸 Initiating payment: ${amount} ADA from ${fromId} to ${toId}`)
      
      const timestamp = new Date().toISOString()
      
      // Determine sender and receiver agents using real agent IDs
      const senderAgent = fromId === 'arduino_a' ? arduinoA : arduinoB
      const receiverAgent = toId === 'arduino_b' ? arduinoB : arduinoA
      
      // Update UI immediately (optimistic update)
      const payment = {
        id: `tx_${Date.now()}_${Math.random().toString(36).substr(2, 6)}`,
        from: senderAgent.name || fromId,
        to: receiverAgent.name || toId,
        fromAddress: senderAgent.walletAddress || 'unknown',
        toAddress: receiverAgent.walletAddress || 'unknown',
        amount,
        timestamp,
        status: 'pending'
      }

      setPaymentHistory(prev => [...prev, payment])

      // Update balances optimistically
      if (fromId === 'arduino_a' || fromId === arduinoA.id) {
        setArduinoA(prev => ({
          ...prev,
          balance: Math.max(0, prev.balance - amount),
          lastAction: `Sending ${amount} ADA to ${receiverAgent.name}`,
          status: 'sending'
        }))
      }

      if (toId === 'arduino_b' || toId === arduinoB.id) {
        setArduinoB(prev => ({
          ...prev,
          lastAction: `Receiving ${amount} ADA from ${senderAgent.name}`,
          status: 'receiving'
        }))
      }
      
      // Attempt real payment via Masumi Network
      console.log('📡 Sending real Cardano transaction via Masumi...')
      
      const result = await masumiService.sendPayment({
        fromAgentId: senderAgent.agentId || senderAgent.id,
        toAgentId: receiverAgent.agentId || receiverAgent.id,
        amount,
        metadata: { 
          source: 'arduino_simulator',
          fromWallet: senderAgent.walletAddress,
          toWallet: receiverAgent.walletAddress,
          network: senderAgent.network || 'Preprod'
        }
      })
      
      // Update payment status with complete transaction data
      setPaymentHistory(prev => 
        prev.map(p => 
          p.id === payment.id 
            ? { 
                ...p, 
                status: result.success ? 'completed' : 'failed',
                txHash: result.txHash,
                explorerUrl: result.explorerUrl,
                type: result.type,
                note: result.note,
                error: result.error,
                network: result.network
              }
            : p
        )
      )
      
      console.log('✅ Payment transaction completed:', result)
      console.log(`🔗 View on Cardano Explorer: ${result.explorerUrl}`)
      
      // Show notification for successful transaction
      if (result && result.success && result.txHash) {
        setNotification({
          txHash: result.txHash,
          explorerUrl: result.explorerUrl,
          amount,
          from: senderAgent.name || fromId,
          to: receiverAgent.name || toId,
          type: result.type || 'payment',
          network: result.network || 'Preprod'
        })
      }
      
      // Update final balances based on real transaction
      if (result && result.success) {
        if (toId === 'arduino_b' || toId === arduinoB.id) {
          setArduinoB(prev => ({
            ...prev,
            balance: prev.balance + amount,
            lastAction: `Received ${amount} ADA (${result.txHash?.slice(0, 8)}...)`,
            status: 'idle'
          }))
        }
      }
      
      // Reset sender status
      setTimeout(() => {
        if (fromId === 'arduino_a' || fromId === arduinoA.id) {
          setArduinoA(prev => ({ ...prev, status: 'idle' }))
        }
      }, 2000)
      
    } catch (error) {
      console.error('❌ Payment failed:', error.message)
      
      // Update payment status to failed
      setPaymentHistory(prev => 
        prev.map(p => 
          p.timestamp === timestamp 
            ? { ...p, status: 'failed', error: error.message }
            : p
        )
      )
      
      // Reset statuses on error
      setArduinoA(prev => ({ ...prev, status: 'idle' }))
      setArduinoB(prev => ({ ...prev, status: 'idle' }))
      
      // Show error in UI
      alert(`Payment failed: ${error.message}\n\nThis is expected if wallets need funding. Check console for details.`)
    }
  }

  const runArduinoCode = (arduinoId) => {
    console.log(`🔄 Running Arduino code for: ${arduinoId}`)
    
    if (arduinoId === 'arduino_a' || arduinoId === arduinoA.id) {
      setArduinoA(prev => ({ 
        ...prev, 
        status: 'running',
        lastAction: 'Executing payment code...'
      }))
      
      // Trigger real payment with actual agent IDs
      setTimeout(() => {
        const amount = 1.5 // 1.5 ADA for demo
        console.log(`💸 Arduino A executing: Send ${amount} ADA to Arduino B`)
        handlePayment(arduinoA.id || 'arduino_a', arduinoB.id || 'arduino_b', amount)
      }, 1500)
      
    } else if (arduinoId === 'arduino_b' || arduinoId === arduinoB.id) {
      setArduinoB(prev => ({ 
        ...prev, 
        status: 'listening',
        lastAction: 'Listening for payments...'
      }))
      
      setTimeout(() => {
        setArduinoB(prev => ({ 
          ...prev, 
          status: 'idle',
          lastAction: 'Ready to receive payments'
        }))
      }, 3000)
    }
  }

  // Arduino Hardware Management Functions
  const handleConnectBoards = async () => {
    try {
      console.log('🔍 Detecting Arduino boards...')
      
      // Simulate board detection and connection
      // In real implementation, this would call the MCP server
      setTimeout(() => {
        setArduinoStatus({
          connected: true,
          port: 'COM3',
          agentId: 'arduino_uno_sender'
        })
        
        setEsp32Status({
          connected: true,
          port: 'COM4',
          wifiConnected: true,
          ipAddress: '192.168.1.100'
        })
        
        console.log('✅ Arduino boards connected successfully')
      }, 2000)
      
    } catch (error) {
      console.error('❌ Failed to connect to Arduino boards:', error)
    }
  }

  const handleSendArduinoCommand = async (board, command) => {
    try {
      console.log(`📤 Sending command to ${board}: ${command}`)
      
      // Add to recent commands
      const newCommand = {
        timestamp: new Date().toISOString(),
        board,
        command,
        status: 'pending'
      }
      
      setRecentCommands(prev => [...prev.slice(-20), newCommand])
      
      // Simulate command execution
      setTimeout(() => {
        setRecentCommands(prev => 
          prev.map(cmd => 
            cmd === newCommand 
              ? { ...cmd, status: 'success', response: 'Command executed successfully' }
              : cmd
          )
        )
        
        // If it's a payment command, trigger the payment flow
        if (command.startsWith('SEND_PAYMENT:')) {
          const parts = command.split(':')
          const amount = parseFloat(parts[1])
          handlePayment('arduino_a', 'arduino_b', amount)
        }
        
      }, 1000)
      
    } catch (error) {
      console.error('❌ Arduino command failed:', error)
      
      setRecentCommands(prev => 
        prev.map(cmd => 
          cmd.command === command && cmd.board === board
            ? { ...cmd, status: 'error', response: error.message }
            : cmd
        )
      )
    }
  }

  // Satoshi AI Agent Management Functions
  const handleCreateSatoshiAgent = async (agentName) => {
    try {
      console.log(`🤖 Creating Satoshi AI agent: ${agentName}`)
      
      // Determine random strategy for AI agent
      const strategies = ['conservative', 'balanced', 'aggressive']
      const strategy = strategies[Math.floor(Math.random() * strategies.length)]
      
      const newAgent = {
        agent_id: `satoshi_${agentName.toLowerCase()}_${Date.now()}`,
        wallet_address: 'addr_test1qrffhpxs9ky88sxfm9788mr8a4924e0uhl4fexvy9z5pt084p3q2uhgh9wvft4ejrjhx5yes2xpmy2cuufmzljdwtf7qvgt5rz',
        balance: 1000,
        autonomous_mode: false,
        strategy: strategy,
        transaction_count: 0,
        ai_decisions_made: 0,
        successful_transactions: 0,
        market_sentiment: 0.5,
        risk_tolerance: strategy === 'conservative' ? 0.3 : strategy === 'balanced' ? 0.5 : 0.7,
        created_at: new Date().toISOString(),
        last_decision: null,
        decision_history: []
      }
      
      setSatoshiAgents(prev => [...prev, newAgent])
      
      console.log(`✅ Satoshi AI agent created: ${newAgent.agent_id} (${strategy} strategy)`)
      
      // Show notification
      setNotification({
        message: `🤖 AI Agent "${agentName}" created with ${strategy} strategy`,
        type: 'success'
      })
      
    } catch (error) {
      console.error('❌ Failed to create Satoshi agent:', error)
    }
  }

  const handleToggleAutonomous = async (agentId, enable) => {
    try {
      console.log(`🔄 ${enable ? 'Enabling' : 'Disabling'} autonomous mode for ${agentId}`)
      
      setSatoshiAgents(prev => 
        prev.map(agent => 
          agent.agent_id === agentId 
            ? { 
                ...agent, 
                autonomous_mode: enable,
                last_decision: enable ? new Date().toISOString() : agent.last_decision
              }
            : agent
        )
      )
      
      if (enable) {
        console.log(`🚀 Agent ${agentId} is now autonomous and will make AI-driven transaction decisions!`)
        
        // Start AI decision simulation for this agent
        simulateAIAgentActivity(agentId)
        
        setNotification({
          message: `🤖 AI Agent autonomous mode ENABLED - Agent will now make independent blockchain decisions`,
          type: 'success'
        })
      } else {
        console.log(`⏸️ Agent ${agentId} autonomous mode disabled`)
        
        setNotification({
          message: `⏸️ AI Agent autonomous mode disabled`,
          type: 'info'
        })
      }
      
    } catch (error) {
      console.error('❌ Failed to toggle autonomous mode:', error)
    }
  }

  // Simulate AI agent making autonomous decisions and transactions
  const simulateAIAgentActivity = (agentId) => {
    const runAIDecisionCycle = () => {
      setSatoshiAgents(prev => 
        prev.map(agent => {
          if (agent.agent_id === agentId && agent.autonomous_mode) {
            // Simulate AI decision process
            const marketConditions = Math.random()
            const confidence = Math.random()
            const shouldTransact = confidence > (agent.strategy === 'conservative' ? 0.7 : 
                                              agent.strategy === 'balanced' ? 0.55 : 0.4)
            
            const decision = {
              timestamp: new Date().toISOString(),
              confidence: confidence,
              market_conditions: marketConditions,
              decision: shouldTransact ? 'TRANSACT' : 'HOLD',
              amount: shouldTransact ? Math.round((Math.random() * 2 + 0.5) * 100) / 100 : 0
            }
            
            if (shouldTransact && agent.balance > decision.amount) {
              console.log(`🤖 AI Agent ${agentId} decided to transact ${decision.amount} ADA (Confidence: ${confidence.toFixed(2)})`)
              
              // Execute AI-driven transaction
              setTimeout(() => {
                handlePayment('satoshi_ai', 'arduino_b', decision.amount)
              }, 1000)
              
              return {
                ...agent,
                ai_decisions_made: agent.ai_decisions_made + 1,
                successful_transactions: agent.successful_transactions + 1,
                balance: agent.balance - decision.amount,
                last_decision: decision.timestamp,
                decision_history: [...agent.decision_history.slice(-10), decision],
                market_sentiment: marketConditions
              }
            } else {
              console.log(`🤖 AI Agent ${agentId} decided to HOLD (Confidence: ${confidence.toFixed(2)}, Conditions: ${marketConditions.toFixed(2)})`)
              
              return {
                ...agent,
                ai_decisions_made: agent.ai_decisions_made + 1,
                last_decision: decision.timestamp,
                decision_history: [...agent.decision_history.slice(-10), decision],
                market_sentiment: marketConditions
              }
            }
          }
          return agent
        })
      )
    }

    // Run AI decisions every 10-30 seconds
    const aiInterval = setInterval(() => {
      const agent = satoshiAgents.find(a => a.agent_id === agentId)
      if (!agent || !agent.autonomous_mode) {
        clearInterval(aiInterval)
        return
      }
      runAIDecisionCycle()
    }, Math.random() * 20000 + 10000) // 10-30 seconds
  }

  // Simulate MCP connection
  useEffect(() => {
    setTimeout(() => {
      setMcpConnected(true)
      console.log('🔗 MCP (Model Context Protocol) connected')
    }, 3000)
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Clean Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-blue-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">M</span>
            </div>
            <div>
              <h1 className="heading-2 mb-0">Arduino Masumi Network</h1>
              <p className="text-muted text-small">🤖 AI Agents + Real Hardware + Blockchain Payments</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="status-dot online"></div>
              <span className="text-small status-online font-medium">Network Online</span>
            </div>
            <div className="text-small text-muted">
              {paymentHistory.length} transactions completed
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6">
        {/* Network Status - Simplified */}
        <div className="mb-6">
          <AgentStatusPanel 
            network={agentNetwork}
            paymentHistory={paymentHistory}
          />
        </div>

        {/* AI Agent Spotlight Banner */}
        {satoshiAgents.some(agent => agent.autonomous_mode) && (
          <div className="bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 rounded-lg p-6 mb-6 text-white">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold mb-2 flex items-center gap-3">
                  🤖 Satoshi AI Agents Active
                  <span className="animate-pulse w-3 h-3 bg-green-400 rounded-full"></span>
                </h2>
                <p className="text-purple-100">
                  {satoshiAgents.filter(a => a.autonomous_mode).length} autonomous AI agents are making 
                  independent blockchain transaction decisions in real-time
                </p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold">
                  {satoshiAgents.reduce((sum, agent) => sum + (agent.ai_decisions_made || 0), 0)}
                </div>
                <div className="text-sm text-purple-200">AI Decisions Made</div>
              </div>
            </div>
          </div>
        )}

        {/* Real Arduino Hardware Section */}
        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          <RealArduinoPanel
            onSendCommand={handleSendArduinoCommand}
            arduinoStatus={arduinoStatus}
            esp32Status={esp32Status}
            recentCommands={recentCommands}
            onConnectBoards={handleConnectBoards}
          />
          
          <SatoshiAgentPanel
            agents={satoshiAgents}
            onCreateAgent={handleCreateSatoshiAgent}
            onToggleAutonomous={handleToggleAutonomous}
            onAgentAction={() => {}}
            mcpConnected={mcpConnected}
          />
        </div>

        {/* Simulated Arduino Boards Section */}
        <div className="mb-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
            <span className="w-6 h-6 bg-blue-500 rounded text-white text-sm flex items-center justify-center">S</span>
            Simulated Arduino Environment
          </h2>
        </div>
        
        <div className="grid lg:grid-cols-2 gap-6 mb-6">
          {/* Arduino Boards */}
          <div className="space-y-6">
            <ArduinoBoard
              arduino={arduinoA}
              onCodeChange={(code) => setArduinoA(prev => ({ ...prev, code }))}
              onRun={() => runArduinoCode('arduino_a')}
            />
            <ArduinoBoard
              arduino={arduinoB}
              onCodeChange={(code) => setArduinoB(prev => ({ ...prev, code }))}
              onRun={() => runArduinoCode('arduino_b')}
            />
          </div>

          {/* Payment Panel */}
          <div className="lg:sticky lg:top-6 lg:self-start">
            <MasumiPaymentPanel
              arduinoA={arduinoA}
              arduinoB={arduinoB}
              paymentHistory={paymentHistory}
              onSendPayment={handlePayment}
            />
          </div>
        </div>

        {/* Simple Footer */}
        <footer className="text-center py-8 border-t border-gray-200 mt-12">
          <p className="text-muted text-small">
            Arduino Masumi Network Simulator • Built for India Codex Hackathon 2025
          </p>
        </footer>
      </div>

      {/* Transaction Notification */}
      {notification && (
        <TransactionNotification
          transaction={notification}
          onClose={() => setNotification(null)}
        />
      )}
    </div>
  )
}

export default App
