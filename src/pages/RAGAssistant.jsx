import { useEffect, useRef, useState } from 'react'
import { Bot, Send, FileText, Upload, RefreshCw, Trash2, Database, UserRound, AlertCircle, CheckCircle2 } from 'lucide-react'
import { api } from '../api/client'
import Card, { CardHeader, CardBody } from '../components/ui/Card'
import Spinner from '../components/ui/Spinner'
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const STARTER = {
  role: 'assistant',
  content: 'Ask about indexed vendor updates, delivery evidence, materials, or project schedules. Answers are generated from retrieved sources and include citations when evidence is available.',
}

export default function RAGAssistant() {
  const [messages, setMessages] = useState([STARTER])
  const [question, setQuestion] = useState('')
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [indexing, setIndexing] = useState(false)
  const [notice, setNotice] = useState(null)
  const [error, setError] = useState('')
  const [sourcesExpanded, setSourcesExpanded] = useState(true)
  const [expandedCitations, setExpandedCitations] = useState({})
  const inputRef = useRef(null)
  const bottomRef = useRef(null)

  async function loadSources() {
    try {
      const result = await api.ragSources()
      setSources(result.sources || [])
      setError('')
    } catch (e) {
      setError(e.message || 'Unable to load RAG sources. Check the backend and API configuration.')
    }
  }

  useEffect(() => { loadSources() }, [])
  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, loading])

  async function ask(e) {
    e?.preventDefault()
    const q = question.trim()
    if (!q || loading) return
    setQuestion('')
    setError('')
    setMessages((items) => [...items, { role: 'user', content: q }])
    setLoading(true)
    try {
      const result = await api.ragQuery(q)
      setMessages((items) => [...items, {
        role: 'assistant',
        content: result.answer || 'No answer returned.',
        citations: result.citations || [],
        retrievalMethod: result.retrieval_method,
      }])
    } catch (err) {
      setError(err.message || 'RAG query failed.')
      setMessages((items) => [...items, { role: 'assistant', content: `I couldn't complete that query: ${err.message || 'Backend error'}` }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  async function uploadFile(e) {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file) return
    setUploading(true); setNotice(null); setError('')
    try {
      const result = await api.ragIngest(file)
      setNotice({ type: 'success', text: `${result.message} ${result.chunks_added} chunks added from ${result.filename}.` })
      await loadSources()
    } catch (err) {
      setError(err.message || 'Document ingestion failed.')
    } finally { setUploading(false) }
  }

  async function indexProject() {
    setIndexing(true); setNotice(null); setError('')
    try {
      const result = await api.ragIndexProject()
      const fileSummary = result.files || {}
      setNotice({ type: 'success', text: `Project indexing finished. Files found: ${fileSummary.files_found ?? 0}; files newly indexed: ${fileSummary.indexed ?? 0}; database records processed: ${result.database_records_indexed ?? 0}.` })
      if (fileSummary.errors?.length) setError(`${fileSummary.errors.length} file(s) could not be indexed. Check backend logs and API-key configuration.`)
      await loadSources()
    } catch (err) {
      setError(err.message || 'Project indexing failed.')
    } finally { setIndexing(false) }
  }

  async function removeSource(filename) {
    if (!window.confirm(`Delete indexed source "${filename}"?`)) return
    setError(''); setNotice(null)
    try {
      const result = await api.ragDeleteSource(filename)
      setNotice({ type: 'success', text: `Deleted ${result.chunks_deleted} chunks for ${filename}.` })
      await loadSources()
    } catch (err) { setError(err.message || 'Source deletion failed.') }
  }

  return (
    <div className="space-y-4">

      <div className="flex justify-end">
        <button
          type="button"
          className="btn-ghost"
          onClick={() => window.location.reload()}
          title="Reload the RAG Assistant"
        >
          <RefreshCw size={15} />
          Refresh assistant
        </button>
      </div>

      <div className="flex flex-col gap-3 rounded-xl border border-primary/20 bg-primary/5 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3">
          <Bot className="mt-0.5 shrink-0 text-primary" size={20} />
          <div>
            <h2 className="text-sm font-semibold text-content">Retrieval-Augmented Generation</h2>
            <p className="mt-1 text-sm text-muted">Index project evidence, retrieve relevant passages, and ask questions grounded in those sources.</p>
          </div>
        </div>
        <button className="btn-primary shrink-0" onClick={indexProject} disabled={indexing}>
          {indexing ? <Spinner size={16} /> : <Database size={16} />}
          {indexing ? 'Indexing project…' : 'Index project data'}
        </button>
      </div>

      {notice && <div className="flex items-start gap-2 rounded-lg border border-ok/25 bg-ok/10 p-3 text-sm text-ok"><CheckCircle2 size={16} className="mt-0.5 shrink-0" />{notice.text}</div>}
      {error && <div className="flex items-start gap-2 rounded-lg border border-danger/25 bg-danger/10 p-3 text-sm text-danger"><AlertCircle size={16} className="mt-0.5 shrink-0" />{error}</div>}

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
        <Card className="flex min-h-[580px] flex-col">
          <CardHeader title="Project knowledge chat" subtitle="Answers should be verified against the cited source snippets" icon={Bot} />
          <CardBody className="flex flex-1 flex-col gap-4">
            <div className="flex-1 space-y-4">
              {messages.map((message, i) => (
                <div key={`${message.role}-${i}`} className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {message.role !== 'user' && <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-primary/10 text-primary"><Bot size={17} /></span>}
                  <div className={`max-w-[90%] rounded-xl border p-3 text-sm ${message.role === 'user' ? 'border-primary/20 bg-primary/10 text-content' : 'border-border bg-surface-2 text-content'}`}>
                    {message.role === 'user' && <div className="mb-1 flex items-center gap-1 text-xs font-semibold text-muted"><UserRound size={13} /> You</div>}

                    {message.role === 'user' ? (
                      <p className="whitespace-pre-wrap leading-relaxed">
                        {message.content}
                      </p>
                    ) : (
                      <div className="rag-markdown leading-relaxed">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {message.content}
                        </ReactMarkdown>
                      </div>
                    )}


                    {message.citations?.length > 0 && (
                      <div className="mt-3 border-t border-border pt-3">
                        <button
                          type="button"
                          className="flex w-full items-center justify-between gap-2 text-left"
                          onClick={() =>
                            setExpandedCitations((prev) => ({
                              ...prev,
                              [i]: !prev[i],
                            }))
                          }
                          aria-expanded={!!expandedCitations[i]}
                        >
                          <span className="text-xs font-semibold uppercase tracking-wide text-muted">
                            Retrieved sources ({message.citations.length})
                          </span>
                          <span className="text-muted">
                            {expandedCitations[i] ? '−' : '+'}
                          </span>
                        </button>

                        {expandedCitations[i] && (
                          <div className="mt-3 space-y-2">
                            {message.citations.map((citation, j) => (
                              <div
                                key={`${citation.source_id}-${j}`}
                                className="rounded-lg border border-border bg-surface p-2"
                              >
                                <div className="text-xs font-semibold text-primary">
                                  [{citation.source_id}] {citation.filename} · chunk {citation.chunk_index}
                                </div>
                                <p className="mt-1 text-xs leading-relaxed text-muted">
                                  {citation.snippet}
                                </p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                  </div>
                  {message.role === 'user' && <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-surface-2 text-muted"><UserRound size={17} /></span>}
                </div>
              ))}
              {loading && <div className="flex items-center gap-2 text-sm text-muted"><Spinner size={16} /> Retrieving evidence and generating an answer…</div>}
              <div ref={bottomRef} />
            </div>
            <form onSubmit={ask} className="flex gap-2 border-t border-border pt-4">
              <input ref={inputRef} className="input" value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Ask about a vendor, delivery, material, or schedule…" maxLength={2000} disabled={loading} />
              <button className="btn-primary" type="submit" disabled={loading || question.trim().length < 3} aria-label="Send question"><Send size={16} /></button>
            </form>
            <p className="text-xs text-muted">RAG can only answer from indexed evidence. Validate operational decisions against the original records.</p>
          </CardBody>
        </Card>

        <Card>
          <button
            type="button"
            className="flex w-full items-center justify-between p-4 text-left"
            onClick={() => setSourcesExpanded((expanded) => !expanded)}
            aria-expanded={sourcesExpanded}
          >
            <span className="flex items-center gap-2">
              <FileText size={18} className="text-primary" />
              <span>
                <span className="block text-sm font-semibold text-content">
                  Indexed sources
                </span>
                <span className="block text-xs text-muted">
                  {sources.length} source(s) available
                </span>
              </span>
            </span>
            <span className="text-muted">
              {sourcesExpanded ? '−' : '+'}
            </span>
          </button>

          {sourcesExpanded && (
            <CardBody className="space-y-3">
              <label className="btn-ghost w-full cursor-pointer justify-center">
                {uploading ? <Spinner size={16} /> : <Upload size={16} />}
                {uploading ? 'Uploading…' : 'Upload document'}
                <input
                  className="hidden"
                  type="file"
                  accept=".pdf,.txt,.md,.csv,.xml,.json,.log"
                  onChange={uploadFile}
                  disabled={uploading}
                />
              </label>

              <button
                className="btn-ghost w-full justify-center"
                onClick={loadSources}
                disabled={uploading}
              >
                <RefreshCw size={15} />
                Refresh sources
              </button>

              <div className="max-h-[520px] space-y-2 overflow-y-auto">
                {sources.map((source) => (
                  <div
                    key={`${source.filename}-${source.file_sha256}`}
                    className="flex items-start gap-2 rounded-lg border border-border p-3"
                  >
                    <FileText
                      size={16}
                      className="mt-0.5 shrink-0 text-muted"
                    />
                    <div className="min-w-0 flex-1">
                      <p className="break-words text-xs font-semibold text-content">
                        {source.filename}
                      </p>
                      <p className="mt-1 text-xs text-muted">
                        {source.chunks} chunk(s)
                      </p>
                    </div>
                    <button
                      className="rounded p-1 text-muted hover:bg-danger/10 hover:text-danger"
                      onClick={() => removeSource(source.filename)}
                      title="Delete source"
                      aria-label={`Delete ${source.filename}`}
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}

                {!sources.length && (
                  <p className="rounded-lg border border-dashed border-border p-4 text-center text-sm text-muted">
                    No sources indexed yet. Upload a document or index project data.
                  </p>
                )}
              </div>
            </CardBody>
          )}
        </Card>
      </div>
    </div>
  )
}
