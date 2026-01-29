'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { Market, ordersApi, usersApi } from 'lib/api'

interface TradeModalProps {
  market: Market
  isOpen: boolean
  initialSide: 'yes' | 'no'
  onClose: () => void
}

export function TradeModal({ market, isOpen, initialSide, onClose }: TradeModalProps) {
  const router = useRouter()
  const [side, setSide] = useState<'yes' | 'no'>(initialSide)
  const [quantity, setQuantity] = useState('')
  const [loading, setLoading] = useState(false)
  const [authRequired, setAuthRequired] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!isOpen) return null

  const currentPrice = side === 'yes'
    ? parseFloat(market.yes_price)
    : parseFloat(market.no_price)

  const resetState = () => {
    setQuantity('')
    setAuthRequired(false)
    setError(null)
  }

  const handleClose = () => {
    if (loading) return
    resetState()
    onClose()
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!quantity) {
      setError('Please enter how many points you want to stake.')
      return
    }

    const stakeAmount = parseFloat(quantity)
    if (isNaN(stakeAmount) || stakeAmount < 1) {
      setError('Minimum stake is 1 point.')
      return
    }

    setLoading(true)
    try {
      // Check if user is authenticated
      try {
        await usersApi.getMe()
      } catch (authErr: any) {
        const status = authErr?.response?.status
        if (status === 401 || status === 403) {
          setAuthRequired(true)
          setLoading(false)
          return
        }
        throw authErr
      }

      await ordersApi.create({
        market: market.id,
        side,
        order_type: 'market', // Always use market orders for simplicity
        price: currentPrice.toFixed(4),
        quantity: stakeAmount.toFixed(2),
      })
      resetState()
      onClose()
      alert('Order placed successfully!')
    } catch (err: any) {
      const detail = err?.response?.data?.detail || 'Failed to place order.'
      setError(detail)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/50">
      <div className="w-full sm:max-w-md bg-pm-bg-card border-t sm:border border-pm-border rounded-t-2xl sm:rounded-2xl p-4 sm:p-6 shadow-xl">
        {/* Drag handle for mobile */}
        <div className="flex justify-center mb-2 sm:hidden">
          <div className="h-1 w-10 rounded-full bg-pm-border" />
        </div>

        {/* Header */}
        <div className="flex items-start justify-between mb-3">
          <div>
            <p className="text-xs text-pm-text-secondary mb-1">Place order on</p>
            <h2 className="text-sm font-semibold text-pm-text-primary line-clamp-2">
              {market.title}
            </h2>
          </div>
          <button
            onClick={handleClose}
            className="p-1 text-pm-text-secondary hover:text-pm-text-primary"
          >
            <span className="sr-only">Close</span>
            ✕
          </button>
        </div>

        {/* Side selection */}
        <div className="grid grid-cols-2 gap-2 mb-4">
          <button
            type="button"
            onClick={() => setSide('yes')}
            className={`py-2 px-3 rounded-lg text-xs font-semibold transition-all ${
              side === 'yes'
                ? 'bg-pm-green text-white shadow-lg shadow-pm-green/20 border border-pm-green'
                : 'bg-pm-bg-secondary text-pm-green/60 border border-pm-border hover:border-pm-green/50 hover:bg-pm-green/5 hover:text-pm-green hover:shadow-md hover:shadow-pm-green/10'
            }`}
          >
            YES {(parseFloat(market.yes_price) * 100).toFixed(1)}%
          </button>
          <button
            type="button"
            onClick={() => setSide('no')}
            className={`py-2 px-3 rounded-lg text-xs font-semibold transition-all ${
              side === 'no'
                ? 'bg-pm-red text-white shadow-lg shadow-pm-red/20 border border-pm-red'
                : 'bg-pm-bg-secondary text-pm-red/60 border border-pm-border hover:border-pm-red/50 hover:bg-pm-red/5 hover:text-pm-red hover:shadow-md hover:shadow-pm-red/10'
            }`}
          >
            NO {(parseFloat(market.no_price) * 100).toFixed(1)}%
          </button>
        </div>

        {/* Auth required prompt */}
        {authRequired && (
          <div className="mb-3 border border-pm-border rounded-lg bg-pm-bg-secondary p-3 text-xs">
            <p className="text-pm-text-primary font-medium mb-1">
              You need an account to place trades.
            </p>
            <p className="text-pm-text-secondary mb-2">
              Login or create a free account to continue.
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => router.push('/login')}
                className="flex-1 py-1.5 px-2 rounded-md text-xs font-semibold bg-pm-blue text-white hover:bg-pm-blue-dark"
              >
                Login
              </button>
              <button
                onClick={() => router.push('/signup')}
                className="flex-1 py-1.5 px-2 rounded-md text-xs font-semibold bg-pm-bg-primary text-pm-text-primary border border-pm-border hover:bg-pm-bg-secondary"
              >
                Sign up
              </button>
            </div>
          </div>
        )}

        {error && (
          <div className="mb-3 text-xs text-red-400 bg-red-950/40 border border-red-800 rounded px-2 py-1.5">
            {error}
          </div>
        )}

        {/* Order form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Stake (points) + quick buttons */}
          <div>
            <label className="block text-sm font-medium text-pm-text-primary mb-2">
              How many points do you want to stake?
            </label>
            <input
              type="number"
              step="1"
              min="1"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              placeholder="Enter amount"
              className="pm-input w-full text-base py-3 mb-3"
            />
            <div className="flex flex-wrap gap-2">
              {[10, 50, 100, 500].map((amount) => (
                <button
                  key={amount}
                  type="button"
                  onClick={() => setQuantity(amount.toString())}
                  className="px-4 py-2 text-sm font-medium bg-pm-bg-secondary hover:bg-pm-bg-card text-pm-text-primary border border-pm-border rounded-lg transition-colors"
                >
                  {amount} pts
                </button>
              ))}
            </div>
          </div>

          {/* Cost summary */}
          {quantity && parseFloat(quantity) >= 1 && (
            <div className="bg-pm-bg-secondary border border-pm-border rounded-lg p-3 space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-pm-text-secondary">Price per share</span>
                <span className="font-medium text-pm-text-primary">
                  {(currentPrice * 100).toFixed(1)}% implied
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-pm-text-secondary">Total cost</span>
                <span className="font-semibold text-pm-text-primary">
                  {(currentPrice * parseFloat(quantity || '0')).toFixed(2)} pts
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-pm-text-secondary">Max payout (if correct)</span>
                <span className="font-semibold text-pm-text-primary">
                  {parseFloat(quantity || '0').toFixed(2)} pts
                </span>
              </div>
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={loading || !quantity || parseFloat(quantity) < 1}
            className={`w-full py-3 rounded-lg text-base font-semibold mt-2 ${
              side === 'yes'
                ? 'bg-pm-green hover:bg-pm-green-dark text-white'
                : 'bg-pm-red hover:bg-pm-red-dark text-white'
            } disabled:opacity-50 disabled:cursor-not-allowed transition-colors`}
          >
            {loading ? 'Placing order…' : `Stake ${side.toUpperCase()}`}
          </button>
        </form>
      </div>
    </div>
  )
}




