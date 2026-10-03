'use client'

import { useState } from 'react'
import Link from 'next/link'
import {
  ArrowRight,
  Bot,
  CheckCircle2,
  ChevronRight,
  Cpu,
  Database,
  FileText,
  Layers,
  Network,
  Play,
  Search,
  Server,
  ShieldCheck,
  Sparkles,
  Terminal,
  Upload,
  Workflow,
  Zap
} from 'lucide-react'

export default function Page() {
  const [activeStep, setActiveStep] = useState(0)
  const [demoQuery, setDemoQuery] = useState('How does CloudSpawn orchestrate RAG across EKS?')
  const [isSimulating, setIsSimulating] = useState(false)
  const [simStep, setSimStep] = useState<number | null>(null)
  const [simCompleted, setSimCompleted] = useState(false)

  const steps = [
    {
      n: '01',
      title: 'Document Ingestion & Storage',
      tagline: 'AWS S3 Upload',
      desc: 'Docx & text research files are uploaded to dedicated S3 buckets with metadata extraction.',
      icon: Upload,
      color: 'from-blue-500 to-cyan-400',
      badgeColor: 'border-cyan-500/30 bg-cyan-500/10 text-cyan-400',
      details: ['Multi-format Docx parser', 'AWS S3 object key mapping', 'Deterministic document IDs']
    },
    {
      n: '02',
      title: 'Dense Embedding Generation',
      tagline: 'all-MiniLM-L6-v2',
      desc: 'Text is split into semantic chunks and converted into 384-dimensional dense vectors.',
      icon: Cpu,
      color: 'from-indigo-500 to-violet-400',
      badgeColor: 'border-indigo-500/30 bg-indigo-500/10 text-indigo-400',
      details: ['Sentence-Transformers engine', '384-dim dense vectors', 'Semantic boundary chunking']
    },
    {
      n: '03',
      title: 'FAISS Vector Indexing',
      tagline: 'L2 Distance Search',
      desc: 'High-speed similarity search indexes store chunks locally and in S3 for instant top-k retrieval.',
      icon: Database,
      color: 'from-purple-500 to-pink-400',
      badgeColor: 'border-purple-500/30 bg-purple-500/10 text-purple-400',
      details: ['FAISS IndexFlatL2 engine', 'Sub-millisecond retrieval', 'S3 index sync & reload']
    },
    {
      n: '04',
      title: 'EKS Kubernetes Dispatch',
      tagline: 'CloudSpawn Pod Service',
      desc: 'Query string and retrieved vector search chunks are packaged and POSTed to EKS cluster service.',
      icon: Server,
      color: 'from-emerald-500 to-teal-400',
      badgeColor: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400',
      details: ['LoadBalancer service endpoint', 'EKS NodeGroup scaling', 'Grounded context payload']
    },
    {
      n: '05',
      title: 'Grounded LLM Generation',
      tagline: 'Groq Llama-3.3 70B',
      desc: 'Groq LLM synthesizes concise answers strictly bound to provided document context snippets.',
      icon: Bot,
      color: 'from-amber-500 to-orange-400',
      badgeColor: 'border-amber-500/30 bg-amber-500/10 text-amber-400',
      details: ['Zero hallucination enforcement', 'Exact document source attribution', 'Markdown response output']
    }
  ]

  const sampleQueries = [
    'How does CloudSpawn orchestrate RAG across EKS?',
    'What embedding model is used for document vectorization?',
    'How are FAISS indexes synchronized with S3?'
  ]

  const handleRunSimulation = (query: string) => {
    setDemoQuery(query)
    setIsSimulating(true)
    setSimCompleted(false)
    setSimStep(1)

    setTimeout(() => setSimStep(2), 700)
    setTimeout(() => setSimStep(3), 1400)
    setTimeout(() => setSimStep(4), 2100)
    setTimeout(() => {
      setSimStep(5)
      setIsSimulating(false)
      setSimCompleted(true)
    }, 2800)
  }

  return (
    <main className="relative min-h-screen overflow-x-hidden bg-[#07090e] text-slate-100 selection:bg-indigo-500/30 selection:text-indigo-200">
      {/* Background Ambient Glow Lights */}
      <div className="pointer-events-none absolute left-1/2 top-0 -z-10 h-[650px] w-full max-w-7xl -translate-x-1/2">
        <div className="absolute top-[-100px] left-[15%] h-[400px] w-[500px] rounded-full bg-indigo-600/15 blur-[140px] animate-pulse-glow" />
        <div className="absolute top-[50px] right-[15%] h-[450px] w-[450px] rounded-full bg-purple-600/15 blur-[150px] animate-pulse-glow" />
        <div className="absolute top-[250px] left-[35%] h-[300px] w-[400px] rounded-full bg-cyan-500/10 blur-[130px]" />
      </div>

      {/* Grid Pattern Overlay */}
      <div className="pointer-events-none absolute inset-0 -z-10 bg-[linear-gradient(to_right,#1e293b12_1px,transparent_1px),linear-gradient(to_bottom,#1e293b12_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]" />

      {/* Header Navigation */}
      <header className="sticky top-0 z-50 border-b border-slate-800/60 bg-[#07090e]/80 backdrop-blur-xl">
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link href="/" className="group flex items-center gap-3 font-bold tracking-tight text-white">
            <div className="relative flex size-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 via-purple-500 to-cyan-400 p-[1px] shadow-lg shadow-indigo-500/20 transition group-hover:shadow-indigo-500/40">
              <div className="flex size-full items-center justify-center rounded-[11px] bg-[#0c0f17]">
                <Workflow className="size-5 text-indigo-400 transition group-hover:scale-110" />
              </div>
            </div>
            <span className="text-xl tracking-tight">Cloud<span className="text-indigo-400">Spawn</span></span>
          </Link>

          <div className="hidden items-center gap-8 text-sm font-medium text-slate-400 md:flex">
            <a href="#pipeline" className="transition hover:text-white">Architecture</a>
            <a href="#how-it-works" className="transition hover:text-white">How It Works</a>
            <a href="#live-demo" className="transition hover:text-white">Interactive Demo</a>
            <a href="#features" className="transition hover:text-white">Features</a>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-400 sm:flex">
              <span className="relative flex size-2">
                <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                <span className="relative inline-flex size-2 rounded-full bg-emerald-500" />
              </span>
              EKS Engine Active
            </div>

            <Link
              href="/workspace"
              className="group relative inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition hover:shadow-indigo-500/40 hover:brightness-110"
            >
              Open Workspace
              <ArrowRight className="size-4 transition group-hover:translate-x-0.5" />
            </Link>
          </div>
        </nav>
      </header>

      {/* HERO SECTION */}
      <section className="relative mx-auto max-w-7xl px-6 pb-20 pt-16 md:pt-24">
        <div className="flex flex-col items-center text-center">
          {/* Badge */}
          <div className="mb-6 inline-flex items-center gap-2.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-4 py-1.5 text-xs font-semibold text-indigo-300 backdrop-blur-md shadow-sm">
            <Sparkles className="size-3.5 text-cyan-400" />
            <span>Autonomous RAG & Kubernetes Knowledge Orchestrator</span>
          </div>

          {/* Main Title */}
          <h1 className="max-w-4xl text-4xl font-extrabold tracking-tight text-white sm:text-6xl lg:text-7xl">
            Orchestrate RAG Knowledge Bases across <span className="text-gradient-primary">AWS EKS & FAISS Vectors</span>
          </h1>

          {/* Subtitle */}
          <p className="mt-6 max-w-2xl text-lg leading-relaxed text-slate-400 sm:text-xl">
            Transform unstructured research documents into high-dimensional FAISS vector indexes. 
            Orchestrated automatically with zero-hallucination context injection on AWS EKS micro-services.
          </p>

          {/* Action CTAs */}
          <div className="mt-9 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/workspace"
              className="inline-flex items-center gap-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 px-6 py-3.5 text-base font-semibold text-white shadow-xl shadow-indigo-500/30 transition hover:scale-[1.02] hover:shadow-indigo-500/50"
            >
              Launch Workspace
              <ArrowRight className="size-5" />
            </Link>
            <a
              href="#pipeline"
              className="glass-panel glass-card-hover inline-flex items-center gap-2 rounded-xl px-6 py-3.5 text-base font-semibold text-slate-200 transition hover:bg-slate-800/60"
            >
              Explore Architecture
              <ChevronRight className="size-5 text-slate-400" />
            </a>
          </div>

          {/* Metric Stats Banner */}
          <div className="mt-16 grid w-full max-w-4xl grid-cols-2 gap-4 rounded-2xl border border-slate-800/80 bg-slate-950/60 p-6 backdrop-blur-xl sm:grid-cols-4">
            <div className="border-r border-slate-800/60 p-3 text-center last:border-none sm:border-r">
              <div className="text-2xl font-bold text-white sm:text-3xl">384-Dim</div>
              <div className="mt-1 text-xs font-medium text-slate-400">Dense Embeddings</div>
            </div>
            <div className="border-r border-slate-800/60 p-3 text-center last:border-none sm:border-r">
              <div className="text-2xl font-bold text-cyan-400 sm:text-3xl">FAISS L2</div>
              <div className="mt-1 text-xs font-medium text-slate-400">Vector Search</div>
            </div>
            <div className="border-r border-slate-800/60 p-3 text-center last:border-none sm:border-r">
              <div className="text-2xl font-bold text-purple-400 sm:text-3xl">AWS EKS</div>
              <div className="mt-1 text-xs font-medium text-slate-400">Pod Orchestration</div>
            </div>
            <div className="p-3 text-center">
              <div className="text-2xl font-bold text-emerald-400 sm:text-3xl">Groq LLM</div>
              <div className="mt-1 text-xs font-medium text-slate-400">Grounded Output</div>
            </div>
          </div>
        </div>
      </section>

      {/* PIPELINE & ARCHITECTURE EXPLAINER */}
      <section id="pipeline" className="mx-auto max-w-7xl px-6 py-20">
        <div className="mb-12 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-purple-500/30 bg-purple-500/10 px-3 py-1 text-xs font-semibold text-purple-300">
            <Network className="size-3.5" /> Execution Topology
          </div>
          <h2 className="mt-4 text-3xl font-extrabold text-white sm:text-4xl">
            How CloudSpawn Processes & Answers Queries
          </h2>
          <p className="mt-3 text-slate-400">
            Click on any pipeline stage to understand how data flows from raw documents into EKS cluster micro-services.
          </p>
        </div>

        {/* Step Selector Tabs */}
        <div className="grid gap-3 sm:grid-cols-5">
          {steps.map((step, idx) => {
            const Icon = step.icon
            const isSelected = activeStep === idx
            return (
              <button
                key={step.n}
                onClick={() => setActiveStep(idx)}
                className={`flex flex-col items-start rounded-xl p-4 text-left transition ${
                  isSelected
                    ? 'border border-indigo-500/50 bg-slate-900/90 shadow-lg shadow-indigo-500/10'
                    : 'border border-slate-800/60 bg-slate-950/40 hover:border-slate-700 hover:bg-slate-900/40'
                }`}
              >
                <div className="flex w-full items-center justify-between">
                  <span className="font-mono text-xs font-bold text-slate-500">{step.n}</span>
                  <Icon className={`size-5 ${isSelected ? 'text-indigo-400' : 'text-slate-500'}`} />
                </div>
                <div className="mt-3 text-sm font-semibold text-white">{step.title}</div>
                <div className="mt-1 text-xs text-slate-400">{step.tagline}</div>
              </button>
            )
          })}
        </div>

        {/* Active Stage Detail Panel */}
        <div className="mt-6 rounded-2xl border border-slate-800/80 bg-slate-950/80 p-6 backdrop-blur-xl sm:p-8">
          <div className="grid gap-8 lg:grid-cols-2 lg:items-center">
            <div>
              <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-bold ${steps[activeStep].badgeColor}`}>
                Stage {steps[activeStep].n} · {steps[activeStep].tagline}
              </span>
              <h3 className="mt-4 text-2xl font-bold text-white">{steps[activeStep].title}</h3>
              <p className="mt-3 leading-relaxed text-slate-300">{steps[activeStep].desc}</p>
              
              <div className="mt-6 space-y-2.5">
                {steps[activeStep].details.map((detail, dIdx) => (
                  <div key={dIdx} className="flex items-center gap-3 text-sm text-slate-300">
                    <CheckCircle2 className="size-4 shrink-0 text-emerald-400" />
                    <span>{detail}</span>
                  </div>
                ))}
              </div>

              <div className="mt-8 flex items-center gap-3">
                <Link
                  href="/workspace"
                  className="inline-flex items-center gap-2 text-sm font-semibold text-indigo-400 hover:text-indigo-300"
                >
                  Try in Workspace <ArrowRight className="size-4" />
                </Link>
              </div>
            </div>

            {/* Architecture Diagram Code Visualizer */}
            <div className="rounded-xl border border-slate-800 bg-[#0b0e17] p-5 font-mono text-xs">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3 text-slate-500">
                <div className="flex items-center gap-2">
                  <Terminal className="size-4 text-indigo-400" />
                  <span className="font-semibold text-slate-300">pipeline_execution_node_{steps[activeStep].n}.py</span>
                </div>
                <span className="rounded bg-slate-800 px-2 py-0.5 text-[10px] text-slate-400">READY</span>
              </div>
              <pre className="mt-4 overflow-x-auto text-slate-300 leading-relaxed">
{activeStep === 0 && `
# 1. AWS S3 Upload & Key Parsing
s3_client.upload_fileobj(
    file_obj=document.file,
    bucket="cloudspawn-storage-prod",
    key=f"uploads/{document_id}.docx"
)
logger.info(f"Document {filename} indexed in S3.")
`}
{activeStep === 1 && `
# 2. Sentence-Transformers Embedding
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks, normalize_embeddings=True)
print(f"Generated {len(embeddings)} 384-d vectors.")
`}
{activeStep === 2 && `
# 3. FAISS Vector Search Index
index = faiss.IndexFlatL2(384)
index.add(np.array(embeddings, dtype=np.float32))
top_k_indices, scores = index.search(query_vec, top_k=5)
`}
{activeStep === 3 && `
# 4. EKS Cluster Dispatch Payload
payload = {
    "text": user_query,
    "context": "\\n\\n".join([c["text"] for c in top_chunks])
}
res = requests.post(EKS_CHATBOT_URL, json=payload)
`}
{activeStep === 4 && `
# 5. EKS Pod Groq LLM Response
completion = groq_client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "system", "content": prompt}]
)
answer = completion.choices[0].message.content
`}
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* INTERACTIVE DEMO SIMULATOR */}
      <section id="live-demo" className="mx-auto max-w-7xl px-6 py-20">
        <div className="rounded-3xl border border-indigo-500/20 bg-gradient-to-b from-slate-950 via-[#0c0f1c] to-slate-950 p-8 shadow-2xl backdrop-blur-xl sm:p-12">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-xs font-semibold text-cyan-300">
              <Play className="size-3.5" /> Interactive RAG Simulator
            </div>
            <h2 className="mt-4 text-3xl font-extrabold text-white sm:text-4xl">
              Test CloudSpawn Query Dispatch in Real-Time
            </h2>
            <p className="mt-3 text-slate-400">
              Select a sample prompt below or type your query to watch how CloudSpawn embeds text, queries FAISS vectors, and dispatches to EKS.
            </p>
          </div>

          {/* Sample Prompts */}
          <div className="mt-6 flex flex-wrap gap-2">
            {sampleQueries.map((q, i) => (
              <button
                key={i}
                onClick={() => handleRunSimulation(q)}
                className="rounded-lg border border-slate-800 bg-slate-900/60 px-3.5 py-1.5 text-xs font-medium text-slate-300 transition hover:border-indigo-500/50 hover:bg-slate-800 hover:text-white"
              >
                "{q}"
              </button>
            ))}
          </div>

          {/* Interactive Query Input */}
          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-4 top-1/2 size-5 -translate-y-1/2 text-slate-500" />
              <input
                type="text"
                value={demoQuery}
                onChange={(e) => setDemoQuery(e.target.value)}
                placeholder="Ask a research question..."
                className="w-full rounded-xl border border-slate-800 bg-slate-900/90 py-3.5 pl-12 pr-4 text-sm text-white placeholder-slate-500 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <button
              onClick={() => handleRunSimulation(demoQuery)}
              disabled={isSimulating}
              className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition hover:brightness-110 disabled:opacity-50"
            >
              {isSimulating ? (
                <>
                  <div className="size-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  Dispatching to EKS...
                </>
              ) : (
                <>
                  Simulate Execution <Play className="size-4" />
                </>
              )}
            </button>
          </div>

          {/* Simulation Output Card */}
          {(simStep !== null || simCompleted) && (
            <div className="mt-8 rounded-2xl border border-slate-800 bg-[#080b12] p-6">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
                <div className="flex items-center gap-2.5">
                  <div className="size-2.5 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Live Execution Trace</span>
                </div>
                <span className="text-xs font-mono text-indigo-400">
                  {simCompleted ? 'STATUS 200 OK' : `STEP ${simStep}/5`}
                </span>
              </div>

              <div className="mt-5 grid gap-3 sm:grid-cols-4 text-xs font-mono">
                <div className={`rounded-lg p-3 border ${simStep && simStep >= 1 ? 'border-cyan-500/40 bg-cyan-500/10 text-cyan-300' : 'border-slate-800 bg-slate-900/40 text-slate-600'}`}>
                  1. Embed Query (384d)
                </div>
                <div className={`rounded-lg p-3 border ${simStep && simStep >= 2 ? 'border-purple-500/40 bg-purple-500/10 text-purple-300' : 'border-slate-800 bg-slate-900/40 text-slate-600'}`}>
                  2. FAISS L2 Match (k=5)
                </div>
                <div className={`rounded-lg p-3 border ${simStep && simStep >= 3 ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300' : 'border-slate-800 bg-slate-900/40 text-slate-600'}`}>
                  3. EKS POST /chat
                </div>
                <div className={`rounded-lg p-3 border ${simStep && simStep >= 4 ? 'border-amber-500/40 bg-amber-500/10 text-amber-300' : 'border-slate-800 bg-slate-900/40 text-slate-600'}`}>
                  4. Groq Synthesis
                </div>
              </div>

              {simCompleted && (
                <div className="mt-6 rounded-xl border border-emerald-500/30 bg-emerald-500/5 p-5 text-sm text-slate-200">
                  <div className="flex items-center gap-2 font-bold text-emerald-400">
                    <CheckCircle2 className="size-4" /> Grounded EKS Answer Generated
                  </div>
                  <p className="mt-2.5 leading-relaxed text-slate-300">
                    <strong>CloudSpawn RAG Answer:</strong> CloudSpawn orchestrates research queries by converting input text into 384-dimensional dense vectors, matching top chunks from FAISS vector storage, and dispatching both the context and query directly to the active EKS Kubernetes cluster service running Groq LLM inference.
                  </p>
                  <div className="mt-3 flex items-center gap-4 text-xs font-mono text-slate-400">
                    <span>Sources: docx_research_kb.docx (Chunk #1, #3)</span>
                    <span>Similarity Score: 0.892</span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      {/* CORE FEATURES GRID */}
      <section id="features" className="mx-auto max-w-7xl px-6 py-20">
        <div className="mb-12 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-xs font-semibold text-indigo-300">
            <Zap className="size-3.5 text-indigo-400" /> Platform Architecture
          </div>
          <h2 className="mt-4 text-3xl font-extrabold text-white sm:text-4xl">
            Built for Autonomous AI Workloads
          </h2>
          <p className="mt-3 text-slate-400">
            Key capabilities engineered for reliability, accuracy, and scale.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          <div className="glass-panel glass-card-hover rounded-2xl p-7">
            <div className="flex size-12 items-center justify-center rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
              <Database className="size-6" />
            </div>
            <h3 className="mt-5 text-xl font-bold text-white">FAISS Vector Search</h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-400">
              High-dimensional L2 distance index for sub-millisecond similarity queries across indexed research collections.
            </p>
          </div>

          <div className="glass-panel glass-card-hover rounded-2xl p-7">
            <div className="flex size-12 items-center justify-center rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400">
              <Server className="size-6" />
            </div>
            <h3 className="mt-5 text-xl font-bold text-white">AWS EKS Orchestration</h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-400">
              Isolated Kubernetes pod deployment running high-throughput FastAPI & Groq LLM inference endpoints.
            </p>
          </div>

          <div className="glass-panel glass-card-hover rounded-2xl p-7">
            <div className="flex size-12 items-center justify-center rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
              <ShieldCheck className="size-6" />
            </div>
            <h3 className="mt-5 text-xl font-bold text-white">Strict Source Attribution</h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-400">
              Every generated response cites exact document IDs, filenames, and chunk indices to eliminate AI hallucinations.
            </p>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-slate-800/80 bg-[#05070a] px-6 py-10">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 text-center text-sm text-slate-500 md:flex-row md:text-left">
          <div className="flex items-center gap-3">
            <span className="font-bold text-white">CloudSpawn</span>
            <span className="text-slate-600">|</span>
            <span>FAISS Vector Indexing × AWS EKS Orchestrator</span>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/workspace" className="text-slate-400 transition hover:text-white">Workspace</Link>
            <Link href="/workspace/chat" className="text-slate-400 transition hover:text-white">Chat Engine</Link>
            <Link href="/workspace/knowledge-base" className="text-slate-400 transition hover:text-white">Knowledge Base</Link>
          </div>
        </div>
      </footer>
    </main>
  )
}
