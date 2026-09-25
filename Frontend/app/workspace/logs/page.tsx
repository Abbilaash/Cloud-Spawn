'use client'

import { useEffect, useState } from 'react'
import { Terminal, RefreshCw, Trash2, Search, Filter, Pause, Play, AlertTriangle, CheckCircle, Info } from 'lucide-react'
import { Shell, SectionEyebrow, StatCard, EmptyState } from '@/components/cloudspawn-shell'
import { Button } from '@/components/ui/button'
import { getLogs, clearLogs, LogEntry } from '@/lib/api'

export default function LogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [autoRefresh, setAutoRefresh] = useState(true)
  const [filterLevel, setFilterLevel] = useState('ALL')
  const [searchQuery, setSearchQuery] = useState('')

  const fetchLogsData = async () => {
    try {
      const data = await getLogs(200, filterLevel)
      setLogs(data.logs || [])
      setError('')
    } catch (err: any) {
      setError('Failed to connect to backend logs stream (http://localhost:8000/api/logs).')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLogsData()
    if (!autoRefresh) return

    const interval = setInterval(fetchLogsData, 2000)
    return () => clearInterval(interval)
  }, [autoRefresh, filterLevel])

  const handleClearLogs = async () => {
    try {
      await clearLogs()
      setLogs([])
    } catch {
      setError('Failed to clear logs.')
    }
  }

  const filteredLogs = logs.filter((log) => {
    if (!searchQuery.trim()) return true
    const query = searchQuery.toLowerCase()
    return (
      log.message.toLowerCase().includes(query) ||
      log.logger.toLowerCase().includes(query) ||
      log.level.toLowerCase().includes(query)
    )
  })

  const infoCount = logs.filter((l) => l.level === 'INFO').length
  const warningCount = logs.filter((l) => l.level === 'WARNING').length
  const errorCount = logs.filter((l) => l.level === 'ERROR').length

  return (
    <Shell>
      <div className="mx-auto max-w-6xl px-5 py-8 md:px-8 md:py-12">
        <SectionEyebrow>System</SectionEyebrow>
        <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-end">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">System & Agent Logs</h1>
            <p className="mt-2 text-muted-foreground">
              Real-time log stream from FastAPI backend, background tasks, and Formicx agent execution.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setAutoRefresh(!autoRefresh)}
              className="gap-1.5 text-xs"
            >
              {autoRefresh ? <Pause className="size-3.5" /> : <Play className="size-3.5" />}
              {autoRefresh ? 'Live Stream' : 'Paused'}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchLogsData}
              className="gap-1.5 text-xs"
            >
              <RefreshCw className="size-3.5" /> Refresh
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClearLogs}
              className="gap-1.5 text-xs text-destructive hover:bg-destructive/10"
            >
              <Trash2 className="size-3.5" /> Clear Logs
            </Button>
          </div>
        </div>

        {/* Stat Cards */}
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            label="Total Log Entries"
            value={loading ? '...' : String(logs.length)}
            detail="Recorded in memory buffer"
            icon={Terminal}
          />
          <StatCard
            label="Info Messages"
            value={loading ? '...' : String(infoCount)}
            detail="Operational events"
            icon={Info}
          />
          <StatCard
            label="Warnings"
            value={loading ? '...' : String(warningCount)}
            detail="System warnings"
            icon={AlertTriangle}
          />
          <StatCard
            label="Errors"
            value={loading ? '...' : String(errorCount)}
            detail="Failed operations"
            icon={AlertTriangle}
          />
        </div>

        {/* Toolbar: Filters & Search */}
        <div className="mt-8 flex flex-col justify-between gap-4 rounded-xl border bg-card p-4 sm:flex-row sm:items-center">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-medium text-muted-foreground mr-1 flex items-center gap-1">
              <Filter className="size-3" /> Level:
            </span>
            {['ALL', 'INFO', 'WARNING', 'ERROR'].map((lvl) => (
              <button
                key={lvl}
                onClick={() => setFilterLevel(lvl)}
                className={`rounded-md px-2.5 py-1 text-xs font-medium transition ${filterLevel === lvl
                    ? 'bg-primary text-primary-foreground'
                    : 'border bg-muted/30 text-muted-foreground hover:bg-muted'
                  }`}
              >
                {lvl}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2 rounded-lg border bg-background px-3 py-1.5 text-sm sm:w-64">
            <Search className="size-4 text-muted-foreground shrink-0" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search logs..."
              className="w-full bg-transparent text-xs outline-none"
            />
          </div>
        </div>

        {error && (
          <div className="mt-4 rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-xs text-destructive">
            {error}
          </div>
        )}

        {/* Log Console Terminal View */}
        <div className="mt-6 overflow-hidden rounded-xl border bg-slate-950 font-mono text-xs text-slate-200 shadow-2xl">
          <div className="flex items-center justify-between border-b border-slate-800 bg-slate-900/80 px-4 py-3">
            <div className="flex items-center gap-2">
              <span className="size-3 rounded-full bg-rose-500/80" />
              <span className="size-3 rounded-full bg-amber-500/80" />
              <span className="size-3 rounded-full bg-emerald-500/80" />
              <span className="ml-2 text-xs font-medium text-slate-400">cloudspawn-backend.log</span>
            </div>
            <div className="flex items-center gap-2 text-[10px] text-slate-400">
              <span className={`size-2 rounded-full ${autoRefresh ? 'bg-emerald-400 animate-ping' : 'bg-slate-600'}`} />
              {autoRefresh ? 'LIVE POLLING (2s)' : 'STREAM PAUSED'}
            </div>
          </div>

          <div className="max-h-[500px] overflow-y-auto p-4 space-y-2">
            {filteredLogs.length > 0 ? (
              filteredLogs.map((log) => {
                const timeStr = new Date(log.timestamp).toLocaleTimeString()
                const isInfo = log.level === 'INFO'
                const isWarn = log.level === 'WARNING'
                const isError = log.level === 'ERROR'

                return (
                  <div key={log.id} className="flex items-start gap-3 hover:bg-slate-900/50 p-1 rounded">
                    <span className="text-slate-500 shrink-0">{timeStr}</span>
                    <span
                      className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-semibold shrink-0 ${isInfo
                          ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                          : isWarn
                            ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                            : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                        }`}
                    >
                      {log.level}
                    </span>
                    <span className="text-slate-400 font-semibold shrink-0">[{log.logger}]</span>
                    <span className="text-slate-200 break-all">{log.message}</span>
                  </div>
                )
              })
            ) : (
              <div className="py-12 text-center text-slate-500">
                <Terminal className="mx-auto size-8 mb-2 opacity-50" />
                <p>No log records match your filter criteria.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </Shell>
  )
}
