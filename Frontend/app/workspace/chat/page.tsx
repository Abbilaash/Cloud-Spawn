'use client'

import { FormEvent, useState } from 'react'
import { ArrowUp, Bot, FileText, Loader2, MessageSquare, Sparkles, User } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Shell, SectionEyebrow } from '@/components/cloudspawn-shell'
import { sendChatMessage, SourceItem } from '@/lib/api'

type Message = {
  role: 'user' | 'assistant'
  content: string
  sources?: SourceItem[]
}

const prompts = [
  'What are the key findings discussed in the documents?',
  'Compare the main concepts presented.',
  'What technical limitations are mentioned?',
  'Summarize the primary conclusions.',
]

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [conversationId, setConversationId] = useState<string | undefined>(undefined)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async (event?: FormEvent) => {
    event?.preventDefault()
    if (!input.trim() || loading) return

    const question = input.trim()
    setInput('')
    setError('')
    setMessages((current) => [...current, { role: 'user', content: question }])
    setLoading(true)

    try {
      const response = await sendChatMessage(question, conversationId)

      // Store conversation_id for multi-turn thread persistence
      if (response.conversation_id) {
        setConversationId(response.conversation_id)
      }

      setMessages((current) => [
        ...current,
        {
          role: 'assistant',
          content: response.answer,
          sources: response.sources,
        },
      ])
    } catch (err: any) {
      setError(err?.message || 'Unable to connect to the backend. Please ensure FastAPI is running at http://localhost:8000.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Shell>
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-5xl flex-col px-5 py-8 md:px-8 md:py-12">
        <div className="flex items-end justify-between">
          <div>
            <SectionEyebrow>Knowledge Base</SectionEyebrow>
            <h1 className="text-3xl font-semibold tracking-tight">RAG Assistant</h1>
            <p className="mt-2 text-muted-foreground">Ask grounded questions about your indexed documents.</p>
          </div>
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <span className="size-1.5 rounded-full bg-emerald-500" />
            Connected
          </div>
        </div>

        <div className="mt-8 flex flex-1 flex-col rounded-xl border bg-card">
          <div className="flex-1 p-5 md:p-8">
            {messages.length === 0 ? (
              <div className="flex min-h-[390px] flex-col items-center justify-center text-center">
                <span className="grid size-12 place-items-center rounded-xl border bg-muted/40">
                  <Sparkles className="size-5 text-muted-foreground" />
                </span>
                <h2 className="mt-5 text-lg font-medium">Ask your knowledge base</h2>
                <p className="mt-2 text-sm text-muted-foreground">Start with a question or try one of these sample prompts.</p>
                <div className="mt-6 grid w-full max-w-xl gap-2 sm:grid-cols-2">
                  {prompts.map((prompt) => (
                    <button
                      key={prompt}
                      onClick={() => setInput(prompt)}
                      className="rounded-lg border px-3 py-3 text-left text-sm text-muted-foreground transition hover:border-foreground/30 hover:text-foreground"
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex flex-col gap-6">
                {messages.map((message, index) => (
                  <div key={index} className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : ''}`}>
                    {message.role === 'assistant' && (
                      <span className="mt-1 grid size-7 shrink-0 place-items-center rounded-md border bg-muted/40">
                        <Bot className="size-3.5 text-emerald-400" />
                      </span>
                    )}

                    <div
                      className={`max-w-[80%] rounded-xl px-4 py-3 text-sm leading-6 ${
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'border bg-background shadow-sm'
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{message.content}</p>

                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-4 border-t pt-3">
                          <p className="mb-2 text-xs font-medium text-muted-foreground">Sources Cited</p>
                          <div className="flex flex-wrap gap-2">
                            {message.sources.map((source, idx) => (
                              <div
                                key={`${source.document_id}-${source.chunk_index}-${idx}`}
                                className="flex items-center gap-1.5 rounded-md border bg-muted/30 px-2 py-1 text-xs text-muted-foreground"
                              >
                                <FileText className="size-3 shrink-0" />
                                <span className="truncate max-w-[200px]">{source.filename}</span>
                                <span className="font-mono text-[10px] opacity-75">#{source.chunk_index}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {message.role === 'user' && (
                      <span className="mt-1 grid size-7 shrink-0 place-items-center rounded-md border bg-primary/20 text-primary">
                        <User className="size-3.5" />
                      </span>
                    )}
                  </div>
                ))}

                {loading && (
                  <div className="flex items-center gap-3 text-sm text-muted-foreground">
                    <Loader2 className="size-4 animate-spin text-emerald-500" />
                    Generating grounded answer...
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="border-t p-4">
            {error && <p className="mb-3 text-xs text-destructive">{error}</p>}
            <form onSubmit={submit} className="flex items-center gap-2 rounded-lg border bg-background p-1.5">
              <MessageSquare className="ml-2 size-4 text-muted-foreground" />
              <input
                value={input}
                onChange={(event) => setInput(event.target.value)}
                placeholder="Ask something about your uploaded documents..."
                className="min-w-0 flex-1 bg-transparent px-2 py-2 text-sm outline-none"
              />
              <Button size="icon" type="submit" disabled={!input.trim() || loading} aria-label="Send message">
                <ArrowUp />
              </Button>
            </form>
          </div>
        </div>
      </div>
    </Shell>
  )
}
