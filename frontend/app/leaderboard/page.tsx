'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import PanraLogo from 'components/PanraIcon'

interface LeaderboardUser {
  id: number
  username: string
  total_points: number
  weekly_points: number
  monthly_points: number
  win_streak: number
  accuracy_percentage: number
  roi_percentage: number
  rank?: number
}

interface LeaderboardData {
  results: LeaderboardUser[]
  type: 'all-time' | 'weekly' | 'monthly'
}

export default function LeaderboardPage() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [type, setType] = useState<'all-time' | 'weekly' | 'monthly'>('all-time')

  useEffect(() => {
    const fetchLeaderboard = async () => {
      setLoading(true)
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/auth/leaderboard/${type === 'all-time' ? 'all-time' : type}/`
        )
        if (response.ok) {
          const data = await response.json()
          // Add rank numbers
          const resultsWithRank = data.results.map((user: LeaderboardUser, index: number) => ({
            ...user,
            rank: index + 1
          }))
          setLeaderboard({ ...data, results: resultsWithRank })
        }
      } catch (error) {
        console.error('Error fetching leaderboard:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchLeaderboard()
  }, [type])

  const getMedal = (rank: number) => {
    if (rank === 1) return '🥇'
    if (rank === 2) return '🥈'
    if (rank === 3) return '🥉'
    return null
  }

  const getPointsField = () => {
    if (type === 'weekly') return 'weekly_points'
    if (type === 'monthly') return 'monthly_points'
    return 'total_points'
  }

  return (
    <main className="min-h-screen bg-pm-bg-primary">
      {/* Header */}
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
                <Link href="/leaderboard" className="nav-link font-semibold text-pm-blue">
                  Leaderboard
                </Link>
              </nav>
            </div>
            <div className="flex items-center space-x-4">
              <button className="btn-primary text-sm">
                Connect Wallet
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-pm-text-primary mb-2">Leaderboard</h1>
          <p className="text-pm-text-secondary">Compete with the best traders</p>
        </div>

        {/* Type Selector */}
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setType('all-time')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              type === 'all-time'
                ? 'bg-pm-blue text-white'
                : 'bg-pm-bg-card text-pm-text-secondary hover:bg-pm-bg-secondary border border-pm-border'
            }`}
          >
            All-Time
          </button>
          <button
            onClick={() => setType('weekly')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              type === 'weekly'
                ? 'bg-pm-blue text-white'
                : 'bg-pm-bg-card text-pm-text-secondary hover:bg-pm-bg-secondary border border-pm-border'
            }`}
          >
            Weekly
          </button>
          <button
            onClick={() => setType('monthly')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              type === 'monthly'
                ? 'bg-pm-blue text-white'
                : 'bg-pm-bg-card text-pm-text-secondary hover:bg-pm-bg-secondary border border-pm-border'
            }`}
          >
            Monthly
          </button>
        </div>

        {/* Leaderboard Table */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-pm-blue"></div>
          </div>
        ) : leaderboard && leaderboard.results.length > 0 ? (
          <div className="bg-pm-bg-card rounded-lg border border-pm-border overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-pm-bg-secondary border-b border-pm-border">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-pm-text-secondary uppercase tracking-wider">
                      Rank
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-pm-text-secondary uppercase tracking-wider">
                      User
                    </th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-pm-text-secondary uppercase tracking-wider">
                      Points
                    </th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-pm-text-secondary uppercase tracking-wider">
                      Win Rate
                    </th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-pm-text-secondary uppercase tracking-wider">
                      ROI
                    </th>
                    <th className="px-6 py-4 text-right text-xs font-semibold text-pm-text-secondary uppercase tracking-wider">
                      Streak
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-pm-border">
                  {leaderboard.results.map((user) => {
                    const medal = user.rank ? getMedal(user.rank) : null
                    const points = user[getPointsField() as keyof LeaderboardUser] as number
                    
                    return (
                      <tr
                        key={user.id}
                        className="hover:bg-pm-bg-secondary transition-colors"
                      >
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center gap-2">
                            {medal ? (
                              <span className="text-2xl">{medal}</span>
                            ) : (
                              <span className="text-pm-text-secondary font-medium">
                                #{user.rank}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center">
                            <div className="flex-shrink-0 h-10 w-10 rounded-full bg-pm-blue/20 flex items-center justify-center mr-3">
                              <span className="text-pm-blue font-semibold">
                                {user.username.charAt(0).toUpperCase()}
                              </span>
                            </div>
                            <div>
                              <div className="text-sm font-medium text-pm-text-primary">
                                {user.username}
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <div className="text-sm font-semibold text-pm-text-primary">
                            {points.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <div className="text-sm text-pm-text-primary">
                            {user.accuracy_percentage.toFixed(1)}%
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          <div className={`text-sm font-medium ${
                            user.roi_percentage >= 0 ? 'text-pm-green' : 'text-red-500'
                          }`}>
                            {user.roi_percentage >= 0 ? '+' : ''}{user.roi_percentage.toFixed(1)}%
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-right">
                          {user.win_streak > 0 ? (
                            <div className="flex items-center justify-end gap-1">
                              <span className="text-sm font-medium text-pm-text-primary">
                                {user.win_streak}
                              </span>
                              <span className="text-orange-500">🔥</span>
                            </div>
                          ) : (
                            <span className="text-sm text-pm-text-secondary">-</span>
                          )}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-pm-text-secondary">No rankings yet. Be the first to trade!</p>
          </div>
        )}
      </section>
    </main>
  )
}







