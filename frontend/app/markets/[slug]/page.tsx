"use client"

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { marketsApi, Market } from 'lib/api'
import { formatDistanceToNow } from 'date-fns'
import { TradeModal } from 'components/TradeModal'
import { TopNav } from 'components/TopNav'

export default function MarketDetailPage() {
  const params = useParams()
  const [market, setMarket] = useState<Market | null>(null)
  const [loading, setLoading] = useState(true)
  const [tradeOpen, setTradeOpen] = useState(false)
  const [tradeSide, setTradeSide] = useState<'yes' | 'no'>('yes')

  useEffect(() => {
    const fetchMarket = async () => {
      if (!params.slug) {
        setLoading(false)
        return
      }

      const slug = params.slug as string

      try {
        const data = await marketsApi.getBySlug(slug)
        setMarket(data)
      } catch (error: any) {
        const asNumber = Number(slug)
        if (!Number.isNaN(asNumber)) {
          try {
            const data = await marketsApi.getById(asNumber)
            setMarket(data)
          } catch {
            setMarket(null)
          }
        } else {
          setMarket(null)
        }
      } finally {
        setLoading(false)
      }
    }

    fetchMarket()
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
      <TopNav />

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

          <p className="text-lg text-pm-text-secondary mb-4">
            {market.question}
          </p>

          {market.resolution_criteria && (
            <div className="mb-6 p-4 rounded-lg bg-pm-bg-secondary border border-pm-border">
              <p className="text-xs font-medium text-pm-text-secondary uppercase tracking-wide mb-1">Resolution criteria</p>
              <p className="text-sm text-pm-text-primary">
                This market resolves to YES when: {market.resolution_criteria}
              </p>
            </div>
          )}

          <div className="flex items-center space-x-6 text-sm text-pm-text-secondary">
            <span>Created by {market.created_by_username}</span>
            <span>•</span>
            <span>Ends {formatDistanceToNow(new Date(market.end_date), { addSuffix: true })}</span>
            <span>•</span>
            <span>Volume: {parseFloat(market.total_volume).toLocaleString()} pts</span>
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
                  className="group flex flex-col items-start justify-between p-4 rounded-xl border border-pm-green/30 bg-pm-green/10 transition-all duration-200 cursor-pointer hover:border-pm-green/60 hover:bg-pm-green/20"
                >
                  <span className="text-xs text-pm-green/70 font-medium mb-1 group-hover:text-pm-green transition-colors">
                    YES
                  </span>
                  <span className="text-2xl font-bold text-pm-green/70 group-hover:text-pm-green transition-colors">
                    {(parseFloat(market.yes_price) * 100).toFixed(1)}%
                  </span>
                  <span className="text-[11px] text-pm-text-secondary">
                    Tap to stake on YES
                  </span>
                </button>
                <button
                  onClick={() => {
                    setTradeSide('no')
                    setTradeOpen(true)
                  }}
                  className="group flex flex-col items-start justify-between p-4 rounded-xl border border-pm-red/30 bg-pm-red/10 transition-all duration-200 cursor-pointer hover:border-pm-red/60 hover:bg-pm-red/20"
                >
                  <span className="text-xs text-pm-red/70 font-medium mb-1 group-hover:text-pm-red transition-colors">
                    NO
                  </span>
                  <span className="text-2xl font-bold text-pm-red/70 group-hover:text-pm-red transition-colors">
                    {(parseFloat(market.no_price) * 100).toFixed(1)}%
                  </span>
                  <span className="text-[11px] text-pm-text-secondary">
                    Tap to stake on NO
                  </span>
                </button>
              </div>
            </div>
          </div>

          {/* Market Info + desktop trade ticket - Right Column */}
          <div className="space-y-6">
            {/* Desktop trade ticket */}
            <div className="hidden lg:block bg-pm-bg-card rounded-lg border border-pm-border p-6">
              <h2 className="text-lg font-semibold text-pm-text-primary mb-3">
                Trade ticket
              </h2>
              <p className="text-xs text-pm-text-secondary mb-3">
                Stake points on YES or NO. No real money, just points and leaderboard rank.
              </p>
              <div className="grid grid-cols-2 gap-2 mb-4">
                <button
                  onClick={() => {
                    setTradeSide('yes')
                    setTradeOpen(true)
                  }}
                  className="group py-2 px-3 rounded-lg text-xs font-semibold bg-pm-bg-secondary border border-pm-border text-left transition-all cursor-pointer hover:border-pm-green/50 hover:bg-pm-green/5 hover:shadow-md hover:shadow-pm-green/10"
                >
                  <div className="text-[11px] text-pm-text-secondary mb-0.5 group-hover:text-pm-green transition-colors">YES</div>
                  <div className="text-base font-bold text-pm-green/60 group-hover:text-pm-green transition-colors">
                    {(parseFloat(market.yes_price) * 100).toFixed(1)}% implied
                  </div>
                </button>
                <button
                  onClick={() => {
                    setTradeSide('no')
                    setTradeOpen(true)
                  }}
                  className="group py-2 px-3 rounded-lg text-xs font-semibold bg-pm-bg-secondary border border-pm-border text-left transition-all cursor-pointer hover:border-pm-red/50 hover:bg-pm-red/5 hover:shadow-md hover:shadow-pm-red/10"
                >
                  <div className="text-[11px] text-pm-text-secondary mb-0.5 group-hover:text-pm-red transition-colors">NO</div>
                  <div className="text-base font-bold text-pm-red/60 group-hover:text-pm-red transition-colors">
                    {(parseFloat(market.no_price) * 100).toFixed(1)}% implied
                  </div>
                </button>
              </div>
              <button
                onClick={() => setTradeOpen(true)}
                className="w-full btn-primary py-2 text-sm"
              >
                Open trade
              </button>
            </div>

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
                    {parseFloat(market.total_volume).toLocaleString()} pts
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-pm-text-secondary">Total Liquidity</dt>
                  <dd className="text-sm font-medium text-pm-text-primary">
                    {parseFloat(market.total_liquidity).toLocaleString()} pts
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








