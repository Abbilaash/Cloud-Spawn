const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!response.ok) throw new Error('Request failed')
  return response.json()
}

export function uploadDocuments(files: File[]) {
  const body = new FormData()
  files.forEach((file) => body.append('files', file))
  return fetch(`${API_URL}/api/documents/upload`, { method: 'POST', body }).then((response) => {
    if (!response.ok) throw new Error('Upload failed')
    return response.json()
  })
}

export function buildKnowledgeBase(payload?: { document_ids?: string[] }) {
  return request<{ job_id: string }>('/api/jobs/build', { method: 'POST', body: JSON.stringify(payload || {}) })
}

export function getJobStatus(jobId: string) { return request(`/api/jobs/${jobId}`) }
export function getDocuments() { return request('/api/documents') }
export function sendChatMessage(message: string, conversationId?: string) {
  return request<{ answer: string; sources?: { filename: string; chunk?: number }[] }>('/api/chat', { method: 'POST', body: JSON.stringify({ message, conversation_id: conversationId }) })
}
export function getConversation(conversationId: string) { return request(`/api/conversations/${conversationId}`) }
