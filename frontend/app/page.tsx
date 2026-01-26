import Link from 'next/link'
import { MarketList } from 'components/MarketList'
import PanraLogo from 'components/PanraIcon'
import { WhatsAppBanner } from 'components/WhatsAppBanner'

export default function Home() {
  return (
    <main className="min-h-screen bg-pm-bg-primary">
      {/* WhatsApp Community Banner */}
      <WhatsAppBanner 
        groupLink={process.env.NEXT_PUBLIC_WHATSAPP_GROUP_LINK || 'https://chat.whatsapp.com/YOUR_GROUP_LINK'}
        groupName="Panra Trading Community"
      />
      
      {/* Header - Polymarket style */}
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
              <button className="btn-primary text-sm">
                Connect Wallet
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Market List */}
        <MarketList />
      </section>
    </main>
  )
}








