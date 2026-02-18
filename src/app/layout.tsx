import type { Metadata } from 'next'
import '@/styles/tailwind.css'

export const metadata: Metadata = {
  title: 'Todo App',
  description: 'A simple todo application',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://rsms.me/" />
        <link rel="stylesheet" href="https://rsms.me/inter/inter.css" />
      </head>
      <body className="bg-white dark:bg-zinc-900">
        {children}
      </body>
    </html>
  )
}
