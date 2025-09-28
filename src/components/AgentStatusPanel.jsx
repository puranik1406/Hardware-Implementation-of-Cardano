import { useState, useEffect } from 'react'
import { masumiService } from '../services/MasumiNetworkService'
import { Network, Users, Activity, Globe, Zap, TrendingUp } from 'lucide-react'

const AgentStatusPanel = ({ network, paymentHistory }) => {
  const [networkStats, setNetworkStats] = useState({
    latency: 0,
    throughput: 0,
    activeAgents: 0,
    blockHeight: 0
  })

  useEffect(() => {
    // Subscribe to network stats events from Masumi service (WebSocket-driven)
    const handler = (evt) => {
      const stats = evt.detail || {}
      setNetworkStats((prev) => ({
        latency: Number(stats.latency ?? prev.latency),
        throughput: Number(stats.throughput ?? prev.throughput),
        activeAgents: Number(stats.activeAgents ?? network.agents.length ?? prev.activeAgents),
        blockHeight: Number(stats.blockHeight ?? prev.blockHeight)
      }))
    }

    window.addEventListener('masumi:networkStats', handler)

    // Fallback: fetch stats once on mount and then every 10s if no WS updates
    let intervalId
    const primeStats = async () => {
      try {
        const stats = await masumiService.getNetworkStats()
        handler({ detail: stats })
      } catch {}
    }
    primeStats()
    intervalId = setInterval(primeStats, 10000)

    return () => {
      window.removeEventListener('masumi:networkStats', handler)
      if (intervalId) clearInterval(intervalId)
    }
  }, [network.agents.length])

  const getNetworkStatusColor = () => {
    return network.connected ? 'text-green-400' : 'text-red-400'
  }

  const getLatencyColor = (latency) => {
    if (latency < 30) return 'text-green-400'
    if (latency < 50) return 'text-yellow-400'
    return 'text-red-400'
  }

  return (
    <div className="card p-6">
      {/* Simple Network Status */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
            <Network className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="heading-2">Network Status</h3>
            <div className={`flex items-center gap-2 ${getNetworkStatusColor()}`}>
              <div className={`status-dot ${network.connected ? 'online' : 'error'}`}></div>
              <span className="font-medium">{network.connected ? 'Connected' : 'Disconnected'}</span>
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-small text-muted">Network ID</div>
          <div className="font-mono font-bold text-blue-600">
            {network.connected ? 'masumi-preprod-live' : 'disconnected'}
          </div>
        </div>
      </div>

      {/* Simple Network Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="card p-4 text-center">
          <Activity className="w-8 h-8 mx-auto mb-2 text-blue-500" />
          <div className={`text-2xl font-bold mb-1 ${getLatencyColor(networkStats.latency)}`}>
            {networkStats.latency}ms
          </div>
          <div className="text-small text-muted">Latency</div>
        </div>

        <div className="card p-4 text-center">
          <TrendingUp className="w-8 h-8 mx-auto mb-2 text-green-500" />
          <div className="text-2xl font-bold text-green-600 mb-1">
            {networkStats.throughput}
          </div>
          <div className="text-small text-muted">TPS</div>
        </div>

        <div className="card p-4 text-center">
          <Users className="w-8 h-8 mx-auto mb-2 text-purple-500" />
          <div className="text-2xl font-bold text-purple-600 mb-1">
            {networkStats.activeAgents}
          </div>
          <div className="text-small text-muted">Agents</div>
        </div>

        <div className="card p-4 text-center">
          <Globe className="w-8 h-8 mx-auto mb-2 text-orange-500" />
          <div className="text-2xl font-bold text-orange-600 mb-1">
            {networkStats.blockHeight}
          </div>
          <div className="text-small text-muted">Block Height</div>
        </div>
      </div>

      {/* Arduino Agents */}
      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <h4 className="heading-3 mb-3">Connected Arduino Devices</h4>
          {network.agents.length === 0 ? (
            <div className="card p-6 text-center text-gray-500">
              <Users className="w-12 h-12 mx-auto mb-3" />
              <p>No devices connected</p>
            </div>
          ) : (
            <div className="space-y-3">
              {network.agents.map((agent) => (
                <div key={agent.id} className="card p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className={`status-dot ${agent.status === 'online' ? 'online' : 'error'}`}></div>
                      <div>
                        <div className="font-medium">{agent.id}</div>
                        <div className="text-small text-muted capitalize">{agent.type} device</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-blue-600">{agent.balance} ADA</div>
                      <div className="text-small text-muted">Balance</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div>
          <h4 className="heading-3 mb-3">Recent Activity</h4>
          {paymentHistory.length === 0 ? (
            <div className="card p-6 text-center text-gray-500">
              <Activity className="w-12 h-12 mx-auto mb-3" />
              <p>No recent activity</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {paymentHistory.slice(-3).reverse().map((payment) => (
                <div key={payment.id} className="card p-4 border-l-4 border-blue-500">
                  <div className="text-small text-muted mb-1">
                    {new Date(payment.timestamp).toLocaleTimeString()}
                  </div>
                  <div className="font-medium">
                    Payment: <span className="text-blue-600 font-bold">{payment.amount} ADA</span>
                  </div>
                  <div className="text-small text-muted">
                    {payment.from} → {payment.to}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AgentStatusPanel