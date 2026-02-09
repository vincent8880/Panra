'use client'

import { useState, useEffect } from 'react'
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
  const [success, setSuccess] = useState<{ cost: number; quantity: number; side: 'yes' | 'no' } | null>(null)
  const [userCredits, setUserCredits] = useState<number | null>(null)

  const currentPrice = side === 'yes'
    ? parseFloat(market.yes_price)
    : parseFloat(market.no_price)

  const resetState = () => {
    setQuantity('')
    setAuthRequired(false)
    setError(null)
    setSuccess(null)
  }

  // Fetch user credits when modal opens
  useEffect(() => {
    if (isOpen && !success) {
      usersApi.getCredits().then(data => {
        setUserCredits(data.credits)
      }).catch(() => {
        // Ignore errors - user might not be logged in
      })
    }
  }, [isOpen, success])

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

      // Debug: Check token and request data
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
      const requestData: Parameters<typeof ordersApi.create>[0] = {
        market: market.id,
        side,
        order_type: 'market', // Always use market orders for simplicity
        price: currentPrice.toFixed(4),
        quantity: stakeAmount.toFixed(2),
      }
      console.log('🔍 [TradeModal] Token check:', token ? `Token exists (${token.substring(0, 20)}...)` : '❌ NO TOKEN FOUND')
      console.log('🔍 [TradeModal] Request data:', requestData)
      
      const order = await ordersApi.create(requestData)
      
      // Calculate cost
      const cost = currentPrice * stakeAmount
      
      // Show success state
      setSuccess({ cost, quantity: stakeAmount, side })
      
      // Refresh user credits
      try {
        const creditsData = await usersApi.getCredits()
        setUserCredits(creditsData.credits)
        // Trigger a page refresh to update TopNav
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new Event('creditsUpdated'))
        }
      } catch (err) {
        console.error('Failed to refresh credits:', err)
      }
      
      // Auto-close after 2 seconds
      setTimeout(() => {
        resetState()
        onClose()
      }, 2000)
    } catch (err: any) {
      const detail = err?.response?.data?.detail || 'Failed to place order.'
      setError(detail)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full sm:max-w-md bg-pm-bg-card border-t sm:border sm:rounded-xl border-pm-border p-5 sm:p-6 shadow-2xl">
        {/* Drag handle for mobile */}
        <div className="flex justify-center mb-4 sm:hidden">
          <div className="h-1 w-12 rounded-full bg-pm-border/60" />
        </div>

        {/* Header - Polymarket style: compact and clean */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1 pr-4">
            <p className="text-[11px] text-pm-text-secondary mb-0.5 uppercase tracking-wide">Place order on</p>
            <h2 className="text-sm font-semibold text-pm-text-primary leading-tight line-clamp-2">
              {market.title}
            </h2>
          </div>
          <button
            onClick={handleClose}
            className="flex-shrink-0 p-1.5 text-pm-text-secondary hover:text-pm-text-primary hover:bg-pm-bg-secondary rounded transition-colors"
          >
            <span className="sr-only">Close</span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Side selection - Polymarket style: larger, more prominent */}
        <div className="grid grid-cols-2 gap-2.5 mb-5">
          <button
            type="button"
            onClick={() => setSide('yes')}
            className={`py-3 px-4 rounded-lg text-sm font-semibold transition-all duration-200 ${
              side === 'yes'
                ? 'bg-pm-green text-white shadow-md shadow-pm-green/20'
                : 'bg-pm-bg-secondary text-pm-text-secondary border border-pm-border hover:bg-pm-green/10 hover:text-pm-green/80 hover:border-pm-green/40'
            }`}
          >
            YES {(parseFloat(market.yes_price) * 100).toFixed(1)}%
          </button>
          <button
            type="button"
            onClick={() => setSide('no')}
            className={`py-3 px-4 rounded-lg text-sm font-semibold transition-all duration-200 ${
              side === 'no'
                ? 'bg-pm-red text-white shadow-md shadow-pm-red/20'
                : 'bg-pm-bg-secondary text-pm-text-secondary border border-pm-border hover:bg-pm-red/10 hover:text-pm-red/80 hover:border-pm-red/40'
            }`}
          >
            NO {(parseFloat(market.no_price) * 100).toFixed(1)}%
          </button>
        </div>

        {/* Auth required prompt - Polymarket style: subtle */}
        {authRequired && (
          <div className="mb-4 border border-pm-border/50 rounded-lg bg-pm-bg-secondary/50 p-3 text-xs">
            <p className="text-pm-text-primary font-medium mb-1">
              You need an account to place trades.
            </p>
            <p className="text-pm-text-secondary mb-3 text-[11px]">
              Login or create a free account to continue.
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => router.push('/login')}
                className="flex-1 py-2 px-3 rounded-md text-xs font-semibold bg-blue-600 hover:bg-blue-500 text-white transition-all duration-200"
              >
                Login
              </button>
              <button
                onClick={() => router.push('/signup')}
                className="flex-1 py-2 px-3 rounded-md text-xs font-semibold bg-pm-bg-secondary hover:bg-pm-bg-card text-pm-text-primary border border-pm-border transition-all duration-200"
              >
                Sign up
              </button>
            </div>
          </div>
        )}

        {error && (
          <div className="mb-4 text-xs text-red-400 bg-red-950/30 border border-red-800/50 rounded-lg px-3 py-2">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-4 text-xs bg-green-950/30 border border-green-800/50 rounded-lg px-3 py-2">
            <div className="flex items-center gap-2 text-green-400">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <span className="font-semibold">Order placed successfully!</span>
            </div>
            <div className="mt-2 space-y-1 text-green-300/80">
              <div>Staked {success.quantity.toFixed(2)} pts on {success.side.toUpperCase()}</div>
              <div>Cost: {success.cost.toFixed(2)} pts</div>
              {userCredits !== null && (
                <div className="pt-1 border-t border-green-800/50">
                  Remaining: {userCredits.toFixed(2)} pts
                </div>
              )}
            </div>
          </div>
        )}

        {/* Order form - Polymarket style: clean and compact */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Stake (points) + quick buttons */}
          <div>
            <label className="block text-xs font-medium text-pm-text-secondary mb-2 uppercase tracking-wide">
              How many points do you want to stake?
            </label>
            <input
              type="number"
              step="1"
              min="1"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              placeholder="0"
              className="pm-input w-full text-lg font-semibold py-3.5 mb-3 text-center"
            />
            <div className="flex flex-wrap gap-2">
              {[10, 50, 100, 500].map((amount) => (
                <button
                  key={amount}
                  type="button"
                  onClick={() => setQuantity(amount.toString())}
                  className="px-3 py-1.5 text-xs font-medium bg-pm-bg-secondary hover:bg-pm-bg-card text-pm-text-primary border border-pm-border rounded-md transition-all duration-200"
                >
                  {amount} pts
                </button>
              ))}
            </div>
          </div>

          {/* Available points display */}
          {userCredits !== null && !success && (
            <div className="text-xs text-pm-text-secondary text-center">
              Available: <span className="font-semibold text-pm-text-primary">{userCredits.toFixed(2)} pts</span>
            </div>
          )}

          {/* Cost summary - Polymarket style: minimal and clean */}
          {quantity && parseFloat(quantity) >= 1 && !success && (
            <div className="bg-pm-bg-secondary/50 border border-pm-border/50 rounded-lg p-3 space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-pm-text-secondary">Price per share</span>
                <span className="font-medium text-pm-text-primary">
                  {(currentPrice * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-pm-text-secondary">Total cost</span>
                <span className="font-semibold text-pm-text-primary">
                  {(currentPrice * parseFloat(quantity || '0')).toFixed(2)} pts
                </span>
              </div>
              {userCredits !== null && (
                <div className="flex justify-between text-xs pt-1 border-t border-pm-border/30">
                  <span className="text-pm-text-secondary">After trade</span>
                  <span className="font-semibold text-pm-text-primary">
                    {(userCredits - (currentPrice * parseFloat(quantity || '0'))).toFixed(2)} pts
                  </span>
                </div>
              )}
              <div className="flex justify-between text-xs">
                <span className="text-pm-text-secondary">Max payout</span>
                <span className="font-semibold text-pm-text-primary">
                  {parseFloat(quantity || '0').toFixed(2)} pts
                </span>
              </div>
            </div>
          )}

          {/* Submit - Polymarket style: large, prominent button */}
          {!success && (
            <button
              type="submit"
              disabled={loading || !quantity || parseFloat(quantity) < 1}
              className={`w-full py-3.5 rounded-lg text-sm font-semibold mt-4 transition-all duration-200 ${
                side === 'yes'
                  ? 'bg-pm-green hover:bg-pm-green/90 text-white shadow-md shadow-pm-green/20'
                  : 'bg-pm-red hover:bg-pm-red/90 text-white shadow-md shadow-pm-red/20'
              } disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-opacity-50`}
            >
              {loading ? 'Placing order…' : `Stake ${side.toUpperCase()}`}
            </button>
          )}
        </form>
      </div>
    </div>
  )
}




