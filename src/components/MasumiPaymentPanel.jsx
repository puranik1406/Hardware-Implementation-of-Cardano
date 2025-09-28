import { useState } from 'react'
import { Send, ArrowLeftRight, History, Wallet, Zap, CheckCircle } from 'lucide-react'

const MasumiPaymentPanel = ({ arduinoA, arduinoB, paymentHistory, onSendPayment }) => {
  const [paymentAmount, setPaymentAmount] = useState(50)
  const [selectedSender, setSelectedSender] = useState('arduino_a')
  const [selectedReceiver, setSelectedReceiver] = useState('arduino_b')

  const handleSendPayment = () => {
    if (paymentAmount > 0) {
      onSendPayment(selectedSender, selectedReceiver, paymentAmount)
    }
  }

  const getArduinoData = (id) => {
    return id === 'arduino_a' ? arduinoA : arduinoB
  }

  return (
    <div className="masumi-card p-6">
      {/* Funding Information Panel */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <div className="flex items-start gap-3">
          <Wallet className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-medium text-blue-900 mb-1">Wallet Funding Required</h4>
            <p className="text-sm text-blue-700 mb-2">
              For real Cardano transactions, fund these wallets with testnet ADA:
            </p>
            <div className="space-y-1 text-xs">
              <div className="font-mono bg-blue-100 p-2 rounded border break-all">
                Arduino A: {arduinoA.walletAddress}
              </div>
              <div className="font-mono bg-blue-100 p-2 rounded border break-all">
                Arduino B: {arduinoB.walletAddress}
              </div>
            </div>
            <p className="text-xs text-blue-600 mt-2">
              💡 Use <a href="https://docs.cardano.org/cardano-testnet/tools/faucet/" target="_blank" className="underline">Cardano Testnet Faucet</a> to get free test ADA
            </p>
          </div>
        </div>
      </div>

      {/* Simple Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-blue-500 rounded-lg flex items-center justify-center">
          <Send className="w-6 h-6 text-white" />
        </div>
        <div>
          <h3 className="heading-2">Send Payment</h3>
          <p className="text-muted">Transfer ADA between Arduino devices</p>
        </div>
      </div>

      {/* Payment Form - Clean Layout */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="space-y-4">
          {/* From Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">From</label>
            <select
              value={selectedSender}
              onChange={(e) => setSelectedSender(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="arduino_a">{arduinoA.name} ({arduinoA.balance} ADA)</option>
              <option value="arduino_b">{arduinoB.name} ({arduinoB.balance} ADA)</option>
            </select>
          </div>

          {/* To Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">To</label>
            <select
              value={selectedReceiver}
              onChange={(e) => setSelectedReceiver(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="arduino_b">{arduinoB.name} ({arduinoB.balance} ADA)</option>
              <option value="arduino_a">{arduinoA.name} ({arduinoA.balance} ADA)</option>
            </select>
          </div>

          {/* Amount Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Amount (ADA)</label>
            <input
              type="number"
              value={paymentAmount}
              onChange={(e) => setPaymentAmount(Number(e.target.value))}
              min="1"
              max={getArduinoData(selectedSender).balance}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter amount"
            />
          </div>

          {/* Quick Amount Buttons */}
          <div className="flex gap-2">
            {[10, 25, 50, 100].map((amount) => (
              <button
                key={amount}
                onClick={() => setPaymentAmount(amount)}
                className="btn btn-secondary text-small"
              >
                {amount}
              </button>
            ))}
          </div>

          {/* Send Button */}
          <button
            onClick={handleSendPayment}
            disabled={paymentAmount <= 0 || paymentAmount > getArduinoData(selectedSender).balance || selectedSender === selectedReceiver}
            className="w-full btn btn-primary"
          >
            <ArrowLeftRight className="w-4 h-4" />
            Send {paymentAmount} ADA
          </button>
        </div>

        {/* Payment History */}
        <div>
          <h4 className="heading-3 mb-4">Recent Transactions</h4>
          
          {paymentHistory.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <History className="w-12 h-12 mx-auto mb-3" />
              <p>No transactions yet</p>
              <p className="text-small">Send your first payment to see history</p>
            </div>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {paymentHistory.slice(-5).reverse().map((payment) => (
                <div
                  key={payment.id}
                  className="card p-4 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <CheckCircle className={`w-4 h-4 ${payment.status === 'completed' ? 'text-green-500' : payment.status === 'failed' ? 'text-red-500' : 'text-yellow-500'}`} />
                      <span className="font-medium">
                        #{payment.id.slice(0, 8)}
                      </span>
                      {payment.status === 'completed' && (
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                          Confirmed
                        </span>
                      )}
                    </div>
                    <span className="text-small text-muted">
                      {new Date(payment.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-small">
                      <span className="text-blue-600 font-medium">{payment.from}</span>
                      <ArrowLeftRight className="w-3 h-3 inline mx-2 text-gray-400" />
                      <span className="text-green-600 font-medium">{payment.to}</span>
                    </div>
                    <div className="font-bold text-blue-600">
                      {payment.amount} ADA
                    </div>
                  </div>

                  {/* Transaction Hash and Explorer Link */}
                  {payment.txHash && (
                    <div className="mt-3 pt-3 border-t border-gray-100">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-xs text-gray-500 mb-1">Transaction Hash</div>
                          <div className="font-mono text-xs text-gray-700 bg-gray-50 px-2 py-1 rounded">
                            {payment.txHash.slice(0, 12)}...{payment.txHash.slice(-8)}
                          </div>
                        </div>
                        {payment.explorerUrl && (
                          <a
                            href={payment.explorerUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 transition-colors"
                          >
                            View on Explorer
                          </a>
                        )}
                      </div>
                      
                      {payment.type && (
                        <div className="mt-2">
                          <span className={`text-xs px-2 py-1 rounded ${
                            payment.type === 'real_cardano_transaction' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-orange-100 text-orange-800'
                          }`}>
                            {payment.type === 'real_cardano_transaction' ? 'Live Transaction' : 'Demo Transaction'}
                          </span>
                        </div>
                      )}
                      
                      {payment.note && (
                        <div className="mt-2 text-xs text-gray-600 italic">
                          {payment.note}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Simple Stats */}
          {paymentHistory.length > 0 && (
            <div className="mt-4 grid grid-cols-2 gap-4">
              <div className="card p-4 text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {paymentHistory.length}
                </div>
                <div className="text-small text-muted">Total Transactions</div>
              </div>
              <div className="card p-4 text-center">
                <div className="text-2xl font-bold text-green-600">
                  {paymentHistory.reduce((sum, p) => sum + p.amount, 0)}
                </div>
                <div className="text-small text-muted">Total Volume (ADA)</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MasumiPaymentPanel