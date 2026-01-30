'use client'

import { useState } from 'react'

interface WhatsAppBannerProps {
  groupLink?: string
  groupName?: string
}

export function WhatsAppBanner({ 
  groupLink = 'https://chat.whatsapp.com/YOUR_GROUP_LINK', 
  groupName = 'Panra Community' 
}: WhatsAppBannerProps) {
  const [dismissed, setDismissed] = useState(false)

  if (dismissed) return null

  return (
    <div className="bg-gradient-to-r from-green-600 to-green-500 text-white px-4 py-3 relative">
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="text-2xl">💬</div>
          <div>
            <div className="font-semibold">Join our WhatsApp Community!</div>
            <div className="text-sm text-green-100">
              Get updates, tips, and connect with other traders
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <a
            href={groupLink}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 bg-white text-green-600 font-semibold rounded-lg hover:bg-green-50 transition-colors text-sm"
          >
            Join Group
          </a>
          <button
            onClick={() => setDismissed(true)}
            className="text-white/80 hover:text-white transition-colors p-1"
            aria-label="Dismiss"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  )
}






