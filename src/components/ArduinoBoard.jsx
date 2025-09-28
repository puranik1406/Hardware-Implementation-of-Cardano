import { useState, useEffect } from 'react'
import { Play, Square, Wifi, WifiOff, Cpu, Zap, DollarSign } from 'lucide-react'
import CodeEditor from './CodeEditor'

const ArduinoBoard = ({ arduino, onCodeChange, onRun }) => {
  const [isRunning, setIsRunning] = useState(false)
  const [serialOutput, setSerialOutput] = useState([])
  const [pins, setPins] = useState({
    digital: Array(14).fill(false),
    analog: Array(6).fill(0)
  })

  useEffect(() => {
    if (arduino.status === 'running' || arduino.status === 'listening') {
      setIsRunning(true)
      simulateSerialOutput()
    } else {
      setIsRunning(false)
    }
  }, [arduino.status])

  const simulateSerialOutput = () => {
    // TODO: Integrate with backend to stream actual Arduino serial output and Masumi API events
    // Example:
    // fetch(`/api/arduino/${arduino.id}/serial`).then(...)
    // or use WebSocket for real-time output
  }

  const getStatusColor = () => {
    switch (arduino.status) {
      case 'running': return 'text-green-400'
      case 'sending': return 'text-blue-400'
      case 'receiving': return 'text-yellow-400'
      case 'listening': return 'text-purple-400'
      default: return 'text-gray-400'
    }
  }

  const getStatusIcon = () => {
    switch (arduino.status) {
      case 'running': return <Zap className="w-4 h-4 animate-pulse" />
      case 'sending': return <DollarSign className="w-4 h-4 animate-bounce" />
      case 'receiving': return <DollarSign className="w-4 h-4 animate-pulse" />
      case 'listening': return <Wifi className="w-4 h-4 animate-pulse" />
      default: return <Cpu className="w-4 h-4" />
    }
  }

  const togglePin = (type, index) => {
    setPins(prev => ({
      ...prev,
      [type]: type === 'digital' 
        ? prev[type].map((pin, i) => i === index ? !pin : pin)
        : prev[type].map((pin, i) => i === index ? (pin + 256) % 1024 : pin)
    }))
  }

  return (
    <div className="arduino-card p-6">
      {/* Simple Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-green-500 rounded-lg flex items-center justify-center">
            <Cpu className="w-6 h-6 text-white" />
          </div>
          <div>
            <h3 className="heading-3 mb-1">{arduino.name}</h3>
            <div className="flex items-center gap-2">
              <div className={`status-dot ${arduino.status === 'idle' ? 'online' : arduino.status === 'running' ? 'warning' : 'online'}`}></div>
              <span className="text-small text-muted capitalize">{arduino.status || 'Ready'}</span>
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-small text-muted">Balance</div>
          <div className="text-xl font-bold text-green-600">{arduino.balance} ADA</div>
        </div>
      </div>

      {/* Simplified Pin Interface */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h4 className="heading-3">Arduino Pins</h4>
          <button
            onClick={onRun}
            disabled={isRunning}
            className={`btn ${isRunning ? 'btn-secondary' : 'btn-arduino'}`}
          >
            {isRunning ? (
              <>
                <Square className="w-4 h-4" />
                Running...
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Upload & Run
              </>
            )}
          </button>
        </div>

        {/* Digital Pins - Clean Grid */}
        <div className="mb-4">
          <div className="text-small font-medium text-gray-700 mb-2">Digital Pins (0-13)</div>
          <div className="grid grid-cols-7 gap-2">
            {pins.digital.map((pin, index) => (
              <button
                key={index}
                onClick={() => togglePin('digital', index)}
                className={`w-10 h-10 rounded-lg text-xs font-mono font-bold transition-all ${
                  pin 
                    ? 'bg-red-500 text-white shadow-md' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border border-gray-300'
                }`}
                title={`Pin ${index}: ${pin ? 'HIGH' : 'LOW'}`}
              >
                {index}
              </button>
            ))}
          </div>
        </div>

        {/* Analog Pins - Clean Grid */}
        <div>
          <div className="text-small font-medium text-gray-700 mb-2">Analog Pins (A0-A5)</div>
          <div className="grid grid-cols-6 gap-2">
            {pins.analog.map((pin, index) => (
              <button
                key={index}
                onClick={() => togglePin('analog', index)}
                className={`w-12 h-10 rounded-lg text-xs font-mono font-bold transition-all ${
                  pin > 0 
                    ? 'bg-orange-500 text-white shadow-md' 
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border border-gray-300'
                }`}
                title={`Pin A${index}: ${pin}`}
              >
                A{index}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Simple Code Display */}
      <div className="mb-6">
        <h4 className="heading-3 mb-3">Arduino Code</h4>
        <div className="bg-gray-50 border border-gray-200 rounded-lg overflow-hidden">
          <div className="bg-gray-100 px-4 py-2 border-b border-gray-200 flex items-center justify-between">
            <span className="text-small font-mono text-gray-600">{arduino.id}.ino</span>
            <span className="text-small text-muted">Arduino C++</span>
          </div>
          <div className="h-48 overflow-y-auto">
            <CodeEditor
              code={arduino.code}
              onChange={onCodeChange}
              language="cpp"
            />
          </div>
        </div>
      </div>

      {/* Simple Serial Output */}
      <div className="mb-4">
        <h4 className="heading-3 mb-3">Serial Monitor</h4>
        <div className="bg-gray-900 text-green-400 p-4 rounded-lg font-mono text-sm h-32 overflow-y-auto">
          {serialOutput.length === 0 ? (
            <div className="text-gray-500">Ready for output...</div>
          ) : (
            serialOutput.map((line, index) => (
              <div key={index} className="mb-1">
                <span className="text-gray-500">[{new Date().toLocaleTimeString()}]</span> {line}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Status Display */}
      {arduino.lastAction && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-blue-500" />
            <div>
              <div className="text-small text-muted">Last Activity</div>
              <div className="font-medium text-gray-900">{arduino.lastAction}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ArduinoBoard