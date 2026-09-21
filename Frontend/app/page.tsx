import Link from 'next/link'
import { ArrowRight, Box, Check, ChevronRight, Cloud, FileText, GitBranch, Layers3, Network, Upload, Workflow, Zap } from 'lucide-react'

export default function Page() {
  const steps: { n: string; title: string; desc: string; icon: React.ElementType }[] = [
    { n: '01', title: 'Upload documents', desc: 'Bring your DOCX research files into the workspace.', icon: Upload },
    { n: '02', title: 'Create a knowledge base', desc: 'CloudSpawn prepares chunks and vectors for retrieval.', icon: Layers3 },
    { n: '03', title: 'Process the workload', desc: 'The runtime coordinates work across independent tasks.', icon: GitBranch },
    { n: '04', title: 'Ask through RAG', desc: 'Query your collection and inspect the supporting sources.', icon: FileText }
  ]

  return (
    <main className="min-h-screen overflow-hidden bg-[#0b0d0f] text-[#f3f5f6]">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
        <Link href="/" className="flex items-center gap-2.5 font-semibold tracking-tight">
          <span className="grid size-7 place-items-center rounded-md bg-[#e8ecef] text-[#101315]">
            <Workflow className="size-4" />
          </span>
          CloudSpawn
        </Link>
        <div className="hidden items-center gap-8 text-sm text-[#9aa2a8] md:flex">
          <a href="#architecture" className="hover:text-white">Architecture</a>
          <a href="#workflow" className="hover:text-white">How it works</a>
          <Link href="/workspace" className="flex items-center gap-1 text-white hover:text-[#b9c3ca]">
            Open workspace <ArrowRight className="size-4" />
          </Link>
        </div>
      </nav>

      <section className="relative mx-auto max-w-6xl px-6 pb-24 pt-20 md:pt-28">
        <div className="pointer-events-none absolute left-1/2 top-0 -z-0 size-[520px] -translate-x-1/2 rounded-full bg-[#46535b]/10 blur-[120px]" />
        <div className="relative z-10 max-w-3xl">
          <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-[#2c3338] bg-[#111518] px-3 py-1.5 text-xs text-[#aeb8be]">
            <span className="size-1.5 rounded-full bg-emerald-400" />
            Research preview · Local runtime
          </div>
          <h1 className="max-w-3xl text-5xl font-medium leading-[1.05] tracking-[-0.045em] md:text-7xl">
            Serverless execution for <span className="text-[#98a4ab]">autonomous AI workloads.</span>
          </h1>
          <p className="mt-7 max-w-xl text-lg leading-8 text-[#9aa2a8]">
            Turn large AI workloads into dynamically distributed cloud tasks with a runtime built for agents.
          </p>
          <div className="mt-9 flex flex-wrap items-center gap-3">
            <Link href="/workspace" className="inline-flex items-center gap-2 rounded-md bg-[#e8ecef] px-4 py-2.5 text-sm font-medium text-[#101315] transition hover:bg-white">
              Start building <ArrowRight className="size-4" />
            </Link>
            <a href="#architecture" className="inline-flex items-center gap-2 rounded-md border border-[#30383e] px-4 py-2.5 text-sm font-medium text-[#d1d7da] transition hover:bg-[#151a1d]">
              View architecture <ChevronRight className="size-4" />
            </a>
          </div>
        </div>
      </section>

      <section id="architecture" className="mx-auto max-w-6xl px-6 pb-28">
        <div className="rounded-xl border border-[#252c31] bg-[#101417] p-6 md:p-10">
          <div className="mb-10 flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-[#77828a]">Execution topology</p>
              <h2 className="mt-2 text-xl font-medium">One agent. Many ephemeral tasks.</h2>
            </div>
            <Network className="size-5 text-[#77828a]" />
          </div>
          <div className="grid gap-5 md:grid-cols-5 md:items-center">
            <Node icon={Zap} label="AI Agent" />
            <Connector />
            <Node active icon={Workflow} label="CloudSpawn" />
            <Connector />
            <div className="grid grid-cols-3 gap-2 md:col-span-1 md:grid-cols-1">
              <Node compact icon={Cloud} label="Task 01" />
              <Node compact icon={Cloud} label="Task 02" />
              <Node compact icon={Cloud} label="Task 03" />
            </div>
          </div>
        </div>
      </section>

      <section id="workflow" className="mx-auto max-w-6xl border-t border-[#252c31] px-6 py-24">
        <div className="grid gap-12 md:grid-cols-[0.8fr_1.2fr]">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-[#77828a]">How it works</p>
            <h2 className="mt-3 text-3xl font-medium tracking-tight">From documents to answers.</h2>
            <p className="mt-4 max-w-sm leading-7 text-[#8f999f]">
              A focused workflow for turning research material into a searchable, agent-ready knowledge base.
            </p>
          </div>
          <div className="grid gap-3">
            {steps.map(({ n, title, desc, icon: Icon }) => (
              <div key={n} className="group flex gap-5 border-b border-[#252c31] py-5">
                <span className="pt-1 font-mono text-xs text-[#677279]">{n}</span>
                <div className="flex-1">
                  <h3 className="font-medium">{title}</h3>
                  <p className="mt-1 text-sm text-[#8f999f]">{desc}</p>
                </div>
                <Icon className="mt-1 size-4 text-[#677279] transition group-hover:text-white" />
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="mx-auto flex max-w-6xl flex-col gap-3 border-t border-[#252c31] px-6 py-8 text-sm text-[#77828a] md:flex-row md:items-center md:justify-between">
        <span className="font-medium text-[#c9d0d4]">CloudSpawn</span>
        <span>Powered by Formicx Runtime × AWS</span>
      </footer>
    </main>
  )
}

function Node({ icon: Icon, label, active, compact }: { icon: React.ElementType; label: string; active?: boolean; compact?: boolean }) { return <div className={`flex ${compact ? 'flex-row items-center gap-3 p-3' : 'min-h-24 flex-col items-center justify-center gap-3 p-5'} rounded-lg border ${active ? 'border-[#8e9ba3] bg-[#182024]' : 'border-[#30383e] bg-[#14191c]'}`}><Icon className="size-5 text-[#aab5bb]" /><span className="text-sm text-[#d2d8db]">{label}</span></div> }
function Connector() { return <div className="hidden h-px bg-[#3b454c] md:block" /> }

