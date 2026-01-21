import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Panra - Prediction Markets',
  description: 'Predict and trade on events',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-pm-bg-primary text-pm-text-primary">{children}</body>
    </html>
  )
}








