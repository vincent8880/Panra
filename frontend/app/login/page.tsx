'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { authApi } from 'lib/api'

export default function LoginPage() {
  const router = useRouter()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await authApi.login({ username: identifier, email: identifier, password })
      router.push('/')
    } catch (err: any) {
      const detail = err?.response?.data?.detail || 'Login failed. Check your details and try again.'
      setError(detail)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-pm-bg-primary px-4">
      <div className="w-full max-w-md bg-pm-bg-secondary border border-pm-border rounded-xl p-6 shadow-lg">
        <h1 className="text-xl font-semibold mb-1 text-center">Login to Panra</h1>
        <p className="text-sm text-pm-text-secondary mb-6 text-center">
          Use your username or email and password.
        </p>

        {error && (
          <div className="mb-4 text-sm text-red-400 bg-red-950/40 border border-red-800 rounded px-3 py-2">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm mb-1">Username or Email</label>
            <input
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              className="w-full px-3 py-2 rounded-md bg-pm-bg-primary border border-pm-border text-sm focus:outline-none focus:ring-1 focus:ring-pm-accent"
              required
            />
          </div>

          <div>
            <label className="block text-sm mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 rounded-md bg-pm-bg-primary border border-pm-border text-sm focus:outline-none focus:ring-1 focus:ring-pm-accent"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full btn-primary py-2 text-sm disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? 'Logging in…' : 'Login'}
          </button>
        </form>

        <p className="mt-4 text-xs text-center text-pm-text-secondary">
          Don&apos;t have an account?{' '}
          <Link href="/signup" className="text-pm-accent hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </main>
  )
}