import { Analytics } from '@vercel/analytics/next'
import type { Metadata, Viewport } from 'next'
import { Plus_Jakarta_Sans } from 'next/font/google'
import './globals.css'

const fontSans = Plus_Jakarta_Sans({
  subsets: ['latin'],
  variable: '--font-sans',
})

export const metadata: Metadata = {
  title: 'CloudSpawn — Autonomous RAG & Kubernetes AI Knowledge Orchestrator',
  description: 'Serverless FAISS vector indexing and EKS Kubernetes cluster orchestration for grounded AI workloads.',
  icons: {
    icon: '/icon.svg',
  },
}

export const viewport: Viewport = {
  colorScheme: 'dark',
  themeColor: '#0b0d14',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className={`dark ${fontSans.variable}`}>
      <body className="font-sans antialiased bg-[#07090e] text-slate-100 selection:bg-indigo-500/30 selection:text-indigo-200">
        {children}
        {process.env.NODE_ENV === 'production' && <Analytics />}
      </body>
    </html>
  )
}
