'use client'

import Link from 'next/link'
import { ChangeEvent, useState } from 'react'
import { Check, FileText, Loader2, UploadCloud, X, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Shell, SectionEyebrow } from '@/components/cloudspawn-shell'
import { buildKnowledgeBase, uploadDocuments, clearAllDocuments } from '@/lib/api'

export default function UploadPage() {
  const [files, setFiles] = useState<File[]>([])
  const [busy, setBusy] = useState(false)
  const [purging, setPurging] = useState(false)
  const [error, setError] = useState('')
  const [infoMessage, setInfoMessage] = useState('')

  const select = (event: ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || []).filter((file) => {
      const name = file.name.toLowerCase()
      return name.endsWith('.docx') || name.endsWith('.pdf')
    })
    setFiles((current) => [...current, ...selectedFiles])
  }

  const handlePurgeServerDocs = async () => {
    if (!confirm('Are you sure you want to purge all stored documents from disk, S3, and database?')) return
    setPurging(true)
    setError('')
    setInfoMessage('')
    try {
      const res = await clearAllDocuments()
      setInfoMessage(res.message || 'All stored documents purged successfully.')
      setFiles([])
    } catch (err: any) {
      setError(err?.message || 'Failed to purge documents.')
    } finally {
      setPurging(false)
    }
  }

  const build = async () => {
    if (!files.length) return
    setBusy(true)
    setError('')

    try {
      // 1. Upload DOCX/PDF files to backend
      const uploadResult = await uploadDocuments(files)
      const docIds = uploadResult.documents.map((d) => d.document_id)

      if (!docIds.length) {
        throw new Error('No valid document IDs returned from upload.')
      }

      // 2. Trigger knowledge base ingestion job
      const jobResult = await buildKnowledgeBase({ document_ids: docIds })

      // 3. Redirect to processing status monitor
      window.location.href = `/workspace/processing?job_id=${jobResult.job_id}`
    } catch (err: any) {
      setError(err?.message || 'Unable to connect to the backend. Please ensure FastAPI is running at http://localhost:8000.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Shell>
      <div className="mx-auto max-w-4xl px-5 py-8 md:px-8 md:py-12">
        <SectionEyebrow>Documents</SectionEyebrow>
        <h1 className="text-3xl font-semibold tracking-tight">Build Knowledge Base</h1>
        <p className="mt-2 text-muted-foreground">Upload DOCX or PDF documents and create your searchable AI knowledge base.</p>

        <label className="mt-8 flex min-h-64 cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed bg-card/50 px-6 text-center transition hover:border-foreground/40 hover:bg-card">
          <input type="file" accept=".docx,.pdf" multiple className="sr-only" onChange={select} />
          <span className="grid size-12 place-items-center rounded-lg border bg-muted/40">
            <UploadCloud className="size-5 text-muted-foreground" />
          </span>
          <span className="mt-4 font-medium">Drop DOCX or PDF files here</span>
          <span className="mt-1 text-sm text-muted-foreground">or click to browse · Supports .docx and .pdf</span>
        </label>

        {files.length > 0 && (
          <div className="mt-8 rounded-xl border bg-card">
            <div className="flex items-center justify-between border-b p-5">
              <div>
                <h2 className="font-medium">Selected documents</h2>
                <p className="mt-1 text-xs text-muted-foreground">
                  {files.length} {files.length === 1 ? 'document' : 'documents'} selected
                </p>
              </div>
              <Button variant="ghost" size="sm" onClick={() => setFiles([])}>
                Clear
              </Button>
            </div>
            <div className="flex flex-col divide-y">
              {files.map((file, index) => (
                <div key={`${file.name}-${index}`} className="flex items-center gap-3 px-5 py-3">
                  <FileText className="size-4 text-muted-foreground" />
                  <span className="min-w-0 flex-1 truncate text-sm">{file.name}</span>
                  <span className="text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                  <Check className="size-4 text-emerald-500" />
                </div>
              ))}
            </div>
          </div>
        )}

        {infoMessage && (
          <div className="mt-5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-400 flex items-center justify-between">
            <span>{infoMessage}</span>
          </div>
        )}

        {error && (
          <div className="mt-5 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            {error}
          </div>
        )}

        <div className="mt-6 flex items-center justify-between gap-4">
          <Button
            variant="outline"
            onClick={handlePurgeServerDocs}
            disabled={purging || busy}
            className="gap-2 text-xs text-destructive hover:bg-destructive/10 hover:text-destructive"
          >
            {purging ? <Loader2 className="size-3.5 animate-spin" /> : <Trash2 className="size-3.5" />}
            Purge Server Documents & S3
          </Button>

          <Button disabled={!files.length || busy} onClick={build}>
            {busy ? (
              <>
                <Loader2 className="mr-2 size-4 animate-spin" /> Building...
              </>
            ) : (
              'Build Knowledge Base'
            )}
          </Button>
        </div>
      </div>
    </Shell>
  )
}
