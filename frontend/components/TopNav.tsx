'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import PanraLogo from 'components/PanraIcon'
import { usersApi, authApi, User } from 'lib/api'

export function TopNav() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const me = await usersApi.getMe()
        setUser(me)
      } catch {
        // not logged in, ignore
      } finally {
        setLoading(false)
      }
    }

    fetchUser()
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
            </nav>
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
              <Link href="/login" className="btn-primary text-sm">
                Login / Sign up
              </Link>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}





