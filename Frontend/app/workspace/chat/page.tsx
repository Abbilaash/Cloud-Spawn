'use client'

import { FormEvent, useEffect, useRef, useState } from 'react'
import {
  ArrowUp,
  Bot,
  Check,
  ChevronDown,
  ChevronUp,
  Copy,
  Database,
  FileText,
  Layers,
  Loader2,
  MessageSquare,
  RefreshCw,
  Search,
  Sparkles,
  User,
  Zap,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Shell, SectionEyebrow } from '@/components/cloudspawn-shell'
import {
  sendChatMessage,
  searchRAGContext,
  SourceItem,
  RAGSearchResultItem,
} from '@/lib/api'

type MessageRole = 'user' | 'assistant'

interface ChatMessage {
  id: string
  role: MessageRole
  content: string
  timestamp: string
  sources?: SourceItem[]
  rawVectorResults?: RAGSearchResultItem[]
  mode?: 'chat' | 'vector'
}

const SAMPLE_PROMPTS = [
  'What are the key concepts discussed in the uploaded documents?',
  'Summarize the primary conclusions and findings.',
  'How does the vector orchestration pipeline work?',
  'What technical architecture steps are mentioned?',
]

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [mode, setMode] = useState<'chat' | 'vector'>('chat')
  const [topK, setTopK] = useState<number>(5)
  const [conversationId, setConversationId] = useState<string | undefined>(undefined)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [copiedId, setCopiedId] = useState<string | null>(null)
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({})

  const chatEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom of chat when messages update
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const toggleSourceExpand = (messageId: string) => {
    setExpandedSources((prev) => ({
      ...prev,
      [messageId]: !prev[messageId],
    }))
  }

  const handleClearChat = () => {
    setMessages([])
    setConversationId(undefined)
    setError('')
  }

  const handleSubmit = async (event?: FormEvent) => {
    event?.preventDefault()
    if (!input.trim() || loading) return

    const question = input.trim()
    setInput('')
    setError('')

    const userMessageId = `msg-${Date.now()}`
    const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

    const userMsg: ChatMessage = {
      id: userMessageId,
      role: 'user',
      content: question,
      timestamp,
      mode,
    }

    setMessages((current) => [...current, userMsg])
    setLoading(true)

    try {
      if (mode === 'chat') {
        // Mode 1: Grounded LLM RAG Chat (/api/chat)
        const response = await sendChatMessage(question, conversationId)

        if (response.conversation_id) {
          setConversationId(response.conversation_id)
        }

        const assistantMsg: ChatMessage = {
          id: `msg-${Date.now() + 1}`,
          role: 'assistant',
          content: response.answer,
          sources: response.sources,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          mode: 'chat',
        }

        setMessages((current) => [...current, assistantMsg])
      } else {
        // Mode 2: Direct FAISS Vector Search Explorer (/api/rag/search)
        const response = await searchRAGContext(question, topK)

        let answerContent = `Retrieved ${response.total_matches} vector matching text chunk(s) from the master FAISS index.`
        if (response.total_matches === 0) {
          answerContent = `No matching vector text chunks found in the index for "${question}".`
        }

        const vectorMsg: ChatMessage = {
          id: `msg-${Date.now() + 1}`,
          role: 'assistant',
          content: answerContent,
          rawVectorResults: response.results,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          mode: 'vector',
        }

        setMessages((current) => [...current, vectorMsg])
      }
    } catch (err: any) {
      console.error('RAG Chat Error:', err)
      setError(
        err?.message || 'Failed to communicate with CloudSpawn backend service. Please check API status.'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <Shell>
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-5xl flex-col px-4 py-6 md:px-8 md:py-10">
        
        {/* Page Header */}
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b pb-6">
          <div>
            <SectionEyebrow>RAG Inference</SectionEyebrow>
            <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">Knowledge Base Chat</h1>
            <p className="mt-1 text-sm text-muted-foreground">
              Query vector-indexed documents or explore raw FAISS embedding matches.
            </p>
          </div>

          <div className="flex items-center gap-3">
            {/* Mode Switcher Pills */}
            <div className="flex items-center rounded-lg border bg-muted/30 p-1 text-xs">
              <button
                onClick={() => setMode('chat')}
                className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 font-medium transition ${
                  mode === 'chat'
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <Sparkles className="size-3.5 text-emerald-400" />
                Grounded Chat
              </button>

              <button
                onClick={() => setMode('vector')}
                className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 font-medium transition ${
                  mode === 'vector'
                    ? 'bg-background text-foreground shadow-sm'
                    : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <Search className="size-3.5 text-blue-400" />
                Vector Search
              </button>
            </div>

            {/* Clear Chat Button */}
            {messages.length > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearChat}
                className="gap-1.5 text-xs text-muted-foreground hover:text-foreground"
              >
                <RefreshCw className="size-3.5" />
                Clear
              </Button>
            )}
          </div>
        </div>

        {/* Main Chat Interface Container */}
        <div className="mt-6 flex flex-1 flex-col rounded-xl border bg-card shadow-sm overflow-hidden">
          
          {/* Scrollable Message List */}
          <div className="flex-1 overflow-y-auto p-4 md:p-6 min-h-[420px] max-h-[calc(100vh-22rem)]">
            {messages.length === 0 ? (
              <div className="flex min-h-[360px] flex-col items-center justify-center text-center px-4">
                <span className="grid size-14 place-items-center rounded-2xl border bg-muted/40 shadow-inner">
                  {mode === 'chat' ? (
                    <Sparkles className="size-6 text-emerald-400" />
                  ) : (
                    <Search className="size-6 text-blue-400" />
                  )}
                </span>
                
                <h2 className="mt-5 text-lg font-medium tracking-tight">
                  {mode === 'chat'
                    ? 'Ask your Knowledge Base'
                    : 'Search Master Vector FAISS Database'}
                </h2>
                <p className="mt-2 max-w-md text-sm text-muted-foreground">
                  {mode === 'chat'
                    ? 'Query grounded information extracted from uploaded DOCX/PDF files. Answers are verified using FAISS context retrieval.'
                    : 'Perform direct cosine similarity vector search to inspect matching chunk text snippets and scores.'}
                </p>

                {/* Sample Prompts */}
                <div className="mt-8 grid w-full max-w-2xl gap-2.5 sm:grid-cols-2">
                  {SAMPLE_PROMPTS.map((prompt) => (
                    <button
                      key={prompt}
                      onClick={() => {
                        setInput(prompt)
                        inputRef.current?.focus()
                      }}
                      className="group flex items-start gap-2.5 rounded-xl border bg-background/50 p-3.5 text-left text-xs leading-relaxed text-muted-foreground transition hover:border-foreground/30 hover:bg-accent/40 hover:text-foreground"
                    >
                      <MessageSquare className="mt-0.5 size-3.5 shrink-0 text-emerald-500 opacity-70 group-hover:opacity-100" />
                      <span>{prompt}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex flex-col gap-6">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex gap-3.5 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {/* Assistant Avatar */}
                    {message.role === 'assistant' && (
                      <span className="mt-1 grid size-8 shrink-0 place-items-center rounded-lg border bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                        {message.mode === 'vector' ? (
                          <Database className="size-4 text-blue-400" />
                        ) : (
                          <Bot className="size-4 text-emerald-400" />
                        )}
                      </span>
                    )}

                    {/* Message Bubble */}
                    <div
                      className={`relative group max-w-[85%] rounded-2xl p-4 text-sm leading-6 ${
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground rounded-tr-none'
                          : 'border bg-background shadow-xs rounded-tl-none'
                      }`}
                    >
                      {/* Message Content */}
                      <div className="whitespace-pre-wrap">{message.content}</div>

                      {/* Cited Sources for Grounded Chat Mode */}
                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-4 border-t pt-3">
                          <button
                            onClick={() => toggleSourceExpand(message.id)}
                            className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground transition mb-2"
                          >
                            <FileText className="size-3.5 text-emerald-400" />
                            <span>Cited Sources ({message.sources.length})</span>
                            {expandedSources[message.id] ? (
                              <ChevronUp className="size-3" />
                            ) : (
                              <ChevronDown className="size-3" />
                            )}
                          </button>

                          <div className="flex flex-wrap gap-2">
                            {message.sources.map((source, idx) => (
                              <div
                                key={`${source.document_id}-${source.chunk_index}-${idx}`}
                                className="flex items-center gap-1.5 rounded-lg border bg-muted/40 px-2.5 py-1 text-xs text-muted-foreground"
                              >
                                <FileText className="size-3 shrink-0 text-emerald-400" />
                                <span className="truncate max-w-[180px] font-medium text-foreground">
                                  {source.filename}
                                </span>
                                <span className="font-mono text-[10px] opacity-75">
                                  #Chunk {source.chunk_index}
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Raw Vector Results for Vector Search Mode */}
                      {message.rawVectorResults && message.rawVectorResults.length > 0 && (
                        <div className="mt-4 border-t pt-3 flex flex-col gap-3">
                          <p className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                            <Layers className="size-3.5 text-blue-400" />
                            Nearest Vector Matches ({message.rawVectorResults.length})
                          </p>
                          {message.rawVectorResults.map((item, idx) => (
                            <div
                              key={item.chunk_id || idx}
                              className="rounded-xl border bg-card p-3 text-xs leading-relaxed"
                            >
                              <div className="flex items-center justify-between mb-1.5 font-medium">
                                <span className="truncate text-foreground max-w-[220px]">
                                  {item.filename}
                                </span>
                                <span className="rounded-md bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 text-[10px] font-mono text-blue-400">
                                  Score: {item.score ? item.score.toFixed(4) : '0.0000'}
                                </span>
                              </div>
                              <p className="text-muted-foreground bg-muted/30 p-2 rounded-md font-mono text-[11px] whitespace-pre-wrap">
                                "{item.text}"
                              </p>
                              <div className="mt-1.5 flex items-center gap-2 text-[10px] text-muted-foreground">
                                <span>Chunk Index: #{item.chunk_index}</span>
                                <span>•</span>
                                <span className="truncate">Doc ID: {item.document_id}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}

                      {/* Footer Metadata & Actions */}
                      <div className="mt-2.5 flex items-center justify-between text-[11px] text-muted-foreground opacity-80 group-hover:opacity-100 transition">
                        <span>{message.timestamp}</span>
                        {message.role === 'assistant' && (
                          <button
                            onClick={() => handleCopy(message.id, message.content)}
                            className="flex items-center gap-1 hover:text-foreground transition ml-2"
                            title="Copy response"
                          >
                            {copiedId === message.id ? (
                              <>
                                <Check className="size-3 text-emerald-400" />
                                <span className="text-emerald-400">Copied</span>
                              </>
                            ) : (
                              <>
                                <Copy className="size-3" />
                                <span>Copy</span>
                              </>
                            )}
                          </button>
                        )}
                      </div>
                    </div>

                    {/* User Avatar */}
                    {message.role === 'user' && (
                      <span className="mt-1 grid size-8 shrink-0 place-items-center rounded-lg border bg-primary/20 text-primary border-primary/30">
                        <User className="size-4" />
                      </span>
                    )}
                  </div>
                ))}

                {/* Loading indicator */}
                {loading && (
                  <div className="flex items-center gap-3 text-xs text-muted-foreground pl-1">
                    <span className="grid size-8 place-items-center rounded-lg border bg-muted/40">
                      <Loader2 className="size-4 animate-spin text-emerald-400" />
                    </span>
                    <span>
                      {mode === 'chat'
                        ? 'Searching FAISS master vector index & generating grounded answer...'
                        : 'Querying master vector database...'}
                    </span>
                  </div>
                )}

                <div ref={chatEndRef} />
              </div>
            )}
          </div>

          {/* Bottom Chat Input Form */}
          <div className="border-t bg-background/50 p-3 md:p-4">
            {error && (
              <div className="mb-3 rounded-lg border border-destructive/30 bg-destructive/10 p-2.5 text-xs text-destructive flex items-center justify-between">
                <span>{error}</span>
                <button onClick={() => setError('')} className="hover:underline">
                  Dismiss
                </button>
              </div>
            )}

            <form onSubmit={handleSubmit} className="flex items-center gap-2 rounded-xl border bg-background px-3 py-2 shadow-xs focus-within:ring-1 focus-within:ring-ring">
              <MessageSquare className="size-4 shrink-0 text-muted-foreground ml-1" />

              <input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={
                  mode === 'chat'
                    ? 'Ask something grounded in your knowledge base...'
                    : 'Enter raw query string to search FAISS vector chunks...'
                }
                disabled={loading}
                className="min-w-0 flex-1 bg-transparent px-2 py-1 text-sm outline-none placeholder:text-muted-foreground/70"
              />

              {mode === 'vector' && (
                <div className="flex items-center gap-1.5 border-l pl-2 text-xs text-muted-foreground">
                  <span>Top K:</span>
                  <select
                    value={topK}
                    onChange={(e) => setTopK(Number(e.target.value))}
                    className="bg-transparent font-medium text-foreground outline-none cursor-pointer"
                  >
                    <option value={3} className="bg-card">3</option>
                    <option value={5} className="bg-card">5</option>
                    <option value={10} className="bg-card">10</option>
                  </select>
                </div>
              )}

              <Button
                size="icon"
                type="submit"
                disabled={!input.trim() || loading}
                className="shrink-0 size-8 rounded-lg"
              >
                {loading ? <Loader2 className="size-4 animate-spin" /> : <ArrowUp className="size-4" />}
              </Button>
            </form>
            
            <p className="mt-2 text-[11px] text-center text-muted-foreground/80">
              CloudSpawn Grounded RAG Assistant • Powered by Formicx Vector Orchestrator Engine & FAISS
            </p>
          </div>
        </div>
      </div>
    </Shell>
  )
}
