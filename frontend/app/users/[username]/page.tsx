'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { statsApi } from 'lib/api'
import type { UserStats } from 'lib/api'
import { TopNav } from 'components/TopNav'

export default function UserProfilePage() {
  const params = useParams()
  const username = typeof params.username === 'string' ? params.username : ''
  const [stats, setStats] = useState<UserStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!username) {
      setLoading(false)
      setError('Invalid username')
      return
    }
    const fetchStats = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await statsApi.getUserStatsByUsername(username)
        setStats(data)
      } catch (err: any) {
        if (err?.response?.status === 404) {
          setError('User not found')
        } else {
          setError('Failed to load profile')
        }
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [username])

  if (loading) {
    return (
      <main className="min-h-screen bg-pm-bg-primary">
        <TopNav />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 flex justify-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-pm-blue" />
        </div>
      </main>
    )
  }

  if (error || !stats) {
    return (
      <main className="min-h-screen bg-pm-bg-primary">
        <TopNav />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
          <p className="text-pm-text-secondary mb-4">{error || 'User not found'}</p>
          <Link href="/" className="text-pm-blue hover:text-pm-blue/80 font-medium">
            Back to Markets
          </Link>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-pm-bg-primary">
      <TopNav />

      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Profile Header */}
        <div className="bg-pm-bg-card rounded-lg border border-pm-border p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="h-20 w-20 rounded-full bg-pm-blue/20 flex items-center justify-center">
                <span className="text-3xl font-bold text-pm-blue">
                  {stats.user.username.charAt(0).toUpperCase()}
                </span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-pm-text-primary mb-1">
                  {stats.user.username}
                </h1>
                <p className="text-pm-text-secondary">
                  Rank #{stats.user.rank} • {stats.user.total_points.toLocaleString()} points
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-pm-text-secondary mb-1">Current Credits</div>
              <div className="text-2xl font-bold text-pm-text-primary">
                {stats.credits.current.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </div>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
          {/* Points Card */}
          <div className="bg-pm-bg-card rounded-lg border border-pm-border p-6">
            <h3 className="text-sm font-semibold text-pm-text-secondary uppercase tracking-wider mb-4">
              Points
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Total</span>
                <span className="text-lg font-bold text-pm-text-primary">
                  {stats.user.total_points.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Weekly</span>
                <span className="text-pm-text-primary font-medium">
                  {stats.user.weekly_points.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Monthly</span>
                <span className="text-pm-text-primary font-medium">
                  {stats.user.monthly_points.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </span>
              </div>
            </div>
          </div>

          {/* Trading Performance */}
          <div className="bg-pm-bg-card rounded-lg border border-pm-border p-6">
            <h3 className="text-sm font-semibold text-pm-text-secondary uppercase tracking-wider mb-4">
              Trading Performance
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Win Rate</span>
                <span className="text-lg font-bold text-pm-text-primary">
                  {stats.trading.accuracy_percentage.toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">ROI</span>
                <span className={`text-lg font-bold ${
                  stats.trading.roi_percentage >= 0 ? 'text-pm-green' : 'text-red-500'
                }`}>
                  {stats.trading.roi_percentage >= 0 ? '+' : ''}{stats.trading.roi_percentage.toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Markets Traded</span>
                <span className="text-pm-text-primary font-medium">
                  {stats.trading.total_markets_traded}
                </span>
              </div>
            </div>
          </div>

          {/* Win Streak */}
          <div className="bg-pm-bg-card rounded-lg border border-pm-border p-6">
            <h3 className="text-sm font-semibold text-pm-text-secondary uppercase tracking-wider mb-4">
              Streaks
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Current</span>
                <div className="flex items-center gap-2">
                  <span className="text-lg font-bold text-pm-text-primary">
                    {stats.trading.win_streak}
                  </span>
                  {stats.trading.win_streak > 0 && <span className="text-orange-500">🔥</span>}
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Best</span>
                <span className="text-pm-text-primary font-medium">
                  {stats.trading.best_win_streak}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Correct Predictions</span>
                <span className="text-pm-text-primary font-medium">
                  {stats.trading.markets_predicted_correctly}
                </span>
              </div>
            </div>
          </div>

          {/* Volume Stats */}
          <div className="bg-pm-bg-card rounded-lg border border-pm-border p-6">
            <h3 className="text-sm font-semibold text-pm-text-secondary uppercase tracking-wider mb-4">
              Volume
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Total Volume</span>
                <span className="text-pm-text-primary font-medium">
                  {stats.volume.total_volume_traded.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Total P&L</span>
                <span className={`font-medium ${
                  stats.volume.total_profit_loss >= 0 ? 'text-pm-green' : 'text-red-500'
                }`}>
                  {stats.volume.total_profit_loss >= 0 ? '+' : ''}
                  {stats.volume.total_profit_loss.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Unrealized P&L</span>
                <span className={`font-medium ${
                  stats.volume.unrealized_pnl >= 0 ? 'text-pm-green' : 'text-red-500'
                }`}>
                  {stats.volume.unrealized_pnl >= 0 ? '+' : ''}
                  {stats.volume.unrealized_pnl.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </span>
              </div>
            </div>
          </div>

          {/* Activity Stats */}
          <div className="bg-pm-bg-card rounded-lg border border-pm-border p-6">
            <h3 className="text-sm font-semibold text-pm-text-secondary uppercase tracking-wider mb-4">
              Activity
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Total Trades</span>
                <span className="text-pm-text-primary font-medium">
                  {stats.trading.total_trades}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Active Positions</span>
                <span className="text-pm-text-primary font-medium">
                  {stats.trading.active_positions}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Markets Traded</span>
                <span className="text-pm-text-primary font-medium">
                  {stats.trading.markets_traded}
                </span>
              </div>
            </div>
          </div>

          {/* Credits Info */}
          <div className="bg-pm-bg-card rounded-lg border border-pm-border p-6">
            <h3 className="text-sm font-semibold text-pm-text-secondary uppercase tracking-wider mb-4">
              Credits
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Current</span>
                <span className="text-pm-text-primary font-medium">
                  {stats.credits.current.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Stored</span>
                <span className="text-pm-text-primary font-medium">
                  {stats.credits.stored.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-pm-text-secondary">Max</span>
                <span className="text-pm-text-primary font-medium">
                  {stats.credits.max.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}

















