import Link from 'next/link'
import { TopNav } from 'components/TopNav'

export default function NotFound() {
  return (
    <main className="min-h-screen bg-pm-bg-primary">
      <TopNav />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center">
        <h1 className="text-6xl font-bold text-pm-text-primary mb-2">404</h1>
        <p className="text-xl text-pm-text-secondary mb-6">Page not found</p>
        <p className="text-pm-text-secondary mb-8 max-w-md mx-auto">
          The page you’re looking for doesn’t exist or has been moved.
        </p>
        <Link
          href="/"
          className="inline-flex items-center px-5 py-2.5 rounded-lg bg-pm-blue hover:bg-pm-blue/90 text-white font-medium transition-colors"
        >
          Back to Markets
        </Link>
      </div>
    </main>
  )
}
