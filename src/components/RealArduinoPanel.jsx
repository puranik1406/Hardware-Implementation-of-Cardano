import { useState, useEffect } from 'react'
import { Cpu, Wifi, Zap, Monitor, Bluetooth, Activity } from 'lucide-react'

export default function RealArduinoPanel({ 
  onSendCommand, 
  arduinoStatus, 
  esp32Status, 
  recentCommands = [],
  onConnectBoards 
}) {
  const [selectedBoard, setSelectedBoard] = useState('uno')
  const [command, setCommand] = useState('')
  const [serialOutput, setSerialOutput] = useState([])
  const [isConnecting, setIsConnecting] = useState(false)

  // Simulate real-time serial output
  useEffect(() => {
    const interval = setInterval(() => {
      if (arduinoStatus?.connected || esp32Status?.connected) {
        setSerialOutput(prev => [...prev.slice(-20), {
          timestamp: new Date().toLocaleTimeString(),
          board: Math.random() > 0.5 ? 'Arduino Uno' : 'ESP32',
          message: generateSerialMessage(),
          type: 'info'
        }])
      }
    }, 3000)

    return () => clearInterval(interval)
  }, [arduinoStatus?.connected, esp32Status?.connected])

  const generateSerialMessage = () => {
    const messages = [
      'HEARTBEAT: System OK',
      'WiFi signal: -45dBm',
      'Masumi agent status: Connected',
      'Button state: Released',
      'Temperature: 24.5°C',
      'Free memory: 2048 bytes',
      'Waiting for commands...'
    ]
    return messages[Math.floor(Math.random() * messages.length)]
  }

  const handleSendCommand = () => {
    if (!command.trim()) return

    onSendCommand(selectedBoard, command)
    
    // Add to serial output
    setSerialOutput(prev => [...prev.slice(-20), {
      timestamp: new Date().toLocaleTimeString(),
      board: selectedBoard === 'uno' ? 'Arduino Uno' : 'ESP32',
      message: `> ${command}`,
      type: 'command'
    }])
    
    setCommand('')
  }

  const handleConnectBoards = async () => {
    setIsConnecting(true)
    try {
      await onConnectBoards()
    } finally {
      setIsConnecting(false)
    }
  }

  const predefinedCommands = {
    uno: [
      'GET_STATUS',
      'SEND_PAYMENT:1.5:esp32_receiver',
      'HEARTBEAT',
      'SET_AGENT:arduino_sender:Payment Node'
    ],
    esp32: [
      'GET_STATUS',
      'SHOW_HISTORY',
      'DISPLAY_TX:demo123:2.5:SUCCESS',
      'SET_WIFI:YourNetwork:Password'
    ]
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
              <Cpu className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-white font-bold text-lg">Real Arduino Hardware</h3>
              <p className="text-blue-100 text-sm">Physical board communication</p>
            </div>
          </div>
          <button
            onClick={handleConnectBoards}
            disabled={isConnecting}
            className="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50"
          >
            <Bluetooth className="w-4 h-4" />
            {isConnecting ? 'Connecting...' : 'Detect Boards'}
          </button>
        </div>
      </div>

      <div className="p-6">
        {/* Board Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Arduino Uno Status */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Cpu className="w-5 h-5 text-blue-600" />
                <span className="font-medium">Arduino Uno</span>
              </div>
              <div className={`w-3 h-3 rounded-full ${arduinoStatus?.connected ? 'bg-green-500' : 'bg-red-500'}`} />
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Port:</span>
                <span className="font-mono">{arduinoStatus?.port || 'Not detected'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <span className={`font-medium ${arduinoStatus?.connected ? 'text-green-600' : 'text-red-600'}`}>
                  {arduinoStatus?.connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Agent ID:</span>
                <span className="font-mono text-xs">{arduinoStatus?.agentId || 'N/A'}</span>
              </div>
            </div>
          </div>

          {/* ESP32 Status */}
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Wifi className="w-5 h-5 text-purple-600" />
                <span className="font-medium">ESP32</span>
              </div>
              <div className={`w-3 h-3 rounded-full ${esp32Status?.connected ? 'bg-green-500' : 'bg-red-500'}`} />
            </div>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Port:</span>
                <span className="font-mono">{esp32Status?.port || 'Not detected'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">WiFi:</span>
                <span className={`font-medium ${esp32Status?.wifiConnected ? 'text-green-600' : 'text-red-600'}`}>
                  {esp32Status?.wifiConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">IP:</span>
                <span className="font-mono text-xs">{esp32Status?.ipAddress || 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Command Interface */}
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h4 className="font-medium mb-4 flex items-center gap-2">
            <Zap className="w-4 h-4" />
            Send Commands to Hardware
          </h4>
          
          {/* Board Selection */}
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setSelectedBoard('uno')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedBoard === 'uno'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              Arduino Uno
            </button>
            <button
              onClick={() => setSelectedBoard('esp32')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedBoard === 'esp32'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              ESP32
            </button>
          </div>

          {/* Command Input */}
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendCommand()}
              placeholder={`Enter command for ${selectedBoard === 'uno' ? 'Arduino Uno' : 'ESP32'}...`}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
            />
            <button
              onClick={handleSendCommand}
              disabled={!command.trim()}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
            >
              Send
            </button>
          </div>

          {/* Predefined Commands */}
          <div className="grid grid-cols-2 gap-2">
            {predefinedCommands[selectedBoard].map((cmd, index) => (
              <button
                key={index}
                onClick={() => setCommand(cmd)}
                className="text-left px-3 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-sm font-mono"
              >
                {cmd}
              </button>
            ))}
          </div>
        </div>

        {/* Serial Monitor */}
        <div className="bg-black rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Monitor className="w-4 h-4 text-green-400" />
            <h4 className="text-green-400 font-medium">Serial Monitor</h4>
            <div className="flex items-center gap-1 ml-auto">
              <Activity className="w-3 h-3 text-green-400" />
              <span className="text-green-400 text-xs">Live</span>
            </div>
          </div>
          
          <div className="h-64 overflow-y-auto font-mono text-sm">
            {serialOutput.length === 0 ? (
              <div className="text-gray-500">
                Waiting for Arduino communication...
                <br />
                Connect your Arduino Uno and ESP32 to see real-time output.
              </div>
            ) : (
              <div className="space-y-1">
                {serialOutput.map((line, index) => (
                  <div key={index} className="flex gap-2">
                    <span className="text-gray-500 text-xs whitespace-nowrap">
                      [{line.timestamp}]
                    </span>
                    <span className={`text-xs whitespace-nowrap ${
                      line.board === 'Arduino Uno' ? 'text-blue-400' : 'text-purple-400'
                    }`}>
                      {line.board}:
                    </span>
                    <span className={`${
                      line.type === 'command' 
                        ? 'text-yellow-400' 
                        : line.type === 'error' 
                          ? 'text-red-400' 
                          : 'text-green-400'
                    }`}>
                      {line.message}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Recent Commands */}
        {recentCommands.length > 0 && (
          <div className="mt-6">
            <h4 className="font-medium mb-3">Recent Commands</h4>
            <div className="space-y-2">
              {recentCommands.slice(-5).map((cmd, index) => (
                <div key={index} className="flex items-center justify-between bg-gray-50 rounded-lg px-4 py-2">
                  <div>
                    <span className="font-mono text-sm">{cmd.command}</span>
                    <span className="text-gray-500 text-xs ml-2">→ {cmd.board}</span>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    cmd.status === 'success' 
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                  }`}>
                    {cmd.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}