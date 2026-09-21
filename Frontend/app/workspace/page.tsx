'use client'

import Link from 'next/link'
import { Activity, ArrowUpRight, Database, FileText, Plus, Upload, Workflow, Layers } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { EmptyState, SectionEyebrow, Shell, StatCard } from '@/components/cloudspawn-shell'

export default function WorkspacePage() {
  return (
    <Shell>
      <div className="mx-auto max-w-6xl px-5 py-8 md:px-8 md:py-12">
        <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
          <div>
            <SectionEyebrow>Overview</SectionEyebrow>
            <h1 className="text-3xl font-semibold tracking-tight">CloudSpawn Workspace</h1>
            <p className="mt-2 text-muted-foreground">Dynamic Serverless Task Orchestration & Formicx Agent Control Plane.</p>
          </div>
          <Button asChild>
            <Link href="/workspace/upload">
              <Plus className="mr-1.5 size-4" /> Upload & Cluster
            </Link>
          </Button>
        </div>

        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label="Document Engine" value="Active" detail="DOCX & PDF Support" icon={FileText} />
          <StatCard label="Agent Runtime" value="Formicx" detail="Daemon / Local IPC" icon={Workflow} />
          <StatCard label="Splitter Agent" value="docx-splitter" detail="Dynamic Clustering" icon={Layers} />
          <StatCard label="System Status" value="Ready" detail="FastAPI Backend Online" icon={Activity} />
        </div>

        <div className="mt-8 grid gap-4 lg:grid-cols-[1.25fr_0.75fr]">
          <div className="rounded-xl border bg-card p-6">
            <SectionEyebrow>Get started</SectionEyebrow>
            <h2 className="text-lg font-medium">Upload & Split Research Documents</h2>
            <p className="mt-2 max-w-lg text-sm leading-6 text-muted-foreground">
              Upload `.docx` or `.pdf` research documents. The Formicx `docx-splitter` agent will automatically extract text, compute embeddings, and dynamically partition them into topic clusters.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Button asChild>
                <Link href="/workspace/upload">
                  <Upload className="mr-1.5 size-4" /> Upload documents
                </Link>
              </Button>
              <Button variant="outline" asChild>
                <Link href="/workspace/processing">
                  <Activity className="mr-1.5 size-4" /> Processing Monitor
                </Link>
              </Button>
            </div>
          </div>

          <div className="rounded-xl border bg-card p-6">
            <SectionEyebrow>Runtime Engine</SectionEyebrow>
            <div className="flex items-center gap-2 text-sm font-medium">
              <span className="size-2 rounded-full bg-emerald-500" /> Formicx Agent Runtime
            </div>
            <p className="mt-3 text-sm leading-6 text-muted-foreground">
              Offloads heavy processing workload to Formicx agents (`docx-splitter`), preparing workload clusters for upcoming serverless AWS Lambda workers.
            </p>
            <div className="mt-5 flex items-center gap-1 text-xs text-muted-foreground font-mono">
              http://localhost:8000/docs <ArrowUpRight className="size-3" />
            </div>
          </div>
        </div>

        <div className="mt-8">
          <EmptyState
            icon={Workflow}
            title="Formicx Agent Task Orchestrator"
            description="Upload documents to launch dynamic cluster partitioning tasks."
            action={
              <Button asChild variant="outline">
                <Link href="/workspace/upload">Upload Documents</Link>
              </Button>
            }
          />
        </div>
      </div>
    </Shell>
  )
}
