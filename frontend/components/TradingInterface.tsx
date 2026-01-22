'use client'

import { useState } from 'react'
import { Market, ordersApi } from 'lib/api'

interface TradingInterfaceProps {
  market: Market
}

export function TradingInterface({ market }: TradingInterfaceProps) {
  const [side, setSide] = useState<'yes' | 'no'>('yes')
  const [orderType, setOrderType] = useState<'limit' | 'market'>('limit')
  const [price, setPrice] = useState('')
  const [quantity, setQuantity] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!price || !quantity) {
      alert('Please fill in all fields')
      return
    }

    setLoading(true)
    try {
      await ordersApi.create({
        market: market.id,
        side,
        order_type: orderType,
        price,
        quantity,
      })
      alert('Order placed successfully!')
      setPrice('')
      setQuantity('')
    } catch (error: any) {
      alert(`Error: ${error.response?.data?.detail || 'Failed to place order'}`)
    } finally {
      setLoading(false)
    }
  }

  const currentPrice = side === 'yes' 
    ? parseFloat(market.yes_price) 
    : parseFloat(market.no_price)

  return (
    <div className="bg-pm-bg-card rounded-lg border border-pm-border p-6">
      <h2 className="text-lg font-semibold text-pm-text-primary mb-6">
        Place Order
      </h2>

      {/* Side Selection - Polymarket style */}
      <div className="grid grid-cols-2 gap-3 mb-6">
        <button
          onClick={() => setSide('yes')}
          className={`py-3 px-4 rounded-lg font-semibold transition-all ${
            side === 'yes'
              ? 'bg-pm-green text-white shadow-lg shadow-pm-green/20'
              : 'bg-pm-bg-secondary text-pm-text-secondary hover:bg-pm-bg-card border border-pm-border'
          }`}
        >
          YES {(parseFloat(market.yes_price) * 100).toFixed(2)}%
        </button>
        <button
          onClick={() => setSide('no')}
          className={`py-3 px-4 rounded-lg font-semibold transition-all ${
            side === 'no'
              ? 'bg-pm-red text-white shadow-lg shadow-pm-red/20'
              : 'bg-pm-bg-secondary text-pm-text-secondary hover:bg-pm-bg-card border border-pm-border'
          }`}
        >
          NO {(parseFloat(market.no_price) * 100).toFixed(2)}%
        </button>
      </div>

      {/* Order Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Order Type */}
        <div>
          <label className="block text-sm font-medium text-pm-text-secondary mb-2">
            Order Type
          </label>
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setOrderType('limit')}
              className={`py-2.5 px-4 rounded-lg font-medium transition-colors ${
                orderType === 'limit'
                  ? 'bg-pm-blue text-white'
                  : 'bg-pm-bg-secondary text-pm-text-secondary hover:bg-pm-bg-card border border-pm-border'
              }`}
            >
              Limit
            </button>
            <button
              type="button"
              onClick={() => setOrderType('market')}
              className={`py-2.5 px-4 rounded-lg font-medium transition-colors ${
                orderType === 'market'
                  ? 'bg-pm-blue text-white'
                  : 'bg-pm-bg-secondary text-pm-text-secondary hover:bg-pm-bg-card border border-pm-border'
              }`}
            >
              Market
            </button>
          </div>
        </div>

        {/* Price */}
        {orderType === 'limit' && (
          <div>
            <label className="block text-sm font-medium text-pm-text-secondary mb-2">
              Price (KES)
            </label>
            <input
              type="number"
              step="0.0001"
              min="0"
              max="1"
              value={price}
              onChange={(e) => setPrice(e.target.value)}
              placeholder={currentPrice.toFixed(4)}
              className="pm-input w-full"
              required
            />
            <p className="mt-1 text-xs text-pm-text-secondary">
              Current price: {(currentPrice * 100).toFixed(2)}%
            </p>
          </div>
        )}

        {/* Quantity */}
        <div>
          <label className="block text-sm font-medium text-pm-text-secondary mb-2">
            Quantity (Shares)
          </label>
          <div className="space-y-2">
            <input
              type="number"
              step="0.01"
              min="0.01"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              placeholder="0.00"
              className="pm-input w-full"
              required
            />
            
            {/* Quick Increment Buttons - Polymarket style */}
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                onClick={() => {
                  const current = parseFloat(quantity) || 0
                  setQuantity((current + 10).toFixed(2))
                }}
                className="px-3 py-1.5 text-xs font-medium bg-pm-bg-secondary hover:bg-pm-bg-card text-pm-text-secondary hover:text-pm-text-primary border border-pm-border rounded transition-colors"
              >
                +10
              </button>
              <button
                type="button"
                onClick={() => {
                  const current = parseFloat(quantity) || 0
                  setQuantity((current + 100).toFixed(2))
                }}
                className="px-3 py-1.5 text-xs font-medium bg-pm-bg-secondary hover:bg-pm-bg-card text-pm-text-secondary hover:text-pm-text-primary border border-pm-border rounded transition-colors"
              >
                +100
              </button>
              <button
                type="button"
                onClick={() => {
                  const current = parseFloat(quantity) || 0
                  setQuantity((current + 1000).toFixed(2))
                }}
                className="px-3 py-1.5 text-xs font-medium bg-pm-bg-secondary hover:bg-pm-bg-card text-pm-text-secondary hover:text-pm-text-primary border border-pm-border rounded transition-colors"
              >
                +1000
              </button>
              {orderType === 'limit' && price && (
                <>
                  <button
                    type="button"
                    onClick={() => {
                      const current = parseFloat(quantity) || 0
                      const newQty = (current * 1.25).toFixed(2)
                      setQuantity(newQty)
                    }}
                    className="px-3 py-1.5 text-xs font-medium bg-pm-bg-secondary hover:bg-pm-bg-card text-pm-text-secondary hover:text-pm-text-primary border border-pm-border rounded transition-colors"
                  >
                    +25%
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      const current = parseFloat(quantity) || 0
                      const newQty = (current * 1.5).toFixed(2)
                      setQuantity(newQty)
                    }}
                    className="px-3 py-1.5 text-xs font-medium bg-pm-bg-secondary hover:bg-pm-bg-card text-pm-text-secondary hover:text-pm-text-primary border border-pm-border rounded transition-colors"
                  >
                    +50%
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      const current = parseFloat(quantity) || 0
                      const newQty = (current * 2).toFixed(2)
                      setQuantity(newQty)
                    }}
                    className="px-3 py-1.5 text-xs font-medium bg-pm-bg-secondary hover:bg-pm-bg-card text-pm-text-secondary hover:text-pm-text-primary border border-pm-border rounded transition-colors"
                  >
                    +100%
                  </button>
                  <button
                    type="button"
                    onClick={async () => {
                      try {
                        // Try to fetch user credits to calculate max
                        const { usersApi } = await import('lib/api')
                        const creditsData = await usersApi.getCredits()
                        const availableCredits = creditsData.credits
                        const priceNum = parseFloat(price)
                        if (priceNum > 0 && availableCredits > 0) {
                          const maxQty = Math.floor((availableCredits / priceNum) * 100) / 100
                          setQuantity(maxQty.toFixed(2))
                        } else {
                          // Fallback: set a high quantity
                          setQuantity('10000.00')
                        }
                      } catch (error) {
                        // If not authenticated or API fails, set high quantity
                        setQuantity('10000.00')
                      }
                    }}
                    className="px-3 py-1.5 text-xs font-semibold bg-pm-blue hover:bg-pm-blue-dark text-white border border-pm-blue rounded transition-colors"
                  >
                    Max
                  </button>
                </>
              )}
              {orderType === 'market' && (
                <button
                  type="button"
                  onClick={async () => {
                    try {
                      // For market orders, use current price
                      const { usersApi } = await import('../lib/api')
                      const creditsData = await usersApi.getCredits()
                      const availableCredits = creditsData.credits
                      const priceNum = currentPrice
                      if (priceNum > 0 && availableCredits > 0) {
                        const maxQty = Math.floor((availableCredits / priceNum) * 100) / 100
                        setQuantity(maxQty.toFixed(2))
                      } else {
                        setQuantity('10000.00')
                      }
                    } catch (error) {
                      setQuantity('10000.00')
                    }
                  }}
                  className="px-3 py-1.5 text-xs font-semibold bg-pm-blue hover:bg-pm-blue-dark text-white border border-pm-blue rounded transition-colors"
                >
                  Max
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Total Cost */}
        {price && quantity && orderType === 'limit' && (
          <div className="p-4 bg-pm-bg-secondary rounded-lg border border-pm-border">
            <div className="flex justify-between text-sm">
              <span className="text-pm-text-secondary">Total Cost:</span>
              <span className="font-semibold text-pm-text-primary">
                KES {(parseFloat(price) * parseFloat(quantity)).toFixed(2)}
              </span>
            </div>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className={`w-full py-3 px-4 rounded-lg font-semibold transition-colors ${
            side === 'yes'
              ? 'bg-pm-green hover:bg-pm-green-dark text-white'
              : 'bg-pm-red hover:bg-pm-red-dark text-white'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {loading ? 'Placing Order...' : `Buy ${side.toUpperCase()}`}
        </button>
      </form>
    </div>
  )
}








