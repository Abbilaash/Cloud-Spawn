'use client'

import { useState } from 'react'
import Link from 'next/link'
import {
  ArrowDown,
  ArrowRight,
  Bot,
  CheckCircle2,
  ChevronRight,
  Cloud,
  Cpu,
  Database,
  FileText,
  GitBranch,
  Layers,
  MessageSquare,
  Network,
  Play,
  RefreshCw,
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
  const [selectedNode, setSelectedNode] = useState<string>('formicx')
  const [demoQuery, setDemoQuery] = useState('How does CloudSpawn orchestrate RAG across EKS?')
  const [isSimulating, setIsSimulating] = useState(false)
  const [simStep, setSimStep] = useState<number | null>(null)
  const [simCompleted, setSimCompleted] = useState(false)

  // Formicx Task Splitting Animation State
  const [isFormicxActive, setIsFormicxActive] = useState(false)
  const [formicxPhase, setFormicxPhase] = useState<number>(0)

  const architectureNodes: Record<string, { title: string; subtitle: string; desc: string; icon: any; tech: string; badge: string; color: string; schema: string }> = {
    formicx: {
      title: 'Formicx Runtime Orchestrator',
      subtitle: 'Dynamic Task Splitter & Agent Daemon',
      desc: 'Formicx registers autonomous agents, monitors workload queues, dynamically splits heavy document processing tasks into parallel batches, and dispatches them across AWS Lambda worker tasks.',
      icon: Network,
      tech: 'Formicx Daemon Engine / Python',
      badge: 'Task Splitter & Orchestrator',
      color: 'border-rose-500/50 bg-rose-500/10 text-rose-400',
      schema: `formicx_agent.register_agent("cloudspawn-worker")
batches = split_document(document, batch_size=25)
for batch in batches:
    formicx_agent.send_message(target="lambda-worker", data=batch)
results = await_formicx_inbox()`
    },
    lambda: {
      title: 'AWS Lambda Worker Pool',
      subtitle: 'cloudspawn-lambda-worker (Serverless)',
      desc: 'Serverless execution workers triggered in parallel by Formicx. Each Lambda worker computes 384-dimensional dense vectors and uploads index fragments directly to AWS S3.',
      icon: Zap,
      tech: 'AWS Lambda / Python 3.11',
      badge: 'Serverless Execution Tasks',
      color: 'border-orange-500/50 bg-orange-500/10 text-orange-400',
      schema: `def lambda_handler(event, context):
    chunks = event["chunks"]
    embeddings = embed_minilm(chunks)
    s3.put_object(Bucket="cloudspawn-faiss-indexes", Key=event["key"], Body=embeddings)
    return {"status": 200, "count": len(chunks)}`
    },
    user: {
      title: 'User Interface / API Client',
      subtitle: 'Frontend Chat & REST Endpoints',
      desc: 'Users submit research queries through the React frontend or direct API endpoints (/api/chat, /api/rag/search).',
      icon: MessageSquare,
      tech: 'Next.js 16 / TypeScript',
      badge: 'Client Tier',
      color: 'border-blue-500/50 bg-blue-500/10 text-blue-400',
      schema: `POST /api/chat
{
  "message": "What is CloudSpawn?",
  "conversation_id": "conv-9921-x"
}`
    },
    backend: {
      title: 'CloudSpawn RAG Orchestrator',
      subtitle: 'FastAPI Backend Engine',
      desc: 'Coordinates MongoDB history, triggers embedding generation, executes FAISS similarity queries, and packages EKS payloads.',
      icon: Workflow,
      tech: 'Python 3.11 / FastAPI',
      badge: 'Core Gateway',
      color: 'border-indigo-500/50 bg-indigo-500/10 text-indigo-400',
      schema: `class RAGService:
  def process_chat(user_message, conv_id):
      query_vec = embed_text(user_message)
      context = vector_service.search(query_vec)
      return dispatch_to_eks(context)`
    },
    s3: {
      title: 'AWS S3 Document Storage',
      subtitle: 'cloudspawn-storage-prod & faiss-indexes',
      desc: 'Stores original uploaded Docx research files and serialized FAISS index metadata snapshots in region eu-north-1.',
      icon: Cloud,
      tech: 'AWS S3 / Boto3 SDK',
      badge: 'Persistence Layer',
      color: 'border-cyan-500/50 bg-cyan-500/10 text-cyan-400',
      schema: `s3://cloudspawn-storage-prod/
  ├── uploads/
  │   └── doc_88291.docx
  └── faiss_indexes/
      ├── cluster_0_index.faiss
      └── cluster_0_metadata.json`
    },
    embedding: {
      title: 'Dense Vector Embedder',
      subtitle: 'all-MiniLM-L6-v2',
      desc: 'Transforms text chunks into 384-dimensional floating-point dense vector embeddings for semantic search.',
      icon: Cpu,
      tech: 'Sentence-Transformers / PyTorch',
      badge: 'ML Vectorizer',
      color: 'border-violet-500/50 bg-violet-500/10 text-violet-400',
      schema: `Model: sentence-transformers/all-MiniLM-L6-v2
Vector Dimensions: 384
Output: ndarray(shape=(384,), dtype=float32)`
    },
    faiss: {
      title: 'FAISS Vector Search Store',
      subtitle: 'IndexFlatL2 Similarity Engine',
      desc: 'Executes high-speed sub-millisecond Euclidean (L2) distance search across document vector chunks.',
      icon: Database,
      tech: 'Meta FAISS C++ / Python',
      badge: 'Vector Search Engine',
      color: 'border-purple-500/50 bg-purple-500/10 text-purple-400',
      schema: `faiss.IndexFlatL2(384)
top_k_chunks = index.search(query_vec, k=5)
Result: [{"chunk_id": "c-01", "score": 0.892}]`
    },
    eks: {
      title: 'AWS EKS Kubernetes Cluster',
      subtitle: 'cloudspawn-eks-cluster (eu-north-1)',
      desc: 'Managed EKS cluster with LoadBalancer service (cloudspawn-chatbot-service) and auto-scaling t3.small EC2 nodegroup.',
      icon: Server,
      tech: 'Kubernetes v1.36 / AWS EKS',
      badge: 'Cluster Micro-Service',
      color: 'border-emerald-500/50 bg-emerald-500/10 text-emerald-400',
      schema: `kubectl get svc -n cloudspawn-rag
NAME: cloudspawn-chatbot-service
TYPE: LoadBalancer
ENDPOINT: http://16.171.40.117:32574/chat`
    },
    groq: {
      title: 'Groq LLM Acceleration Pod',
      subtitle: 'Llama-3.3 70B Versatile',
      desc: 'Generates grounded, zero-hallucination markdown answers strictly constrained by the RAG document context.',
      icon: Bot,
      tech: 'Groq API / Llama-3.3-70B',
      badge: 'LLM Inference',
      color: 'border-amber-500/50 bg-amber-500/10 text-amber-400',
      schema: `ChatResponse(
  response="**CloudSpawn** is an AI-powered RAG...",
  sources=[{"filename": "research.docx", "chunk": 1}]
)`
    }
  }

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

  const handleRunFormicxAnimation = () => {
    setIsFormicxActive(true)
    setFormicxPhase(1)

    setTimeout(() => setFormicxPhase(2), 900)
    setTimeout(() => setFormicxPhase(3), 1800)
    setTimeout(() => {
      setFormicxPhase(4)
      setIsFormicxActive(false)
    }, 2700)
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
            <a href="#formicx-animator" className="transition hover:text-white">Formicx & AWS Lambda</a>
            <a href="#flowchart" className="transition hover:text-white">Architecture Flowchart</a>
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
      <section className="relative mx-auto max-w-7xl px-6 pb-16 pt-16 md:pt-24">
        <div className="flex flex-col items-center text-center">
          <div className="mb-6 inline-flex items-center gap-2.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-4 py-1.5 text-xs font-semibold text-indigo-300 backdrop-blur-md shadow-sm">
            <Sparkles className="size-3.5 text-cyan-400" />
            <span>Formicx Orchestration × AWS Lambda Workers × AWS EKS</span>
          </div>

          <h1 className="max-w-4xl text-4xl font-extrabold tracking-tight text-white sm:text-6xl lg:text-7xl">
            Orchestrate RAG Knowledge Bases across <span className="text-gradient-primary">AWS EKS & FAISS Vectors</span>
          </h1>

          <p className="mt-6 max-w-2xl text-lg leading-relaxed text-slate-400 sm:text-xl">
            Formicx dynamically splits heavy document workloads, dispatches parallel serverless AWS Lambda workers, 
            and orchestrates vector search directly into AWS EKS micro-services.
          </p>

          <div className="mt-9 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/workspace"
              className="inline-flex items-center gap-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 px-6 py-3.5 text-base font-semibold text-white shadow-xl shadow-indigo-500/30 transition hover:scale-[1.02] hover:shadow-indigo-500/50"
            >
              Launch Workspace
              <ArrowRight className="size-5" />
            </Link>
            <a
              href="#formicx-animator"
              className="glass-panel glass-card-hover inline-flex items-center gap-2 rounded-xl px-6 py-3.5 text-base font-semibold text-slate-200 transition hover:bg-slate-800/60"
            >
              View Formicx & Lambda Split
              <ChevronRight className="size-5 text-slate-400" />
            </a>
          </div>

          {/* Metric Stats Banner */}
          <div className="mt-16 grid w-full max-w-4xl grid-cols-2 gap-4 rounded-2xl border border-slate-800/80 bg-slate-950/60 p-6 backdrop-blur-xl sm:grid-cols-4">
            <div className="border-r border-slate-800/60 p-3 text-center last:border-none sm:border-r">
              <div className="text-2xl font-bold text-rose-400 sm:text-3xl">Formicx</div>
              <div className="mt-1 text-xs font-medium text-slate-400">Task Orchestrator</div>
            </div>
            <div className="border-r border-slate-800/60 p-3 text-center last:border-none sm:border-r">
              <div className="text-2xl font-bold text-orange-400 sm:text-3xl">AWS Lambda</div>
              <div className="mt-1 text-xs font-medium text-slate-400">Serverless Workers</div>
            </div>
            <div className="border-r border-slate-800/60 p-3 text-center last:border-none sm:border-r">
              <div className="text-2xl font-bold text-cyan-400 sm:text-3xl">FAISS L2</div>
              <div className="mt-1 text-xs font-medium text-slate-400">384d Vector Search</div>
            </div>
            <div className="p-3 text-center">
              <div className="text-2xl font-bold text-emerald-400 sm:text-3xl">AWS EKS</div>
              <div className="mt-1 text-xs font-medium text-slate-400">Chatbot Micro-Service</div>
            </div>
          </div>
        </div>
      </section>

      {/* FORMICX & AWS LAMBDA TASK SPLITTING ANIMATED VISUALIZER */}
      <section id="formicx-animator" className="mx-auto max-w-7xl px-6 py-16">
        <div className="rounded-3xl border border-rose-500/20 bg-gradient-to-b from-slate-950 via-[#130d1a] to-slate-950 p-8 shadow-2xl backdrop-blur-xl sm:p-12">
          <div className="flex flex-col items-start justify-between gap-6 md:flex-row md:items-center">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-rose-500/30 bg-rose-500/10 px-3 py-1 text-xs font-semibold text-rose-300">
                <Network className="size-3.5 text-rose-400" /> Formicx Dynamic Workload Splitter
              </div>
              <h2 className="mt-3 text-3xl font-extrabold text-white sm:text-4xl">
                Formicx Task Splitting & AWS Lambda Orchestration
              </h2>
              <p className="mt-2 max-w-2xl text-sm text-slate-400">
                Watch how Formicx intercepts incoming research documents, splits them into parallel sub-tasks, 
                dispatches jobs across serverless AWS Lambda workers, and merges vector indexes into AWS S3.
              </p>
            </div>

            <button
              onClick={handleRunFormicxAnimation}
              disabled={isFormicxActive}
              className="inline-flex items-center gap-2.5 rounded-xl bg-gradient-to-r from-rose-500 via-purple-600 to-indigo-600 px-6 py-3.5 text-sm font-semibold text-white shadow-xl shadow-rose-500/20 transition hover:scale-[1.02] hover:brightness-110 disabled:opacity-50"
            >
              {isFormicxActive ? (
                <>
                  <RefreshCw className="size-4 animate-spin" /> Splitting Workload...
                </>
              ) : (
                <>
                  <Zap className="size-4 text-yellow-300" /> Trigger Formicx Workload Split
                </>
              )}
            </button>
          </div>

          {/* ANIMATED TASK SPLITTING WORKFLOW CANVAS */}
          <div className="mt-10 rounded-2xl border border-slate-800 bg-[#080a10] p-6 sm:p-8">
            
            {/* STEP PROGRESS INDICATOR */}
            <div className="grid gap-3 sm:grid-cols-4 font-mono text-xs">
              <div className={`rounded-xl p-3 border transition ${formicxPhase >= 1 ? 'border-rose-500/50 bg-rose-500/10 text-rose-300' : 'border-slate-800 bg-slate-900/40 text-slate-600'}`}>
                1. Workload Ingestion
              </div>
              <div className={`rounded-xl p-3 border transition ${formicxPhase >= 2 ? 'border-indigo-500/50 bg-indigo-500/10 text-indigo-300' : 'border-slate-800 bg-slate-900/40 text-slate-600'}`}>
                2. Formicx Sub-task Split
              </div>
              <div className={`rounded-xl p-3 border transition ${formicxPhase >= 3 ? 'border-orange-500/50 bg-orange-500/10 text-orange-300' : 'border-slate-800 bg-slate-900/40 text-slate-600'}`}>
                3. AWS Lambda Parallel Execution
              </div>
              <div className={`rounded-xl p-3 border transition ${formicxPhase >= 4 ? 'border-emerald-500/50 bg-emerald-500/10 text-emerald-300' : 'border-slate-800 bg-slate-900/40 text-slate-600'}`}>
                4. Formicx Inbox & S3 Merge
              </div>
            </div>

            {/* VISUAL DIAGRAM NODES & PARALLEL BRANCHES */}
            <div className="mt-8 grid gap-6 lg:grid-cols-3">
              
              {/* STAGE 1: FORMICX ORCHESTRATOR NODE */}
              <div className="flex flex-col justify-center rounded-2xl border border-rose-500/40 bg-rose-500/5 p-6 backdrop-blur-md">
                <div className="flex items-center justify-between">
                  <div className="flex size-12 items-center justify-center rounded-xl bg-rose-500/20 text-rose-400">
                    <Network className="size-6" />
                  </div>
                  <span className="rounded-full border border-rose-500/30 bg-rose-500/20 px-3 py-1 font-mono text-xs font-bold text-rose-300">FORMICX DAEMON</span>
                </div>

                <div className="mt-5 text-xl font-bold text-white">Formicx Dynamic Splitter</div>
                <p className="mt-2 text-xs leading-relaxed text-slate-300">
                  Intercepts large research documents (`research_paper.docx`, 120 pages) and calculates chunk boundaries.
                </p>

                {formicxPhase >= 2 && (
                  <div className="mt-4 rounded-xl border border-indigo-500/30 bg-indigo-500/10 p-3 font-mono text-[11px] text-indigo-300 animate-pulse">
                    ⚡ Formicx split workload into 3 parallel sub-tasks!
                  </div>
                )}
              </div>

              {/* STAGE 2: PARALLEL AWS LAMBDA WORKERS */}
              <div className="flex flex-col justify-center space-y-3">
                <div className="text-center font-mono text-xs font-bold uppercase tracking-wider text-orange-400">
                  Serverless AWS Lambda Workers (Parallel)
                </div>

                {/* Lambda Worker 1 */}
                <div className={`rounded-xl border p-4 transition ${formicxPhase >= 3 ? 'border-orange-500/60 bg-orange-500/10 text-white shadow-lg shadow-orange-500/10' : 'border-slate-800 bg-slate-900/40 text-slate-500'}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5 font-bold text-xs">
                      <Zap className="size-4 text-orange-400" />
                      <span>Lambda Worker #1</span>
                    </div>
                    <span className="font-mono text-[10px] text-slate-400">Batch 1 (Chunks 1–40)</span>
                  </div>
                  {formicxPhase >= 3 && (
                    <div className="mt-2 font-mono text-[10px] text-emerald-400">
                      ✓ Computed 40 dense 384d vectors
                    </div>
                  )}
                </div>

                {/* Lambda Worker 2 */}
                <div className={`rounded-xl border p-4 transition ${formicxPhase >= 3 ? 'border-orange-500/60 bg-orange-500/10 text-white shadow-lg shadow-orange-500/10' : 'border-slate-800 bg-slate-900/40 text-slate-500'}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5 font-bold text-xs">
                      <Zap className="size-4 text-orange-400" />
                      <span>Lambda Worker #2</span>
                    </div>
                    <span className="font-mono text-[10px] text-slate-400">Batch 2 (Chunks 41–80)</span>
                  </div>
                  {formicxPhase >= 3 && (
                    <div className="mt-2 font-mono text-[10px] text-emerald-400">
                      ✓ Computed 40 dense 384d vectors
                    </div>
                  )}
                </div>

                {/* Lambda Worker 3 */}
                <div className={`rounded-xl border p-4 transition ${formicxPhase >= 3 ? 'border-orange-500/60 bg-orange-500/10 text-white shadow-lg shadow-orange-500/10' : 'border-slate-800 bg-slate-900/40 text-slate-500'}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5 font-bold text-xs">
                      <Zap className="size-4 text-orange-400" />
                      <span>Lambda Worker #3</span>
                    </div>
                    <span className="font-mono text-[10px] text-slate-400">Batch 3 (Chunks 81–120)</span>
                  </div>
                  {formicxPhase >= 3 && (
                    <div className="mt-2 font-mono text-[10px] text-emerald-400">
                      ✓ Computed 40 dense 384d vectors
                    </div>
                  )}
                </div>
              </div>

              {/* STAGE 3: FORMICX AGGREGATION & MASTER FAISS S3 PERSISTENCE */}
              <div className="flex flex-col justify-center rounded-2xl border border-emerald-500/40 bg-emerald-500/5 p-6 backdrop-blur-md">
                <div className="flex items-center justify-between">
                  <div className="flex size-12 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-400">
                    <Database className="size-6" />
                  </div>
                  <span className="rounded-full border border-emerald-500/30 bg-emerald-500/20 px-3 py-1 font-mono text-xs font-bold text-emerald-300">MASTER INDEX</span>
                </div>

                <div className="mt-5 text-xl font-bold text-white">Formicx Inbox Aggregator</div>
                <p className="mt-2 text-xs leading-relaxed text-slate-300">
                  Formicx collects vector output messages from all 3 Lambda workers, merges FAISS index fragments, and notifies AWS EKS.
                </p>

                {formicxPhase >= 4 && (
                  <div className="mt-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3 font-mono text-[11px] text-emerald-300">
                    ✨ Master FAISS index merged (120 vectors) & persisted to AWS S3! Ready for EKS queries.
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SYSTEM ARCHITECTURE FLOWCHART DIAGRAM */}
      <section id="flowchart" className="mx-auto max-w-7xl px-6 py-16">
        <div className="mb-12 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-xs font-semibold text-indigo-300">
            <GitBranch className="size-3.5 text-indigo-400" /> Complete System Topology
          </div>
          <h2 className="mt-4 text-3xl font-extrabold text-white sm:text-4xl">
            System Architecture Flowchart
          </h2>
          <p className="mt-3 text-slate-400">
            Click on any component node in the flowchart below to inspect its live data schema and technical specifications.
          </p>
        </div>

        {/* FLOWCHART DIAGRAM CANVAS */}
        <div className="rounded-3xl border border-slate-800 bg-slate-950/90 p-6 shadow-2xl backdrop-blur-xl sm:p-10">
          
          {/* TOP PIPELINE STAGE HEADERS */}
          <div className="mb-8 hidden grid-cols-5 gap-4 text-center font-mono text-xs font-bold uppercase tracking-wider text-slate-500 lg:grid">
            <div className="rounded-lg border border-slate-800/60 bg-slate-900/30 py-2">1. Client Tier</div>
            <div className="rounded-lg border border-slate-800/60 bg-slate-900/30 py-2">2. Formicx Splitter</div>
            <div className="rounded-lg border border-slate-800/60 bg-slate-900/30 py-2">3. Lambda Workers</div>
            <div className="rounded-lg border border-slate-800/60 bg-slate-900/30 py-2">4. FAISS Search</div>
            <div className="rounded-lg border border-slate-800/60 bg-slate-900/30 py-2">5. EKS Groq LLM</div>
          </div>

          {/* VISUAL FLOWCHART GRAPH NODES */}
          <div className="grid gap-6 lg:grid-cols-5">
            
            {/* NODE 1: User / Frontend */}
            <div className="flex flex-col justify-between gap-4">
              <button
                onClick={() => setSelectedNode('user')}
                className={`group relative flex flex-col rounded-2xl border p-4 text-left transition ${
                  selectedNode === 'user'
                    ? 'border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/20'
                    : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex size-9 items-center justify-center rounded-xl bg-blue-500/20 text-blue-400">
                    <MessageSquare className="size-4" />
                  </div>
                  <span className="rounded-full border border-blue-500/30 bg-blue-500/10 px-2 py-0.5 font-mono text-[9px] font-bold text-blue-400">CLIENT</span>
                </div>
                <div className="mt-3 text-sm font-bold text-white">User Chat UI</div>
                <div className="mt-1 text-[11px] text-slate-400">Next.js Frontend / REST API</div>
              </button>

              <button
                onClick={() => setSelectedNode('backend')}
                className={`group relative flex flex-col rounded-2xl border p-4 text-left transition ${
                  selectedNode === 'backend'
                    ? 'border-indigo-500 bg-indigo-500/10 shadow-lg shadow-indigo-500/20'
                    : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex size-9 items-center justify-center rounded-xl bg-indigo-500/20 text-indigo-400">
                    <Workflow className="size-4" />
                  </div>
                  <span className="rounded-full border border-indigo-500/30 bg-indigo-500/10 px-2 py-0.5 font-mono text-[9px] font-bold text-indigo-400">API GATEWAY</span>
                </div>
                <div className="mt-3 text-sm font-bold text-white">FastAPI Core</div>
                <div className="mt-1 text-[11px] text-slate-400">RAG Engine & Session Storage</div>
              </button>
            </div>

            {/* NODE 2: Formicx */}
            <div className="flex flex-col justify-center gap-4">
              <button
                onClick={() => setSelectedNode('formicx')}
                className={`group relative flex h-full flex-col justify-between rounded-2xl border p-5 text-left transition ${
                  selectedNode === 'formicx'
                    ? 'border-rose-500 bg-rose-500/10 shadow-xl shadow-rose-500/20'
                    : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between">
                    <div className="flex size-10 items-center justify-center rounded-xl bg-rose-500/20 text-rose-400">
                      <Network className="size-5" />
                    </div>
                    <span className="rounded-full border border-rose-500/30 bg-rose-500/10 px-2 py-0.5 font-mono text-[9px] font-bold text-rose-400">ORCHESTRATOR</span>
                  </div>
                  <div className="mt-4 text-base font-bold text-white">Formicx Daemon</div>
                  <div className="mt-1 text-xs text-slate-400">Workload Splitting & Agent Messaging</div>
                </div>

                <div className="mt-4 rounded-xl border border-rose-500/30 bg-rose-500/10 p-2.5 font-mono text-[10px] text-rose-300">
                  ⚡ Splits tasks into Lambda workers
                </div>
              </button>
            </div>

            {/* NODE 3: AWS Lambda Workers */}
            <div className="flex flex-col justify-center gap-4">
              <button
                onClick={() => setSelectedNode('lambda')}
                className={`group relative flex h-full flex-col justify-between rounded-2xl border p-5 text-left transition ${
                  selectedNode === 'lambda'
                    ? 'border-orange-500 bg-orange-500/10 shadow-xl shadow-orange-500/20'
                    : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between">
                    <div className="flex size-10 items-center justify-center rounded-xl bg-orange-500/20 text-orange-400">
                      <Zap className="size-5" />
                    </div>
                    <span className="rounded-full border border-orange-500/30 bg-orange-500/10 px-2 py-0.5 font-mono text-[9px] font-bold text-orange-400">SERVERLESS</span>
                  </div>
                  <div className="mt-4 text-base font-bold text-white">AWS Lambda Pool</div>
                  <div className="mt-1 text-xs text-slate-400">Parallel 384d Dense Embeddings</div>
                </div>

                <div className="mt-4 rounded-xl border border-orange-500/30 bg-orange-500/10 p-2.5 font-mono text-[10px] text-orange-300">
                  🔥 Parallel execution in S3
                </div>
              </button>
            </div>

            {/* NODE 4: FAISS & S3 */}
            <div className="flex flex-col justify-between gap-4">
              <button
                onClick={() => setSelectedNode('faiss')}
                className={`group relative flex flex-col rounded-2xl border p-4 text-left transition ${
                  selectedNode === 'faiss'
                    ? 'border-purple-500 bg-purple-500/10 shadow-lg shadow-purple-500/20'
                    : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex size-9 items-center justify-center rounded-xl bg-purple-500/20 text-purple-400">
                    <Database className="size-4" />
                  </div>
                  <span className="rounded-full border border-purple-500/30 bg-purple-500/10 px-2 py-0.5 font-mono text-[9px] font-bold text-purple-400">FAISS L2</span>
                </div>
                <div className="mt-3 text-sm font-bold text-white">FAISS Vector Store</div>
                <div className="mt-1 text-[11px] text-slate-400">Top-K Context Retrieval</div>
              </button>

              <button
                onClick={() => setSelectedNode('s3')}
                className={`group relative flex flex-col rounded-2xl border p-4 text-left transition ${
                  selectedNode === 's3'
                    ? 'border-cyan-500 bg-cyan-500/10 shadow-lg shadow-cyan-500/20'
                    : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex size-9 items-center justify-center rounded-xl bg-cyan-500/20 text-cyan-400">
                    <Cloud className="size-4" />
                  </div>
                  <span className="rounded-full border border-cyan-500/30 bg-cyan-500/10 px-2 py-0.5 font-mono text-[9px] font-bold text-cyan-400">AWS S3</span>
                </div>
                <div className="mt-3 text-sm font-bold text-white">AWS S3 Bucket</div>
                <div className="mt-1 text-[11px] text-slate-400">Files & FAISS Snapshots</div>
              </button>
            </div>

            {/* NODE 5: EKS & Groq LLM */}
            <div className="flex flex-col justify-between gap-4">
              <button
                onClick={() => setSelectedNode('eks')}
                className={`group relative flex flex-col rounded-2xl border p-4 text-left transition ${
                  selectedNode === 'eks'
                    ? 'border-emerald-500 bg-emerald-500/10 shadow-lg shadow-emerald-500/20'
                    : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex size-9 items-center justify-center rounded-xl bg-emerald-500/20 text-emerald-400">
                    <Server className="size-4" />
                  </div>
                  <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 font-mono text-[9px] font-bold text-emerald-400">AWS EKS</span>
                </div>
                <div className="mt-3 text-sm font-bold text-white">AWS EKS Cluster</div>
                <div className="mt-1 text-[11px] text-slate-400">LoadBalancer Endpoint :32574</div>
              </button>

              <button
                onClick={() => setSelectedNode('groq')}
                className={`group relative flex flex-col rounded-2xl border p-4 text-left transition ${
                  selectedNode === 'groq'
                    ? 'border-amber-500 bg-amber-500/10 shadow-lg shadow-amber-500/20'
                    : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 hover:bg-slate-900'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex size-9 items-center justify-center rounded-xl bg-amber-500/20 text-amber-400">
                    <Bot className="size-4" />
                  </div>
                  <span className="rounded-full border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 font-mono text-[9px] font-bold text-amber-400">LLM</span>
                </div>
                <div className="mt-3 text-sm font-bold text-white">Groq Llama 70B</div>
                <div className="mt-1 text-[11px] text-slate-400">Grounded Answer Output</div>
              </button>
            </div>

          </div>

          {/* NODE SPECIFICATION DETAIL INSPECTOR */}
          <div className="mt-8 rounded-2xl border border-slate-800 bg-[#080b12] p-6">
            <div className="flex flex-col items-start justify-between gap-4 border-b border-slate-800/80 pb-4 sm:flex-row sm:items-center">
              <div>
                <span className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-bold ${architectureNodes[selectedNode].color}`}>
                  {architectureNodes[selectedNode].badge}
                </span>
                <h3 className="mt-2 text-xl font-bold text-white">{architectureNodes[selectedNode].title}</h3>
                <p className="text-xs text-slate-400">{architectureNodes[selectedNode].subtitle}</p>
              </div>

              <div className="rounded-lg border border-slate-800 bg-slate-900 px-3 py-1.5 font-mono text-xs text-indigo-400">
                Tech: {architectureNodes[selectedNode].tech}
              </div>
            </div>

            <p className="mt-4 text-sm leading-relaxed text-slate-300">
              {architectureNodes[selectedNode].desc}
            </p>

            {/* Code / Config Snippet */}
            <div className="mt-4 rounded-xl border border-slate-800 bg-[#0c0f18] p-4 font-mono text-xs">
              <div className="mb-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">Live Data Payload & Specification</div>
              <pre className="overflow-x-auto text-slate-300 leading-relaxed">
                {architectureNodes[selectedNode].schema}
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* INTERACTIVE DEMO SIMULATOR */}
      <section id="live-demo" className="mx-auto max-w-7xl px-6 py-16">
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
      <section id="features" className="mx-auto max-w-7xl px-6 py-16">
        <div className="mb-12 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-indigo-500/30 bg-indigo-500/10 px-3 py-1 text-xs font-semibold text-indigo-300">
            <Zap className="size-3.5 text-indigo-400" /> Platform Features
          </div>
          <h2 className="mt-4 text-3xl font-extrabold text-white sm:text-4xl">
            Engineered for Production RAG
          </h2>
          <p className="mt-3 text-slate-400">
            Core components built for high speed, strict source attribution, and multi-cluster scaling.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          <div className="glass-panel glass-card-hover rounded-2xl p-7">
            <div className="flex size-12 items-center justify-center rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
              <Network className="size-6" />
            </div>
            <h3 className="mt-5 text-xl font-bold text-white">Formicx Task Orchestrator</h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-400">
              Splits large document indexing workloads into sub-tasks and orchestrates serverless Lambda worker execution.
            </p>
          </div>

          <div className="glass-panel glass-card-hover rounded-2xl p-7">
            <div className="flex size-12 items-center justify-center rounded-xl bg-orange-500/10 border border-orange-500/20 text-orange-400">
              <Zap className="size-6" />
            </div>
            <h3 className="mt-5 text-xl font-bold text-white">AWS Lambda Worker Tasks</h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-400">
              Serverless processing pool computing 384-dimensional dense vector embeddings in parallel into AWS S3.
            </p>
          </div>

          <div className="glass-panel glass-card-hover rounded-2xl p-7">
            <div className="flex size-12 items-center justify-center rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <Server className="size-6" />
            </div>
            <h3 className="mt-5 text-xl font-bold text-white">AWS EKS Cluster Service</h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-400">
              Isolated Kubernetes pod deployment running high-throughput FastAPI & Groq LLM inference endpoints.
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
            <span>Formicx × AWS Lambda × AWS EKS Orchestrator</span>
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
