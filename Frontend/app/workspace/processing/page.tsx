'use client'

import { useEffect, useState, use } from 'react'
import Link from 'next/link'
import {
  Activity,
  CheckCircle2,
  Clock3,
  Workflow,
  Layers,
  FileText,
  Loader2,
  AlertCircle,
  Sparkles,
  Server,
  FileSpreadsheet
} from 'lucide-react'
import { Shell, SectionEyebrow, EmptyState } from '@/components/cloudspawn-shell'
import { Button } from '@/components/ui/button'
import { getJobStatus, JobStatusResponse, DocumentTelemetry } from '@/lib/api'

export default function ProcessingPage({ searchParams }: { searchParams: Promise<{ job_id?: string }> }) {
  const params = use(searchParams)
  const jobId = params.job_id

  const [job, setJob] = useState<JobStatusResponse | null>(null)
  const [error, setError] = useState<string>('')

  useEffect(() => {
    if (!jobId) return

    let isMounted = true
    const fetchStatus = async () => {
      try {
        const data = await getJobStatus(jobId)
        if (!isMounted) return
        setJob(data)
        setError('')
      } catch (err: any) {
        if (isMounted) {
          setError(err?.message || 'Failed to fetch job telemetry.')
        }
      }
    }

    fetchStatus()
    const interval = setInterval(fetchStatus, 1500)

    return () => {
      isMounted = false
      clearInterval(interval)
    }
  }, [jobId])

  const formatBytes = (bytes?: number) => {
    if (!bytes) return 'Unknown size'
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  return (
    <Shell>
      <div className="mx-auto max-w-6xl px-5 py-8 md:px-8 md:py-12">
        <SectionEyebrow>Telemetry</SectionEyebrow>
        <h1 className="text-3xl font-semibold tracking-tight">Processing & Live Document Telemetry</h1>
        <p className="mt-2 text-muted-foreground">
          Real-time execution status and live telemetry of dynamic text extraction, vectorization, and Formicx agent document clustering.
        </p>

        {jobId ? (
          <div className="mt-8 grid gap-8 lg:grid-cols-[1.3fr_0.7fr]">
            {/* Main Telemetry & Document Status Section */}
            <div className="flex flex-col gap-6">
              {/* Job Overview Card */}
              <div className="rounded-xl border bg-card p-6 shadow-sm">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Formicx Agent Task</p>
                    <h2 className="mt-1 text-xl font-medium">Document Splitting & Clustering Job</h2>
                  </div>
                  <div className="flex items-center gap-2 rounded-full border bg-muted/30 px-3 py-1 text-xs">
                    <span
                      className={`size-2 rounded-full ${
                        job?.status === 'completed'
                          ? 'bg-emerald-500'
                          : job?.status === 'failed'
                          ? 'bg-destructive'
                          : 'bg-amber-500 animate-pulse'
                      }`}
                    />
                    <span className="font-mono capitalize font-medium">{job ? job.status : 'Connecting...'}</span>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mt-6 h-2.5 overflow-hidden rounded-full bg-muted">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-500"
                    style={{ width: `${job ? job.progress : 5}%` }}
                  />
                </div>

                <div className="mt-3 flex items-center justify-between text-xs text-muted-foreground">
                  <span>
                    {job ? `Processed ${job.processed_documents} of ${job.total_documents} documents` : 'Connecting to telemetry pipeline...'}
                  </span>
                  <span className="font-mono font-semibold text-foreground">{job ? `${job.progress}%` : '0%'}</span>
                </div>

                {error && (
                  <div className="mt-4 flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-xs text-destructive">
                    <AlertCircle className="size-4 shrink-0" />
                    <span>{error}</span>
                  </div>
                )}

                <div className="mt-6 grid gap-3 sm:grid-cols-3 text-xs">
                  <div className="rounded-lg border bg-muted/20 p-3">
                    <p className="text-muted-foreground">Job ID</p>
                    <p className="mt-1 truncate font-mono text-foreground font-medium">{jobId}</p>
                  </div>
                  <div className="rounded-lg border bg-muted/20 p-3">
                    <p className="text-muted-foreground">Dynamic Clusters</p>
                    <p className="mt-1 font-mono text-foreground font-semibold">
                      {job?.cluster_count !== undefined ? `${job.cluster_count} Discovered` : 'Partitioning...'}
                    </p>
                  </div>
                  <div className="rounded-lg border bg-muted/20 p-3">
                    <p className="text-muted-foreground">Failed Documents</p>
                    <p className="mt-1 font-mono text-foreground font-semibold">{job?.failed_documents ?? 0}</p>
                  </div>
                </div>
              </div>

              {/* Per-Document Telemetry Status List */}
              <div className="rounded-xl border bg-card p-6 shadow-sm">
                <div className="flex items-center justify-between border-b pb-4">
                  <div>
                    <h3 className="text-base font-semibold flex items-center gap-2">
                      <Activity className="size-4 text-emerald-500" />
                      Live Document Processing Telemetry
                    </h3>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      Individual status, file sizes, and execution steps for each document in this job
                    </p>
                  </div>
                  <span className="rounded-md border bg-muted px-2 py-0.5 text-xs font-mono text-muted-foreground">
                    {job?.documents?.length || 0} Docs
                  </span>
                </div>

                <div className="mt-4 flex flex-col gap-3">
                  {job?.documents && job.documents.length > 0 ? (
                    job.documents.map((doc: DocumentTelemetry) => (
                      <DocumentTelemetryCard key={doc.document_id} doc={doc} formatBytes={formatBytes} />
                    ))
                  ) : (
                    <div className="flex items-center justify-center py-8 text-xs text-muted-foreground gap-2">
                      <Loader2 className="size-4 animate-spin text-emerald-500" />
                      <span>Loading document telemetry feed...</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Right Column: Formicx Dynamic Clusters & Agent Pipeline */}
            <div className="flex flex-col gap-6">
              {/* Formicx Discovered Clusters */}
              <div className="rounded-xl border bg-card p-6 shadow-sm">
                <div className="flex items-center justify-between border-b pb-3">
                  <h3 className="text-sm font-semibold flex items-center gap-2">
                    <Layers className="size-4 text-emerald-500" />
                    Formicx Cluster Partitioning
                  </h3>
                  <span className="text-xs text-muted-foreground font-mono">
                    {job?.cluster_count !== undefined ? `${job.cluster_count} Clusters` : 'Pending'}
                  </span>
                </div>

                {job?.clusters && job.clusters.length > 0 ? (
                  <div className="mt-4 flex flex-col gap-3">
                    {job.clusters.map((cluster) => (
                      <div key={cluster.cluster_id} className="rounded-lg border bg-muted/20 p-3.5">
                        <div className="flex items-center justify-between text-xs font-medium">
                          <span className="flex items-center gap-1.5 text-emerald-400 font-semibold">
                            <Sparkles className="size-3.5" />
                            Cluster #{cluster.cluster_id}
                          </span>
                          <span className="text-muted-foreground font-mono">
                            {cluster.size} {cluster.size === 1 ? 'doc' : 'docs'}
                          </span>
                        </div>
                        <div className="mt-2.5 flex flex-wrap gap-1.5">
                          {cluster.documents.map((docName, idx) => (
                            <span
                              key={`${cluster.cluster_id}-${idx}`}
                              className="inline-flex items-center gap-1 rounded-md border bg-background px-2 py-0.5 text-[11px] font-mono"
                            >
                              <FileText className="size-3 text-muted-foreground" />
                              <span className="truncate max-w-[150px]">{docName}</span>
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="mt-6 flex flex-col items-center justify-center py-6 text-center text-xs text-muted-foreground">
                    <Workflow className="size-8 text-muted-foreground/50 mb-2 animate-pulse" />
                    <p className="font-medium text-foreground">Awaiting Formicx Agent Results</p>
                    <p className="mt-1 max-w-[200px] leading-relaxed">
                      TF-IDF feature extraction and cosine similarity matrix clustering in progress...
                    </p>
                  </div>
                )}
              </div>

              {/* Formicx Agent Pipeline Steps */}
              <div className="rounded-xl border bg-card p-6 shadow-sm">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Formicx Agent Pipeline</p>
                <p className="mt-1 text-xs text-muted-foreground leading-relaxed">
                  Dynamic document ingestion, scikit-learn TF-IDF feature extraction, and Formicx IPC agent partitioning.
                </p>

                <div className="mt-5 flex flex-col gap-2.5">
                  <WorkerStep
                    label="1. Document Ingestion"
                    status={job ? 'Completed' : 'Pending'}
                    active={!job}
                    icon={FileSpreadsheet}
                  />
                  <WorkerStep
                    label="2. TF-IDF & Cosine Matrix"
                    status={job?.status === 'processing' ? 'Active' : job?.status === 'completed' ? 'Completed' : 'Queued'}
                    active={job?.status === 'processing'}
                    icon={Server}
                  />
                  <WorkerStep
                    label="3. Dynamic Agglomerative Clustering"
                    status={job?.status === 'completed' ? 'Completed' : job?.status === 'failed' ? 'Failed' : 'Pending'}
                    active={job?.status === 'processing'}
                    icon={Layers}
                  />
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-8">
            <EmptyState
              icon={Activity}
              title="No active processing job"
              description="Upload documents to launch a Formicx document splitting and clustering job."
              action={
                <Button asChild>
                  <Link href="/workspace/upload">Upload Documents</Link>
                </Button>
              }
            />
          </div>
        )}
      </div>
    </Shell>
  )
}

function DocumentTelemetryCard({ doc, formatBytes }: { doc: DocumentTelemetry; formatBytes: (b?: number) => string }) {
  const isCompleted = doc.status === 'completed'
  const isFailed = doc.status === 'failed'
  const isProcessing = doc.status === 'processing'

  return (
    <div className="flex flex-col gap-2 rounded-lg border bg-card p-3.5 transition-colors hover:bg-muted/10">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="flex size-8 shrink-0 items-center justify-center rounded-md border bg-muted/30">
            <FileText className="size-4 text-emerald-400" />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-medium leading-none text-foreground">{doc.filename}</p>
            <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
              <span className="font-mono uppercase">{doc.file_type || 'DOC'}</span>
              <span>•</span>
              <span className="font-mono">{formatBytes(doc.file_size_bytes)}</span>
            </div>
          </div>
        </div>

        {/* Telemetry Status Pill */}
        <div className="flex shrink-0 items-center gap-2">
          {doc.cluster_id !== undefined && doc.cluster_id !== null && (
            <span className="rounded-md border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[11px] font-mono text-emerald-400">
              Cluster #{doc.cluster_id}
            </span>
          )}

          <div
            className={`flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium border ${
              isCompleted
                ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
                : isFailed
                ? 'border-destructive/30 bg-destructive/10 text-destructive'
                : isProcessing
                ? 'border-amber-500/30 bg-amber-500/10 text-amber-400'
                : 'border-muted bg-muted/50 text-muted-foreground'
            }`}
          >
            {isProcessing ? (
              <Loader2 className="size-3 animate-spin text-amber-400" />
            ) : isCompleted ? (
              <CheckCircle2 className="size-3 text-emerald-400" />
            ) : isFailed ? (
              <AlertCircle className="size-3 text-destructive" />
            ) : (
              <Clock3 className="size-3 text-muted-foreground" />
            )}
            <span className="capitalize font-mono">{doc.status}</span>
          </div>
        </div>
      </div>

      {/* Processing Telemetry Step Bar */}
      {doc.processing_step && (
        <div className="mt-1 flex items-center gap-2 rounded-md bg-muted/30 px-2.5 py-1 text-[11px] text-muted-foreground">
          <Activity className="size-3 text-emerald-400 shrink-0" />
          <span className="font-mono truncate">{doc.processing_step}</span>
        </div>
      )}
    </div>
  )
}

function WorkerStep({
  label,
  status,
  active,
  icon: Icon
}: {
  label: string
  status: string
  active?: boolean
  icon: React.ElementType
}) {
  return (
    <div
      className={`flex items-center gap-3 rounded-lg border px-3 py-2.5 text-xs transition-colors ${
        active ? 'border-emerald-500/40 bg-emerald-500/5' : 'bg-card'
      }`}
    >
      <Icon className={`size-4 ${active ? 'text-emerald-400 animate-pulse' : 'text-muted-foreground'}`} />
      <span className="flex-1 font-medium">{label}</span>
      <span className="font-mono text-[11px] text-muted-foreground capitalize">{status}</span>
    </div>
  )
}

