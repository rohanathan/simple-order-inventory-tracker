import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Order Management System',
  description: 'Simple order placement system',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}