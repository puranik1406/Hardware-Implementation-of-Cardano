import { useState, useEffect } from 'react'
import { CheckCircle, AlertCircle, ExternalLink } from 'lucide-react'

const TransactionNotification = ({ transaction, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 8000) // Auto close after 8 seconds
    return () => clearTimeout(timer)
  }, [onClose])

  if (!transaction) return null

  return (
    <div className="fixed top-4 right-4 bg-white border border-gray-200 rounded-lg shadow-lg p-4 max-w-md z-50">
      <div className="flex items-start gap-3">
        {transaction.success ? (
          <CheckCircle className="w-6 h-6 text-green-500 flex-shrink-0 mt-1" />
        ) : (
          <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0 mt-1" />
        )}
        
        <div className="flex-1 min-w-0">
          <div className="font-semibold text-gray-900 mb-1">
            {transaction.success ? 'Transaction Submitted!' : 'Transaction Failed'}
          </div>
          
          <div className="text-sm text-gray-600 mb-2">
            {transaction.amount} ADA from Arduino {transaction.fromAgentId?.includes('a') ? 'A' : 'B'} to Arduino {transaction.toAgentId?.includes('b') ? 'B' : 'A'}
          </div>

          {transaction.txHash && (
            <div className="space-y-2">
              <div className="text-xs text-gray-500">Transaction Hash:</div>
              <div className="font-mono text-xs bg-gray-50 p-2 rounded border break-all">
                {transaction.txHash}
              </div>
              
              {transaction.explorerUrl && (
                <a
                  href={transaction.explorerUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800"
                >
                  View on Cardano Explorer <ExternalLink className="w-3 h-3" />
                </a>
              )}
            </div>
          )}

          {transaction.type && (
            <div className="mt-2">
              <span className={`text-xs px-2 py-1 rounded ${
                transaction.type === 'real_cardano_transaction' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-orange-100 text-orange-800'
              }`}>
                {transaction.type === 'real_cardano_transaction' ? 'Live Blockchain Transaction' : 'Demo Transaction'}
              </span>
            </div>
          )}

          {transaction.note && (
            <div className="mt-2 text-xs text-gray-500 italic">
              {transaction.note}
            </div>
          )}
        </div>
        
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 flex-shrink-0"
        >
          <span className="sr-only">Close</span>
          ×
        </button>
      </div>
    </div>
  )
}

export default TransactionNotification