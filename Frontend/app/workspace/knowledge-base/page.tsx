'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import {
  Database,
  FileText,
  CheckCircle2,
  Workflow,
  X,
  Layers,
  Sparkles,
  Clock3,
  Activity,
  ArrowRight,
  Loader2,
  AlertCircle
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { EmptyState, SectionEyebrow, Shell, StatCard } from '@/components/cloudspawn-shell'
import { getDocuments, getDocumentDetail, DocumentItem, DocumentDetailResponse } from '@/lib/api'

export default function KnowledgeBasePage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // State for document splitup & telemetry detail modal
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null)
  const [docDetail, setDocDetail] = useState<DocumentDetailResponse | null>(null)
  const [loadingDetail, setLoadingDetail] = useState(false)
  const [detailError, setDetailError] = useState('')

  useEffect(() => {
    let isMounted = true
    getDocuments()
      .then((res) => {
        if (isMounted) {
          setDocuments(res.documents || [])
          setError('')
        }
      })
      .catch(() => {
        if (isMounted) {
          setError('Could not connect to FastAPI backend at http://localhost:8000')
        }
      })
      .finally(() => {
        if (isMounted) setLoading(false)
      })

    return () => {
      isMounted = false
    }
  }, [])

  const handleSelectDocument = async (documentId: string) => {
    setSelectedDocId(documentId)
    setLoadingDetail(true)
    setDetailError('')
    setDocDetail(null)

    try {
      const data = await getDocumentDetail(documentId)
      setDocDetail(data)
    } catch (err: any) {
      setDetailError(err?.message || 'Failed to load document telemetry.')
    } finally {
      setLoadingDetail(false)
    }
  }

  const formatBytes = (bytes?: number) => {
    if (!bytes) return 'Unknown size'
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
  }

  const completedCount = documents.filter((d) => d.status === 'completed').length
  const statusLabel = documents.length === 0 ? 'Empty' : completedCount === documents.length ? 'Ready' : 'Processing'

  return (
    <Shell>
      <div className="mx-auto max-w-6xl px-5 py-8 md:px-8 md:py-12">
        <SectionEyebrow>Workspace</SectionEyebrow>
        <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">Knowledge Base & Telemetry</h1>
            <p className="mt-2 text-muted-foreground">
              Click any document to inspect Formicx agent dynamic cluster splitups and processing telemetry.
            </p>
          </div>
          <Button asChild>
            <Link href="/workspace/upload">Upload & Build</Link>
          </Button>
        </div>

        {/* Stat Cards */}
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            label="Total Documents"
            value={loading ? '...' : String(documents.length)}
            detail="Uploaded DOCX/PDF files"
            icon={FileText}
          />
          <StatCard
            label="Processed"
            value={loading ? '...' : String(completedCount)}
            detail="Clustered by Formicx Agent"
            icon={CheckCircle2}
          />
          <StatCard
            label="Agent Engine"
            value="Formicx"
            detail="docx-splitter agent"
            icon={Workflow}
          />
          <StatCard
            label="Status"
            value={loading ? '...' : statusLabel}
            detail={statusLabel === 'Ready' ? 'Formicx agent idle' : 'Awaiting build job'}
            icon={Database}
          />
        </div>

        {error && (
          <div className="mt-6 rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
            {error}
          </div>
        )}

        {/* Document List Table */}
        {!loading && documents.length > 0 ? (
          <div className="mt-8 rounded-xl border bg-card shadow-sm">
            <div className="flex items-center justify-between border-b p-5">
              <div>
                <h2 className="font-medium">Uploaded Documents</h2>
                <p className="mt-1 text-xs text-muted-foreground">
                  Click any document row to view cluster splitups and file telemetry metrics
                </p>
              </div>
              <Button asChild variant="outline" size="sm">
                <Link href="/workspace/processing">View Monitor</Link>
              </Button>
            </div>
            <div className="flex flex-col divide-y">
              {documents.map((doc) => (
                <div
                  key={doc.document_id}
                  onClick={() => handleSelectDocument(doc.document_id)}
                  className={`flex cursor-pointer items-center justify-between px-5 py-4 transition-colors hover:bg-muted/30 ${
                    selectedDocId === doc.document_id ? 'bg-muted/40' : ''
                  }`}
                >
                  <div className="flex items-center gap-3.5 min-w-0 flex-1 pr-4">
                    <div className="flex size-9 shrink-0 items-center justify-center rounded-lg border bg-muted/40">
                      <FileText className="size-4 text-emerald-400" />
                    </div>
                    <div className="truncate">
                      <p className="truncate text-sm font-medium text-foreground hover:underline">
                        {doc.filename}
                      </p>
                      <div className="mt-0.5 flex items-center gap-2 text-xs text-muted-foreground">
                        <span className="font-mono">ID: {doc.document_id.slice(0, 8)}...</span>
                        {doc.processing_step && (
                          <>
                            <span>•</span>
                            <span className="font-mono text-emerald-400 truncate max-w-[220px]">
                              {doc.processing_step}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0 text-xs">
                    {doc.cluster_id !== undefined && doc.cluster_id !== null && (
                      <span className="rounded-md border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 font-mono text-emerald-400">
                        Cluster #{doc.cluster_id}
                      </span>
                    )}

                    {doc.file_size && (
                      <span className="text-muted-foreground font-mono">{formatBytes(doc.file_size)}</span>
                    )}

                    <span
                      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 font-medium capitalize border ${
                        doc.status === 'completed'
                          ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
                          : doc.status === 'failed'
                          ? 'border-destructive/30 bg-destructive/10 text-destructive'
                          : 'border-amber-500/30 bg-amber-500/10 text-amber-400'
                      }`}
                    >
                      <span
                        className={`size-1.5 rounded-full ${
                          doc.status === 'completed'
                            ? 'bg-emerald-500'
                            : doc.status === 'failed'
                            ? 'bg-destructive'
                            : 'bg-amber-500'
                        }`}
                      />
                      {doc.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : !loading && documents.length === 0 ? (
          <div className="mt-8">
            <EmptyState
              icon={Database}
              title="No documents yet"
              description="Upload DOCX or PDF files to start your first workload."
              action={
                <Button asChild>
                  <Link href="/workspace/upload">Upload documents</Link>
                </Button>
              }
            />
          </div>
        ) : null}

        {/* Document Splitup & Telemetry Modal / Drawer */}
        {selectedDocId && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
            <div className="relative w-full max-w-2xl rounded-xl border bg-card p-6 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
              {/* Close Button */}
              <button
                onClick={() => setSelectedDocId(null)}
                className="absolute right-4 top-4 rounded-md p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground"
              >
                <X className="size-5" />
              </button>

              {loadingDetail ? (
                <div className="flex flex-col items-center justify-center py-12 text-center text-xs text-muted-foreground gap-3">
                  <Loader2 className="size-6 animate-spin text-emerald-500" />
                  <span>Loading document telemetry & dynamic splitup details...</span>
                </div>
              ) : detailError ? (
                <div className="p-4 text-xs text-destructive flex items-center gap-2">
                  <AlertCircle className="size-4 shrink-0" />
                  <span>{detailError}</span>
                </div>
              ) : docDetail ? (
                <div className="flex flex-col gap-6">
                  {/* Header */}
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="rounded-md border bg-muted px-2 py-0.5 text-xs font-mono uppercase text-muted-foreground">
                        {docDetail.file_type || 'DOCX'}
                      </span>
                      <span
                        className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-mono capitalize border ${
                          docDetail.status === 'completed'
                            ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400'
                            : 'border-amber-500/30 bg-amber-500/10 text-amber-400'
                        }`}
                      >
                        {docDetail.status}
                      </span>
                    </div>
                    <h2 className="mt-2 text-xl font-semibold leading-tight text-foreground truncate">
                      {docDetail.filename}
                    </h2>
                    <p className="mt-1 font-mono text-xs text-muted-foreground">
                      Document ID: {docDetail.document_id}
                    </p>
                  </div>

                  {/* Telemetry Overview Grid */}
                  <div className="grid gap-3 sm:grid-cols-3 text-xs">
                    <div className="rounded-lg border bg-muted/20 p-3">
                      <p className="text-muted-foreground">File Size</p>
                      <p className="mt-1 font-mono font-medium text-foreground">{formatBytes(docDetail.file_size)}</p>
                    </div>
                    <div className="rounded-lg border bg-muted/20 p-3">
                      <p className="text-muted-foreground">Formicx Cluster</p>
                      <p className="mt-1 font-mono font-semibold text-emerald-400">
                        {docDetail.cluster_id !== undefined && docDetail.cluster_id !== null
                          ? `Cluster #${docDetail.cluster_id}`
                          : 'Not Partitioned'}
                      </p>
                    </div>
                    <div className="rounded-lg border bg-muted/20 p-3">
                      <p className="text-muted-foreground">Processing Step</p>
                      <p className="mt-1 font-mono truncate text-foreground">
                        {docDetail.processing_step || 'Uploaded'}
                      </p>
                    </div>
                  </div>

                  {/* Dynamic Cluster Splitups Section */}
                  <div className="rounded-lg border bg-muted/10 p-4">
                    <div className="flex items-center justify-between border-b pb-3">
                      <h3 className="text-sm font-semibold flex items-center gap-2 text-foreground">
                        <Layers className="size-4 text-emerald-400" />
                        Cluster Splitup & Co-partitioned Files
                      </h3>
                      {docDetail.cluster_size !== undefined && (
                        <span className="text-xs font-mono text-muted-foreground">
                          {docDetail.cluster_size} {docDetail.cluster_size === 1 ? 'document' : 'documents'} total
                        </span>
                      )}
                    </div>

                    {docDetail.cluster_documents && docDetail.cluster_documents.length > 0 ? (
                      <div className="mt-3 flex flex-col gap-2">
                        <p className="text-xs text-muted-foreground">
                          Formicx <span className="font-mono text-foreground">docx-splitter</span> agent grouped this file with the following documents based on TF-IDF cosine similarity:
                        </p>
                        <div className="mt-1 flex flex-col gap-1.5 max-h-48 overflow-y-auto pr-1">
                          {docDetail.cluster_documents.map((filename, idx) => (
                            <div
                              key={idx}
                              className={`flex items-center justify-between rounded-md border p-2 text-xs font-mono transition-colors ${
                                filename === docDetail.filename
                                  ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300 font-semibold'
                                  : 'bg-background text-foreground'
                              }`}
                            >
                              <div className="flex items-center gap-2 truncate">
                                <FileText className="size-3.5 text-muted-foreground shrink-0" />
                                <span className="truncate">{filename}</span>
                              </div>
                              {filename === docDetail.filename && (
                                <span className="rounded bg-emerald-500/20 px-1.5 py-0.5 text-[10px] text-emerald-400">
                                  Current File
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <div className="py-4 text-center text-xs text-muted-foreground">
                        <p>No cluster partition splitups found for this document yet.</p>
                      </div>
                    )}
                  </div>

                  {/* Footer Actions */}
                  <div className="flex items-center justify-between border-t pt-4">
                    <Button variant="outline" size="sm" onClick={() => setSelectedDocId(null)}>
                      Close
                    </Button>

                    {docDetail.job_id && (
                      <Button asChild size="sm" className="gap-1.5">
                        <Link href={`/workspace/processing?job_id=${docDetail.job_id}`}>
                          View Job Telemetry <ArrowRight className="size-3.5" />
                        </Link>
                      </Button>
                    )}
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        )}
      </div>
    </Shell>
  )
}

