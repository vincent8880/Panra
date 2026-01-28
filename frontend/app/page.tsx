import { MarketList } from 'components/MarketList'
import { WhatsAppBanner } from 'components/WhatsAppBanner'
import { TopNav } from 'components/TopNav'

export default function Home() {
  return (
    <main className="min-h-screen bg-pm-bg-primary">
      {/* WhatsApp Community Banner */}
      <WhatsAppBanner 
        groupLink={process.env.NEXT_PUBLIC_WHATSAPP_GROUP_LINK || 'https://chat.whatsapp.com/YOUR_GROUP_LINK'}
        groupName="Panra Trading Community"
      />

      <TopNav />

      {/* Main Content */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Market List */}
        <MarketList />
      </section>
    </main>
  )
}








