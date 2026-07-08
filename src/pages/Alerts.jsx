import { useMemo, useState } from 'react'
import { Bell, CheckCircle2, ShieldAlert, AlertTriangle, Info } from 'lucide-react'
import { api } from '../api/client'
import { useResource } from '../hooks/useApi'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import Spinner, { LoadingBlock } from '../components/ui/Spinner'
import EmptyState from '../components/ui/EmptyState'
import { SeverityBadge } from '../components/StatusBadges'
import { relativeTime, formatDateTime } from '../lib/format'

const SEVERITY_ICON = { CRITICAL: ShieldAlert, WARNING: AlertTriangle, INFO: Info }
const FILTERS = ['ALL', 'CRITICAL', 'WARNING', 'INFO']

export default function Alerts() {
  const { data: alerts, loading, refresh } = useResource(() => api.getAlerts(), { pollMs: 15000 })
  const { data: materials } = useResource(() => api.getMaterials(), { pollMs: 30000 })
  const [filter, setFilter] = useState('ALL')
  const [resolving, setResolving] = useState(null)

  const skuById = useMemo(() => {
    const map = {}
    ;(materials || []).forEach((m) => (map[m.id] = m.sku))
    return map
  }, [materials])

  const filtered = (alerts || []).filter((a) => filter === 'ALL' || a.severity === filter)

  async function resolve(id) {
    setResolving(id)
    try {
      await api.resolveAlert(id)
      refresh()
    } finally {
      setResolving(null)
    }
  }

  if (loading && !alerts) return <LoadingBlock label="Loading alerts…" />

  const counts = FILTERS.reduce((acc, f) => {
    acc[f] = f === 'ALL' ? (alerts || []).length : (alerts || []).filter((a) => a.severity === f).length
    return acc
  }, {})

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        {FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`rounded-full border px-3.5 py-1.5 text-sm font-medium transition-colors ${
              filter === f
                ? 'border-primary bg-primary/10 text-primary'
                : 'border-border bg-surface text-muted hover:bg-surface-2'
            }`}
          >
            {f === 'ALL' ? 'All' : f.charAt(0) + f.slice(1).toLowerCase()}
            <span className="ml-1.5 text-xs opacity-70">{counts[f]}</span>
          </button>
        ))}
      </div>

      {filtered.length === 0 ? (
        <Card>
          <EmptyState
            icon={CheckCircle2}
            title="All clear"
            description={filter === 'ALL' ? 'No unresolved alerts right now.' : `No ${filter.toLowerCase()} alerts.`}
          />
        </Card>
      ) : (
        <div className="space-y-3">
          {filtered.map((a) => {
            const Icon = SEVERITY_ICON[a.severity] || Bell
            const isCritical = a.severity === 'CRITICAL'
            return (
              <Card
                key={a.id}
                className={`animate-fade-in p-4 ${isCritical ? 'border-danger/30' : ''}`}
              >
                <div className="flex items-start gap-4">
                  <span
                    className={`mt-0.5 grid h-10 w-10 shrink-0 place-items-center rounded-lg ${
                      isCritical ? 'bg-danger/10 text-danger' : a.severity === 'WARNING' ? 'bg-warn/10 text-warn' : 'bg-info/10 text-info'
                    }`}
                  >
                    <Icon size={20} />
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="mb-1 flex flex-wrap items-center gap-2">
                      <SeverityBadge severity={a.severity} />
                      {a.material_id != null && skuById[a.material_id] && (
                        <Badge tone="neutral" className="font-mono">{skuById[a.material_id]}</Badge>
                      )}
                      <span className="text-xs text-muted" title={formatDateTime(a.created_at)}>
                        {relativeTime(a.created_at)}
                      </span>
                    </div>
                    <p className="text-sm text-content">{a.message}</p>
                  </div>
                  <button
                    className="btn-ghost shrink-0 !py-1.5 text-xs"
                    onClick={() => resolve(a.id)}
                    disabled={resolving === a.id}
                  >
                    {resolving === a.id ? (
                      <Spinner size={14} />
                    ) : (
                      <>
                        <CheckCircle2 size={14} /> Resolve
                      </>
                    )}
                  </button>
                </div>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
