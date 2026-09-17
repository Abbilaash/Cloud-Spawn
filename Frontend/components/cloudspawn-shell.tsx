'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Activity, ArrowUpRight, Box, ChevronRight, CircleDot, Database, FileText, Gauge, Grid2X2, MessageSquare, Settings2, Upload, Workflow, X } from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'

const navigation = [
  { label: 'Overview', href: '/workspace', icon: Grid2X2 },
  { label: 'Documents', href: '/workspace/upload', icon: FileText },
  { label: 'Knowledge Base', href: '/workspace/knowledge-base', icon: Database },
  { label: 'Chat', href: '/workspace/chat', icon: MessageSquare },
]
const system = [
  { label: 'Processing', href: '/workspace/processing', icon: Activity },
  { label: 'Settings', href: '/workspace/settings', icon: Settings2 },
]

export function Brand({ light = false }: { light?: boolean }) {
  return <Link href="/" className={cn('flex items-center gap-2.5 font-semibold tracking-tight', light && 'text-white')}><span className="grid size-7 place-items-center rounded-md bg-primary text-primary-foreground"><Workflow className="size-4" /></span><span>CloudSpawn</span></Link>
}

export function Shell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const [mobileOpen, setMobileOpen] = useState(false)
  const links = (items: typeof navigation) => items.map(({ label, href, icon: Icon }) => <Link key={href} href={href} onClick={() => setMobileOpen(false)} className={cn('flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors', pathname === href ? 'bg-accent text-foreground' : 'text-muted-foreground hover:bg-accent/60 hover:text-foreground')}><Icon className="size-4" />{label}</Link>)
  return <div className="min-h-screen bg-background"><aside className={cn('fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r bg-sidebar p-4 transition-transform md:translate-x-0', mobileOpen ? 'translate-x-0' : '-translate-x-full')}><div className="flex items-center justify-between px-2 py-2"><Brand /><button className="md:hidden" onClick={() => setMobileOpen(false)} aria-label="Close menu"><X className="size-4" /></button></div><div className="mt-10 flex flex-1 flex-col gap-7"><div><p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">Workspace</p><nav className="flex flex-col gap-1">{links(navigation)}</nav></div><div><p className="mb-2 px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">System</p><nav className="flex flex-col gap-1">{links(system)}</nav></div></div><div className="rounded-lg border bg-card p-3"><div className="flex items-center gap-2 text-xs font-medium"><CircleDot className="size-3 text-emerald-500" />Local Runtime</div><p className="mt-1 text-[11px] text-muted-foreground">Ready for your next workload</p></div></aside><div className="md:pl-64"><header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b bg-background/90 px-5 backdrop-blur md:px-8"><button className="md:hidden" onClick={() => setMobileOpen(true)} aria-label="Open menu"><Grid2X2 className="size-5" /></button><div className="hidden items-center gap-2 text-sm text-muted-foreground md:flex"><span>Workspace</span><ChevronRight className="size-3" /><span className="text-foreground">{pathname?.split('/').pop()?.replace('-', ' ') || 'overview'}</span></div><div className="ml-auto flex items-center gap-2 text-xs text-muted-foreground"><span className="size-1.5 rounded-full bg-emerald-500" />System ready</div></header><main>{children}</main></div></div>
}

export function SectionEyebrow({ children }: { children: React.ReactNode }) { return <p className="mb-3 text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">{children}</p> }

export function StatCard({ label, value, detail, icon: Icon }: { label: string; value: string; detail: string; icon: React.ElementType }) { return <div className="rounded-xl border bg-card p-5"><div className="flex items-start justify-between"><span className="text-sm text-muted-foreground">{label}</span><Icon className="size-4 text-muted-foreground" /></div><div className="mt-5 text-2xl font-semibold tracking-tight">{value}</div><p className="mt-1 text-xs text-muted-foreground">{detail}</p></div> }

export function EmptyState({ icon: Icon, title, description, action }: { icon: React.ElementType; title: string; description: string; action?: React.ReactNode }) { return <div className="flex flex-col items-center justify-center rounded-xl border border-dashed bg-card/40 px-6 py-16 text-center"><span className="mb-4 grid size-11 place-items-center rounded-lg border bg-muted/40"><Icon className="size-5 text-muted-foreground" /></span><h3 className="font-medium">{title}</h3><p className="mt-1 max-w-sm text-sm text-muted-foreground">{description}</p>{action && <div className="mt-5">{action}</div>}</div> }
