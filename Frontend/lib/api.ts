const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Request failed')
  }
  return response.json()
}

export interface DocumentItem {
  document_id: string
  filename: string
  status: string
  file_size?: number
  file_type?: string
  processing_step?: string
  cluster_id?: number
  uploaded_at?: string
}

export interface DocumentDetailResponse {
  document_id: string
  filename: string
  file_type?: string
  file_size?: number
  status: string
  processing_step?: string
  cluster_id?: number
  cluster_documents?: string[]
  cluster_size?: number
  uploaded_at?: string
  job_id?: string
}

export interface UploadResponse {
  documents: DocumentItem[]
}

export interface ClusterItem {
  cluster_id: number
  size: number
  documents: string[]
}

export interface DocumentTelemetry {
  document_id: string
  filename: string
  file_type?: string
  file_size_bytes?: number
  status: 'pending' | 'processing' | 'completed' | 'failed' | string
  processing_step?: string
  cluster_id?: number
}

export interface JobStatusResponse {
  job_id: string
  status: 'queued' | 'processing' | 'completed' | 'failed'
  total_documents: number
  processed_documents: number
  failed_documents: number
  progress: number
  cluster_count?: number
  clusters?: ClusterItem[]
  documents?: DocumentTelemetry[]
  created_at?: string
  started_at?: string
  completed_at?: string
}


export interface LogEntry {
  id: string
  timestamp: string
  level: 'INFO' | 'WARNING' | 'ERROR' | string
  logger: string
  message: string
}

export interface LogResponse {
  total: number
  logs: LogEntry[]
}

export interface SourceItem {
  document_id: string
  filename: string
  chunk_index: number
}

export interface ChatResponse {
  conversation_id: string
  answer: string
  sources: SourceItem[]
}

export async function uploadDocuments(files: File[]): Promise<UploadResponse> {
  const body = new FormData()
  files.forEach((file) => body.append('files', file))
  const response = await fetch(`${API_URL}/api/documents/upload`, { method: 'POST', body })
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || 'Upload failed')
  }
  return response.json()
}

export function buildKnowledgeBase(payload: { document_ids: string[] }) {
  return request<{ job_id: string; status: string }>('/api/jobs/build', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function getJobStatus(jobId: string) {
  return request<JobStatusResponse>(`/api/jobs/${jobId}`)
}

export function getDocuments() {
  return request<UploadResponse>('/api/documents')
}

export function getDocumentDetail(documentId: string) {
  return request<DocumentDetailResponse>(`/api/documents/${documentId}`)
}

export function getLogs(limit: number = 200, level?: string) {
  const params = new URLSearchParams()
  params.append('limit', String(limit))
  if (level && level !== 'ALL') {
    params.append('level', level)
  }
  return request<LogResponse>(`/api/logs?${params.toString()}`)
}

export function clearLogs() {
  return request<{ status: string; message: string }>('/api/logs', {
    method: 'DELETE',
  })
}

export function sendChatMessage(message: string, conversationId?: string) {
  return request<ChatResponse>('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message, conversation_id: conversationId }),
  })
}
