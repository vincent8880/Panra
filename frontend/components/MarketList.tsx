'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { marketsApi, Market } from '../lib/api'
import { formatDistanceToNow } from 'date-fns'

export function MarketList() {
  const [markets, setMarkets] = useState<Market[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<'all' | 'open'>('all')

  useEffect(() => {
    const fetchMarkets = async () => {
      try {
        const params = filter === 'open' ? { status: 'open' } : {}
        const data = await marketsApi.getAll(params)
        setMarkets(data)
      } catch (error) {
        console.error('Error fetching markets:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchMarkets()
  }, [filter])

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-pm-blue"></div>
      </div>
    )
  }

  return (
    <div>
      {/* Filter Tabs - Polymarket style */}
      <div className="flex space-x-1 mb-8 border-b border-pm-border">
        <button
          onClick={() => setFilter('all')}
          className={`pb-4 px-4 font-medium transition-colors ${
            filter === 'all'
              ? 'text-pm-text-primary border-b-2 border-pm-blue'
              : 'text-pm-text-secondary hover:text-pm-text-primary'
          }`}
        >
          All Markets
        </button>
        <button
          onClick={() => setFilter('open')}
          className={`pb-4 px-4 font-medium transition-colors ${
            filter === 'open'
              ? 'text-pm-text-primary border-b-2 border-pm-blue'
              : 'text-pm-text-secondary hover:text-pm-text-primary'
          }`}
        >
          Open Markets
        </button>
      </div>

      {/* Market Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {markets.map((market) => (
          <Link 
            key={market.id} 
            href={`/markets/${market.slug}`}
            className="block w-full no-underline"
          >
            <div className="market-card group w-full h-full">
              {/* Market Image */}
              {market.image_url && (
                <div className="w-full h-40 mb-4 rounded-lg overflow-hidden bg-pm-bg-secondary">
                  <img
                    src={market.image_url}
                    alt={market.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}

              {/* Market Title */}
              <h3 className="text-base font-semibold text-pm-text-primary mb-2 line-clamp-2 leading-tight">
                {market.title}
              </h3>

              {/* Market Question */}
              <p className="text-sm text-pm-text-secondary mb-4 line-clamp-2">
                {market.question}
              </p>

              {/* Price Indicators - Polymarket style */}
              <div className="flex items-center gap-3 mb-4">
                <div className="flex-1">
                  <div className="text-xs text-pm-text-secondary mb-1.5 font-medium">YES</div>
                  <div className="price-indicator price-yes">
                    {(parseFloat(market.yes_price) * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="flex-1">
                  <div className="text-xs text-pm-text-secondary mb-1.5 font-medium">NO</div>
                  <div className="price-indicator price-no">
                    {(parseFloat(market.no_price) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Market Stats - Polymarket style with prominent volume */}
              <div className="pt-4 border-t border-pm-border space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-pm-text-secondary">Volume</span>
                  <span className="text-sm font-semibold text-pm-text-primary">
                    {parseFloat(market.total_volume).toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs text-pm-text-secondary">
                  <span>Ends</span>
                  <span>{formatDistanceToNow(new Date(market.end_date), { addSuffix: true })}</span>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {markets.length === 0 && (
        <div className="text-center py-12">
          <p className="text-pm-text-secondary">No markets found</p>
        </div>
      )}
    </div>
  )
}








