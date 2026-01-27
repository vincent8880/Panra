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
  const [orderType, setOrderType] = useState<'limit' | 'market'>('limit')
  const [price, setPrice] = useState('')
  const [quantity, setQuantity] = useState('')
  const [loading, setLoading] = useState(false)
  const [authRequired, setAuthRequired] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!isOpen) return null

  const currentPrice = side === 'yes'
    ? parseFloat(market.yes_price)
    : parseFloat(market.no_price)

  const resetState = () => {
    setOrderType('limit')
    setPrice('')
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

    if (!price && orderType === 'limit') {
      setError('Please enter a price.')
      return
    }
    if (!quantity) {
      setError('Please enter a quantity.')
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
        order_type: orderType,
        price: orderType === 'market' ? currentPrice.toFixed(4) : price,
        quantity,
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
                ? 'bg-pm-green text-white shadow-lg shadow-pm-green/20'
                : 'bg-pm-bg-secondary text-pm-text-secondary hover:bg-pm-bg-card border border-pm-border'
            }`}
          >
            YES {(parseFloat(market.yes_price) * 100).toFixed(1)}%
          </button>
          <button
            type="button"
            onClick={() => setSide('no')}
            className={`py-2 px-3 rounded-lg text-xs font-semibold transition-all ${
              side === 'no'
                ? 'bg-pm-red text-white shadow-lg shadow-pm-red/20'
                : 'bg-pm-bg-secondary text-pm-text-secondary hover:bg-pm-bg-card border border-pm-border'
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
        <form onSubmit={handleSubmit} className="space-y-3">
          {/* Order type */}
          <div>
            <div className="text-[11px] text-pm-text-secondary mb-1">Order type</div>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setOrderType('limit')}
                className={`py-1.5 rounded-md text-xs font-medium ${
                  orderType === 'limit'
                    ? 'bg-pm-blue text-white'
                    : 'bg-pm-bg-secondary text-pm-text-secondary border border-pm-border'
                }`}
              >
                Limit
              </button>
              <button
                type="button"
                onClick={() => setOrderType('market')}
                className={`py-1.5 rounded-md text-xs font-medium ${
                  orderType === 'market'
                    ? 'bg-pm-blue text-white'
                    : 'bg-pm-bg-secondary text-pm-text-secondary border border-pm-border'
                }`}
              >
                Market
              </button>
            </div>
          </div>

          {/* Price (for limit) */}
          {orderType === 'limit' && (
            <div>
              <div className="flex justify-between items-center mb-1">
                <label className="text-[11px] text-pm-text-secondary">Price (KES)</label>
                <span className="text-[11px] text-pm-text-secondary">
                  Current {(currentPrice * 100).toFixed(1)}%
                </span>
              </div>
              <input
                type="number"
                step="0.0001"
                min="0"
                max="1"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder={currentPrice.toFixed(4)}
                className="pm-input w-full text-xs"
              />
            </div>
          )}

          {/* Quantity + quick buttons */}
          <div>
            <label className="block text-[11px] text-pm-text-secondary mb-1">
              Quantity (shares)
            </label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              placeholder="0.00"
              className="pm-input w-full text-xs mb-1.5"
            />
            <div className="flex flex-wrap gap-1.5">
              {[10, 100, 1000].map((inc) => (
                <button
                  key={inc}
                  type="button"
                  onClick={() => {
                    const current = parseFloat(quantity) || 0
                    setQuantity((current + inc).toFixed(2))
                  }}
                  className="px-2 py-1 text-[11px] font-medium bg-pm-bg-secondary hover:bg-pm-bg-card text-pm-text-secondary hover:text-pm-text-primary border border-pm-border rounded"
                >
                  +{inc}
                </button>
              ))}
            </div>
          </div>

          {/* Cost summary */}
          {quantity && (orderType === 'market' || price) && (
            <div className="flex justify-between text-xs bg-pm-bg-secondary border border-pm-border rounded-md px-2 py-1.5">
              <span className="text-pm-text-secondary">Estimated cost</span>
              <span className="font-semibold text-pm-text-primary">
                KES {(
                  (orderType === 'market' ? currentPrice : parseFloat(price || '0')) *
                  parseFloat(quantity || '0')
                ).toFixed(2)}
              </span>
            </div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className={`w-full py-2.5 rounded-lg text-sm font-semibold mt-1 ${
              side === 'yes'
                ? 'bg-pm-green hover:bg-pm-green-dark text-white'
                : 'bg-pm-red hover:bg-pm-red-dark text-white'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {loading ? 'Placing order…' : `Buy ${side.toUpperCase()}`}
          </button>
        </form>
      </div>
    </div>
  )
}


