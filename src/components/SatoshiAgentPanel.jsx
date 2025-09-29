import { useState, useEffect } from 'react'
import { Bot, Brain, Zap, TrendingUp, Activity, Settings, Play, Pause } from 'lucide-react'

export default function SatoshiAgentPanel({ 
  agents = [],
  onCreateAgent,
  onToggleAutonomous,
  onAgentAction,
  mcpConnected = false
}) {
  const [newAgentName, setNewAgentName] = useState('')
  const [isCreating, setIsCreating] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [agentLogs, setAgentLogs] = useState([])

  // Simulate AI agent activity
  useEffect(() => {
    const interval = setInterval(() => {
      const autonomousAgents = agents.filter(agent => agent.autonomous_mode)
      
      if (autonomousAgents.length > 0) {
        const randomAgent = autonomousAgents[Math.floor(Math.random() * autonomousAgents.length)]
        const activities = [
          'Analyzing blockchain conditions',
          'Monitoring wallet balance',
          'Evaluating payment opportunities', 
          'Processing market data',
          'Optimizing transaction timing',
          'Checking network congestion'
        ]
        
        const activity = activities[Math.floor(Math.random() * activities.length)]
        
        setAgentLogs(prev => [...prev.slice(-50), {
          timestamp: new Date().toLocaleTimeString(),
          agentId: randomAgent.agent_id,
          activity,
          type: 'autonomous'
        }])
      }
    }, 2000)

    return () => clearInterval(interval)
  }, [agents])

  const handleCreateAgent = async () => {
    if (!newAgentName.trim()) return

    setIsCreating(true)
    try {
      await onCreateAgent(newAgentName)
      setNewAgentName('')
    } finally {
      setIsCreating(false)
    }
  }

  const getAgentStatusColor = (agent) => {
    if (agent.autonomous_mode) return 'bg-green-500'
    if (agent.balance > 0) return 'bg-blue-500'
    return 'bg-gray-500'
  }

  const getAgentStatusText = (agent) => {
    if (agent.autonomous_mode) return 'Autonomous'
    if (agent.balance > 0) return 'Ready'
    return 'Inactive'
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-white font-bold text-lg">Satoshi AI Agents</h3>
              <p className="text-purple-100 text-sm">Autonomous blockchain agents via MCP</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${mcpConnected ? 'bg-green-400' : 'bg-red-400'}`} />
            <span className="text-white text-sm">
              {mcpConnected ? 'MCP Connected' : 'MCP Disconnected'}
            </span>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Create New Agent */}
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4 mb-6">
          <h4 className="font-medium mb-3 flex items-center gap-2">
            <Brain className="w-4 h-4" />
            Create Satoshi AI Agent
          </h4>
          <div className="flex gap-2">
            <input
              type="text"
              value={newAgentName}
              onChange={(e) => setNewAgentName(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleCreateAgent()}
              placeholder="Enter agent name (e.g., 'Satoshi-Alpha')"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <button
              onClick={handleCreateAgent}
              disabled={!newAgentName.trim() || isCreating}
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              {isCreating ? 'Creating...' : 'Create Agent'}
            </button>
          </div>
        </div>

        {/* Active Agents */}
        <div className="mb-6">
          <h4 className="font-medium mb-3">Active Agents ({agents.length})</h4>
          
          {agents.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Bot className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p>No AI agents created yet</p>
              <p className="text-sm">Create your first Satoshi agent to get started</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {agents.map((agent) => (
                <div key={agent.agent_id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${getAgentStatusColor(agent)}`} />
                      <span className="font-medium">{agent.agent_id}</span>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      agent.autonomous_mode 
                        ? 'bg-green-100 text-green-700'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {getAgentStatusText(agent)}
                    </span>
                  </div>

                  <div className="space-y-2 text-sm mb-4">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Balance:</span>
                      <span className="font-medium">{agent.balance.toFixed(2)} ADA</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Transactions:</span>
                      <span className="font-medium">{agent.transaction_count || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Wallet:</span>
                      <span className="font-mono text-xs">{agent.wallet_address?.slice(0, 12)}...</span>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => onToggleAutonomous(agent.agent_id, !agent.autonomous_mode)}
                      className={`flex-1 flex items-center justify-center gap-1 py-2 px-3 rounded-lg text-sm font-medium transition-colors ${
                        agent.autonomous_mode
                          ? 'bg-red-100 text-red-700 hover:bg-red-200'
                          : 'bg-green-100 text-green-700 hover:bg-green-200'
                      }`}
                    >
                      {agent.autonomous_mode ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
                      {agent.autonomous_mode ? 'Pause' : 'Start'}
                    </button>
                    <button
                      onClick={() => setSelectedAgent(agent)}
                      className="px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-sm transition-colors"
                    >
                      <Settings className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Agent Activity Log */}
        <div className="bg-black rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Activity className="w-4 h-4 text-purple-400" />
            <h4 className="text-purple-400 font-medium">Agent Activity Log</h4>
            <div className="flex items-center gap-1 ml-auto">
              <TrendingUp className="w-3 h-3 text-purple-400" />
              <span className="text-purple-400 text-xs">Real-time</span>
            </div>
          </div>
          
          <div className="h-48 overflow-y-auto font-mono text-sm">
            {agentLogs.length === 0 ? (
              <div className="text-gray-500">
                No agent activity yet...
                <br />
                Create and activate agents to see autonomous behavior.
              </div>
            ) : (
              <div className="space-y-1">
                {agentLogs.slice(-20).map((log, index) => (
                  <div key={index} className="flex gap-2">
                    <span className="text-gray-500 text-xs whitespace-nowrap">
                      [{log.timestamp}]
                    </span>
                    <span className="text-purple-400 text-xs whitespace-nowrap">
                      {log.agentId}:
                    </span>
                    <span className={`${
                      log.type === 'autonomous' 
                        ? 'text-green-400' 
                        : log.type === 'error' 
                          ? 'text-red-400' 
                          : 'text-blue-400'
                    }`}>
                      {log.activity}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Agent Statistics */}
        {agents.length > 0 && (
          <div className="mt-6 grid grid-cols-3 gap-4">
            <div className="bg-purple-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">{agents.length}</div>
              <div className="text-sm text-purple-700">Total Agents</div>
            </div>
            <div className="bg-green-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-600">
                {agents.filter(a => a.autonomous_mode).length}
              </div>
              <div className="text-sm text-green-700">Autonomous</div>
            </div>
            <div className="bg-blue-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">
                {agents.reduce((sum, agent) => sum + (agent.transaction_count || 0), 0)}
              </div>
              <div className="text-sm text-blue-700">Transactions</div>
            </div>
          </div>
        )}
      </div>

      {/* Agent Details Modal */}
      {selectedAgent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="font-bold text-lg mb-4">Agent Details</h3>
            
            <div className="space-y-3 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Agent ID</label>
                <div className="px-3 py-2 bg-gray-100 rounded-lg font-mono text-sm">
                  {selectedAgent.agent_id}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Wallet Address</label>
                <div className="px-3 py-2 bg-gray-100 rounded-lg font-mono text-xs break-all">
                  {selectedAgent.wallet_address}
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Balance</label>
                  <div className="px-3 py-2 bg-gray-100 rounded-lg font-medium">
                    {selectedAgent.balance.toFixed(2)} ADA
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Mode</label>
                  <div className={`px-3 py-2 rounded-lg text-sm font-medium ${
                    selectedAgent.autonomous_mode 
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}>
                    {selectedAgent.autonomous_mode ? 'Autonomous' : 'Manual'}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={() => setSelectedAgent(null)}
                className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors"
              >
                Close
              </button>
              <button
                onClick={() => {
                  onToggleAutonomous(selectedAgent.agent_id, !selectedAgent.autonomous_mode)
                  setSelectedAgent(null)
                }}
                className={`flex-1 px-4 py-2 rounded-lg font-medium transition-colors ${
                  selectedAgent.autonomous_mode
                    ? 'bg-red-600 hover:bg-red-700 text-white'
                    : 'bg-green-600 hover:bg-green-700 text-white'
                }`}
              >
                {selectedAgent.autonomous_mode ? 'Disable Auto' : 'Enable Auto'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}