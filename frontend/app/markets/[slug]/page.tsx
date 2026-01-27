"use client"

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { marketsApi, Market } from 'lib/api'
import { formatDistanceToNow } from 'date-fns'
import { TradeModal } from 'components/TradeModal'
import PanraLogo from 'components/PanraIcon'

export default function MarketDetailPage() {
  const params = useParams()
  const [market, setMarket] = useState<Market | null>(null)
  const [loading, setLoading] = useState(true)
  const [tradeOpen, setTradeOpen] = useState(false)
  const [tradeSide, setTradeSide] = useState<'yes' | 'no'>('yes')

  useEffect(() => {
    const fetchMarket = async () => {
      try {
        const data = await marketsApi.getBySlug(params.slug as string)
        setMarket(data)
      } catch (error) {
        console.error('Error fetching market:', error)
      } finally {
        setLoading(false)
      }
    }

    if (params.slug) {
      fetchMarket()
    }
  }, [params.slug])

  if (loading) {
    return (
      <div className="min-h-screen bg-pm-bg-primary flex items-center justify-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-pm-blue"></div>
      </div>
    )
  }

  if (!market) {
    return (
      <div className="min-h-screen bg-pm-bg-primary flex items-center justify-center">
        <p className="text-pm-text-secondary">Market not found</p>
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-pm-bg-primary">
      {/* Header - Polymarket style */}
      <header className="bg-pm-bg-primary border-b border-pm-border sticky top-0 z-50 backdrop-blur-sm bg-pm-bg-primary/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-8">
              <Link href="/" className="flex items-center">
                <PanraLogo size={28} />
              </Link>
              <nav className="hidden md:flex items-center space-x-6">
                <Link href="/" className="nav-link">
                  Markets
                </Link>
                <Link href="/leaderboard" className="nav-link">
                  Leaderboard
                </Link>
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/login" className="btn-primary text-sm">
                Login / Sign up
              </Link>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <Link 
          href="/" 
          className="inline-flex items-center text-pm-text-secondary hover:text-pm-text-primary mb-6 transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to Markets
        </Link>

        {/* Market Header */}
        <div className="bg-pm-bg-card rounded-lg border border-pm-border p-6 mb-6">
          {market.image_url && (
            <div className="w-full h-64 mb-6 rounded-lg overflow-hidden bg-pm-bg-secondary">
              <img
                src={market.image_url}
                alt={market.title}
                className="w-full h-full object-cover"
              />
            </div>
          )}

          <h1 className="text-3xl font-bold text-pm-text-primary mb-4">
            {market.title}
          </h1>

          <p className="text-lg text-pm-text-secondary mb-6">
            {market.question}
          </p>

          <div className="flex items-center space-x-6 text-sm text-pm-text-secondary">
            <span>Created by {market.created_by_username}</span>
            <span>•</span>
            <span>Ends {formatDistanceToNow(new Date(market.end_date), { addSuffix: true })}</span>
            <span>•</span>
            <span>Volume: KES {parseFloat(market.total_volume).toLocaleString()}</span>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: current prices & trade buttons */}
          <div className="lg:col-span-2 space-y-6">
            {/* Price & trade actions - Polymarket style */}
            <div className="bg-pm-bg-card rounded-lg border border-pm-border p-6">
              <h2 className="text-lg font-semibold text-pm-text-primary mb-4">
                Trade this market
              </h2>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => {
                    setTradeSide('yes')
                    setTradeOpen(true)
                  }}
                  className="flex flex-col items-start justify-between p-4 rounded-xl border border-pm-border bg-pm-bg-secondary hover:bg-pm-bg-card transition-colors"
                >
                  <span className="text-xs text-pm-text-secondary font-medium mb-1">
                    YES
                  </span>
                  <span className="text-2xl font-bold text-pm-green mb-1">
                    {(parseFloat(market.yes_price) * 100).toFixed(1)}%
                  </span>
                  <span className="text-[11px] text-pm-text-secondary">
                    Tap to buy YES shares
                  </span>
                </button>
                <button
                  onClick={() => {
                    setTradeSide('no')
                    setTradeOpen(true)
                  }}
                  className="flex flex-col items-start justify-between p-4 rounded-xl border border-pm-border bg-pm-bg-secondary hover:bg-pm-bg-card transition-colors"
                >
                  <span className="text-xs text-pm-text-secondary font-medium mb-1">
                    NO
                  </span>
                  <span className="text-2xl font-bold text-pm-red mb-1">
                    {(parseFloat(market.no_price) * 100).toFixed(1)}%
                  </span>
                  <span className="text-[11px] text-pm-text-secondary">
                    Tap to buy NO shares
                  </span>
                </button>
              </div>
            </div>
          </div>

          {/* Market Info - Right Column */}
          <div className="space-y-6">
            {/* Market Details */}
            <div className="bg-pm-bg-card rounded-lg border border-pm-border p-6">
              <h2 className="text-lg font-semibold text-pm-text-primary mb-4">
                Market Details
              </h2>
              <dl className="space-y-3">
                <div>
                  <dt className="text-sm text-pm-text-secondary">Status</dt>
                  <dd className="text-sm font-medium text-pm-text-primary capitalize">
                    {market.status}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-pm-text-secondary">Category</dt>
                  <dd className="text-sm font-medium text-pm-text-primary">
                    {market.category || 'Uncategorized'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-pm-text-secondary">Total Volume</dt>
                  <dd className="text-sm font-medium text-pm-text-primary">
                    KES {parseFloat(market.total_volume).toLocaleString()}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-pm-text-secondary">Total Liquidity</dt>
                  <dd className="text-sm font-medium text-pm-text-primary">
                    KES {parseFloat(market.total_liquidity).toLocaleString()}
                  </dd>
                </div>
              </dl>
            </div>
          </div>
        </div>
      </div>

      {/* Trading modal (bottom sheet on mobile) */}
      <TradeModal
        market={market}
        isOpen={tradeOpen}
        initialSide={tradeSide}
        onClose={() => setTradeOpen(false)}
      />
    </main>
  )
}








