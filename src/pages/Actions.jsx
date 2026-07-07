import { useState } from 'react'
import { Send, Mail, FileText, RefreshCw, CheckCircle2, Inbox } from 'lucide-react'
import { api } from '../api/client'
import { useResource } from '../hooks/useApi'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import Modal from '../components/ui/Modal'
import Spinner, { LoadingBlock } from '../components/ui/Spinner'
import EmptyState from '../components/ui/EmptyState'
import { ActionStatusBadge } from '../components/StatusBadges'
import { relativeTime, formatDateTime, titleCase } from '../lib/format'

const TYPE_ICON = { EMAIL_VENDOR: Mail, RFQ_SUBSTITUTION: RefreshCw, PO_AMENDMENT: FileText }

function subjectOf(draft) {
  const first = (draft || '').split('\n').find((l) => /^subject:/i.test(l.trim()))
  return first ? first.replace(/^subject:/i, '').trim() : 'Drafted action'
}

export default function Actions() {
  const { data: drafts, loading, refresh } = useResource(() => api.getDrafts(), { pollMs: 15000 })
  const [active, setActive] = useState(null)
  const [executing, setExecuting] = useState(false)
  const [done, setDone] = useState(null)

  async function execute(id) {
    setExecuting(true)
    try {
      const res = await api.executeAction(id)
      setDone(res?.message || 'Action executed (simulated).')
      refresh()
    } finally {
      setExecuting(false)
    }
  }

  function closeModal() {
    setActive(null)
    setDone(null)
    setExecuting(false)
  }

  if (loading && !drafts) return <LoadingBlock label="Loading drafts…" />

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted">
        FlowSense auto-drafts vendor escalations and amendments when a critical-path risk is detected.
        Review and dispatch with one click.
      </p>

      {(drafts || []).length === 0 ? (
        <Card>
          <EmptyState
            icon={Inbox}
            title="No drafts awaiting approval"
            description="When the cascade engine flags a critical impact, a drafted action will appear here."
          />
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {drafts.map((d) => {
            const Icon = TYPE_ICON[d.action_type] || Send
            return (
              <Card key={d.id} className="flex flex-col animate-fade-in">
                <div className="flex items-start gap-3 p-5 pb-3">
                  <span className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-primary/10 text-primary">
                    <Icon size={18} />
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <Badge tone="primary">{titleCase(d.action_type)}</Badge>
                      <ActionStatusBadge status={d.status} />
                    </div>
                    <p className="mt-1.5 truncate text-sm font-semibold text-content">{subjectOf(d.draft_content)}</p>
                    <p className="text-[11px] text-muted" title={formatDateTime(d.created_at)}>
                      Alert #{d.alert_id} · drafted {relativeTime(d.created_at)}
                    </p>
                  </div>
                </div>
                <div className="mx-5 flex-1 rounded-lg border border-border bg-surface-2/40 p-3">
                  <p className="line-clamp-4 whitespace-pre-wrap text-xs leading-relaxed text-muted">
                    {d.draft_content}
                  </p>
                </div>
                <div className="flex items-center justify-end gap-2 p-4">
                  <button className="btn-ghost !py-1.5 text-xs" onClick={() => setActive(d)}>
                    Review
                  </button>
                  <button className="btn-primary !py-1.5 text-xs" onClick={() => setActive(d)}>
                    <Send size={14} /> Approve & Send
                  </button>
                </div>
              </Card>
            )
          })}
        </div>
      )}

      <Modal
        open={!!active}
        onClose={closeModal}
        title={active ? titleCase(active.action_type) : ''}
        subtitle={active ? `Alert #${active.alert_id} · ${subjectOf(active.draft_content)}` : ''}
        size="lg"
        footer={
          done ? (
            <button className="btn-primary" onClick={closeModal}>
              Done
            </button>
          ) : (
            <>
              <button className="btn-ghost" onClick={closeModal} disabled={executing}>
                Cancel
              </button>
              <button className="btn-primary" onClick={() => execute(active.id)} disabled={executing}>
                {executing ? <Spinner size={14} /> : <Send size={14} />}
                {executing ? 'Sending…' : 'Approve & Execute'}
              </button>
            </>
          )
        }
      >
        {done ? (
          <div className="flex flex-col items-center gap-3 py-8 text-center">
            <span className="grid h-14 w-14 place-items-center rounded-full bg-ok/10 text-ok">
              <CheckCircle2 size={30} />
            </span>
            <p className="text-sm font-semibold text-content">{done}</p>
            <p className="text-xs text-muted">The action has been marked as SENT.</p>
          </div>
        ) : (
          <pre className="max-h-[52vh] overflow-auto whitespace-pre-wrap rounded-lg border border-border bg-surface-2/40 p-4 font-mono text-xs leading-relaxed text-content">
            {active?.draft_content}
          </pre>
        )}
      </Modal>
    </div>
  )
}
