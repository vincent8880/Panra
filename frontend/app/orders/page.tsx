'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { positionsApi, Position, usersApi } from 'lib/api'
import { TopNav } from 'components/TopNav'

export default function OrdersPage() {
  const router = useRouter()
  const [positions, setPositions] = useState<Position[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        await usersApi.getMe()
        const positionsData = await positionsApi.getAll().catch(() => [])
        setPositions(positionsData.filter(p => 
          parseFloat(p.yes_shares) > 0 || parseFloat(p.no_shares) > 0
        ))
      } catch (err: any) {
        if (err?.response?.status === 401 || err?.response?.status === 403) {
          router.push('/login?next=/orders')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [router])

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    })
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-pm-bg-primary">
        <TopNav />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-pm-text-secondary">Loading...</div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-pm-bg-primary">
      <TopNav />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-2xl font-semibold text-pm-text-primary mb-6">Portfolio</h1>

        {/* Positions only - no individual order records */}
        <div className="space-y-4">
            {positions.length === 0 ? (
              <div className="bg-pm-bg-card border border-pm-border rounded-lg p-8 text-center">
                <p className="text-pm-text-secondary mb-4">No open positions</p>
                <Link href="/" className="text-pm-blue hover:text-pm-blue/80 font-medium">
                  Browse markets →
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {positions.map((position) => (
                  <div
                    key={position.id}
                    className="bg-pm-bg-card border border-pm-border rounded-lg p-4"
                  >
                    <Link
                      href={`/markets/${position.market_slug}`}
                      className="text-sm font-semibold text-pm-text-primary hover:text-pm-blue mb-3 block"
                    >
                      {position.market_title}
                    </Link>
                    <div className="grid grid-cols-2 gap-4">
                      {parseFloat(position.yes_shares) > 0 && (
                        <div className="bg-pm-green/10 border border-pm-green/30 rounded-lg p-3">
                          <div className="text-xs text-pm-text-secondary mb-1">YES Shares</div>
                          <div className="text-lg font-semibold text-pm-green">
                            {parseFloat(position.yes_shares).toFixed(2)}
                          </div>
                          <div className="text-xs text-pm-text-secondary mt-1">
                            Avg: {(parseFloat(position.yes_avg_cost) * 100).toFixed(1)}%
                          </div>
                          {position.yes_price != null && (
                            <div className="text-xs mt-1">
                              Now: {(parseFloat(position.yes_price) * 100).toFixed(1)}%
                              {(() => {
                                const pnl = (parseFloat(position.yes_price) - parseFloat(position.yes_avg_cost)) * parseFloat(position.yes_shares)
                                const pnlPct = parseFloat(position.yes_avg_cost) > 0
                                  ? ((parseFloat(position.yes_price) - parseFloat(position.yes_avg_cost)) / parseFloat(position.yes_avg_cost) * 100)
                                  : 0
                                return (
                                  <span className={pnl >= 0 ? 'text-pm-green' : 'text-pm-red'}>
                                    {' '}({pnl >= 0 ? '+' : ''}{(pnl * 100).toFixed(1)} pts, {pnl >= 0 ? '+' : ''}{pnlPct.toFixed(1)}%)
                                  </span>
                                )
                              })()}
                            </div>
                          )}
                        </div>
                      )}
                      {parseFloat(position.no_shares) > 0 && (
                        <div className="bg-pm-red/10 border border-pm-red/30 rounded-lg p-3">
                          <div className="text-xs text-pm-text-secondary mb-1">NO Shares</div>
                          <div className="text-lg font-semibold text-pm-red">
                            {parseFloat(position.no_shares).toFixed(2)}
                          </div>
                          <div className="text-xs text-pm-text-secondary mt-1">
                            Avg: {(parseFloat(position.no_avg_cost) * 100).toFixed(1)}%
                          </div>
                          {position.no_price != null && (
                            <div className="text-xs mt-1">
                              Now: {(parseFloat(position.no_price) * 100).toFixed(1)}%
                              {(() => {
                                const pnl = (parseFloat(position.no_price) - parseFloat(position.no_avg_cost)) * parseFloat(position.no_shares)
                                const pnlPct = parseFloat(position.no_avg_cost) > 0
                                  ? ((parseFloat(position.no_price) - parseFloat(position.no_avg_cost)) / parseFloat(position.no_avg_cost) * 100)
                                  : 0
                                return (
                                  <span className={pnl >= 0 ? 'text-pm-green' : 'text-pm-red'}>
                                    {' '}({pnl >= 0 ? '+' : ''}{(pnl * 100).toFixed(1)} pts, {pnl >= 0 ? '+' : ''}{pnlPct.toFixed(1)}%)
                                  </span>
                                )
                              })()}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                    <div className="text-xs text-pm-text-secondary mt-2">
                      Updated: {formatDate(position.updated_at)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
      </div>
    </main>
  )
}


