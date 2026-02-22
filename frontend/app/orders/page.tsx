'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { ordersApi, positionsApi, Order, Position, usersApi } from 'lib/api'
import { TopNav } from 'components/TopNav'

export default function OrdersPage() {
  const router = useRouter()
  const [orders, setOrders] = useState<Order[]>([])
  const [positions, setPositions] = useState<Position[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'orders' | 'positions'>('orders')

  useEffect(() => {
    const fetchData = async () => {
      try {
        await usersApi.getMe()
        const [ordersData, positionsData] = await Promise.all([
          ordersApi.getAll().catch(() => []),
          positionsApi.getAll().catch(() => [])
        ])
        setOrders(Array.isArray(ordersData) ? ordersData : [])
        setPositions((positionsData || []).filter((p: Position) =>
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

  const handleCancelOrder = async (orderId: number) => {
    if (!confirm('Cancel this order? Unfilled credits will be refunded.')) return
    try {
      await ordersApi.cancel(orderId)
      const updated = await ordersApi.getAll()
      setOrders(Array.isArray(updated) ? updated : [])
      window.dispatchEvent(new CustomEvent('creditsUpdated', { detail: {} }))
    } catch (err: any) {
      alert(err?.response?.data?.error || 'Failed to cancel order')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'filled': return 'text-green-400'
      case 'pending': return 'text-yellow-400'
      case 'partial': return 'text-blue-400'
      case 'cancelled': return 'text-gray-400'
      default: return 'text-pm-text-secondary'
    }
  }

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

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-pm-border">
          <button
            onClick={() => setActiveTab('orders')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === 'orders'
                ? 'text-pm-text-primary border-b-2 border-pm-blue'
                : 'text-pm-text-secondary hover:text-pm-text-primary'
            }`}
          >
            My Orders ({orders.length})
          </button>
          <button
            onClick={() => setActiveTab('positions')}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === 'positions'
                ? 'text-pm-text-primary border-b-2 border-pm-blue'
                : 'text-pm-text-secondary hover:text-pm-text-primary'
            }`}
          >
            Positions ({positions.length})
          </button>
        </div>

        {/* My Orders Tab */}
        {activeTab === 'orders' && (
          <div className="space-y-4">
            {orders.length === 0 ? (
              <div className="bg-pm-bg-card border border-pm-border rounded-lg p-8 text-center">
                <p className="text-pm-text-secondary mb-4">No orders yet</p>
                <Link href="/" className="text-pm-blue hover:text-pm-blue/80 font-medium">
                  Browse markets →
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {orders.map((order) => (
                  <div
                    key={order.id}
                    className="bg-pm-bg-card border border-pm-border rounded-lg p-4"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="text-sm font-semibold text-pm-text-primary mb-1">
                          {order.market_title}
                        </div>
                        <div className="flex items-center gap-4 text-xs text-pm-text-secondary mt-2">
                          <span className={`font-medium ${order.side === 'yes' ? 'text-pm-green' : 'text-pm-red'}`}>
                            {order.side.toUpperCase()}
                          </span>
                          <span>{(parseFloat(order.price) * 100).toFixed(1)}%</span>
                          <span>{parseFloat(order.quantity).toFixed(2)} shares</span>
                          <span className={getStatusColor(order.status)}>
                            {order.status}
                          </span>
                        </div>
                        {order.status === 'partial' && (
                          <div className="text-xs text-pm-text-secondary mt-1">
                            Filled: {parseFloat(order.filled_quantity).toFixed(2)} / {parseFloat(order.quantity).toFixed(2)}
                          </div>
                        )}
                        <div className="text-xs text-pm-text-secondary mt-1">
                          Cost: {(parseFloat(order.price) * parseFloat(order.quantity)).toFixed(2)} pts
                        </div>
                      </div>
                      {(order.status === 'pending' || order.status === 'partial') && (
                        <button
                          onClick={() => handleCancelOrder(order.id)}
                          className="px-3 py-1.5 text-xs font-medium text-red-400 hover:text-red-300 border border-red-800/50 hover:border-red-700/50 rounded-md transition-colors"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Positions Tab */}
        {activeTab === 'positions' && (
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
                    <div className="text-sm font-semibold text-pm-text-primary mb-3">
                      {position.market_title}
                    </div>
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
        )}
      </div>
    </main>
  )
}


