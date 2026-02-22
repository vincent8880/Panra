'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import PanraLogo from 'components/PanraIcon'
import { usersApi, authApi, User } from 'lib/api'

export function TopNav() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    const fetchUser = async () => {
      // Check if token exists first
      const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null
      console.log('🔍 [TopNav] Checking auth state, token exists:', token ? `Yes (${token.substring(0, 20)}...)` : 'No')
      
      try {
        console.log('🔍 [TopNav] Calling usersApi.getMe()...')
        const me = await usersApi.getMe()
        console.log('✅ [TopNav] User authenticated:', me.username)
        setUser(me)
      } catch (err: any) {
        console.error('❌ [TopNav] Not authenticated or error:', err?.response?.status, err?.response?.data)
        // not logged in, ignore
      } finally {
        setLoading(false)
      }
    }

    fetchUser()

    // Listen for credits updates (from TradeModal after a bet, or Portfolio)
    const handleCreditsUpdate = (e: Event) => {
      const customEvent = e as CustomEvent<{ current_credits?: number }>
      const newCredits = customEvent.detail?.current_credits
      if (typeof newCredits === 'number') {
        setUser(prev => prev ? { ...prev, current_credits: newCredits } : null)
      }
      fetchUser()
    }
    window.addEventListener('creditsUpdated', handleCreditsUpdate)

    // Refetch credits when user returns to tab (e.g. after selling/winning elsewhere)
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        fetchUser()
      }
    }
    document.addEventListener('visibilitychange', handleVisibilityChange)

    return () => {
      window.removeEventListener('creditsUpdated', handleCreditsUpdate)
      document.removeEventListener('visibilitychange', handleVisibilityChange)
    }
  }, [])

  const handleLogout = async () => {
    try {
      await authApi.logout()
      setUser(null)
      // Best-effort refresh of client state
      if (typeof window !== 'undefined') {
        window.location.href = '/'
      }
    } catch {
      // ignore for now
    }
  }

  const points = user?.current_credits ?? user?.credits ?? 0

  return (
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
              <Link href="/orders" className="nav-link">
                Portfolio
              </Link>
            </nav>
            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-pm-text-secondary hover:bg-pm-bg-secondary"
              aria-label="Toggle menu"
            >
              {mobileMenuOpen ? (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>

          <div className="flex items-center space-x-4">
            {!loading && user && (
              <>
                <div className="hidden sm:flex flex-col items-end text-right">
                  <span className="text-xs text-pm-text-secondary">Signed in as</span>
                  <span className="text-sm font-medium text-pm-text-primary">
                    {user.username}
                  </span>
                </div>
                <div className="px-3 py-1 rounded-full bg-pm-bg-secondary border border-pm-border text-xs font-medium">
                  {points.toLocaleString()} pts
                </div>
                <button
                  onClick={handleLogout}
                  className="text-xs text-pm-text-secondary hover:text-pm-text-primary underline-offset-2 hover:underline"
                >
                  Logout
                </button>
              </>
            )}
            {(!user && !loading) && (
              <div className="flex items-center gap-3">
                <Link 
                  href="/login" 
                  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-sm transition-all duration-200"
                >
                  Log In
                </Link>
                <Link 
                  href="/signup" 
                  className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm transition-all duration-200"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>
        </div>
        {/* Mobile menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-pm-border bg-pm-bg-primary">
            <nav className="flex flex-col py-4 px-4 space-y-1">
              <Link href="/" className="nav-link py-3" onClick={() => setMobileMenuOpen(false)}>
                Markets
              </Link>
              <Link href="/leaderboard" className="nav-link py-3" onClick={() => setMobileMenuOpen(false)}>
                Leaderboard
              </Link>
              <Link href="/orders" className="nav-link py-3" onClick={() => setMobileMenuOpen(false)}>
                Portfolio
              </Link>
            </nav>
          </div>
        )}
      </div>
    </header>
  )
}










