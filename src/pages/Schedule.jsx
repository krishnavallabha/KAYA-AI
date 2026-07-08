import { useMemo, useState } from 'react'
import { Network, Info, GitBranch, Package } from 'lucide-react'
import { api } from '../api/client'
import { useResource } from '../hooks/useApi'
import { useChartColors } from '../hooks/useChartColors'
import Card, { CardHeader, CardBody } from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import { LoadingBlock } from '../components/ui/Spinner'
import EmptyState from '../components/ui/EmptyState'
import ScheduleGraph from '../components/schedule/ScheduleGraph'
import { ActivityStatusBadge, MaterialStatusBadge } from '../components/StatusBadges'
import { formatDate, pct, riskTone } from '../lib/format'

const RISK_TEXT = { danger: 'text-danger', warn: 'text-warn', ok: 'text-ok' }

export default function Schedule() {
  const colors = useChartColors()
  const { data: graph, loading } = useResource(() => api.getScheduleGraph(), { pollMs: 30000 })
  const { data: materials } = useResource(() => api.getMaterials(), { pollMs: 30000 })
  const [selected, setSelected] = useState(null)

  const criticalCount = useMemo(
    () => (graph?.nodes || []).filter((n) => n.is_critical).length,
    [graph],
  )

  const selectedMaterials = useMemo(() => {
    if (!selected) return []
    return (materials || []).filter((m) => String(m.activity_id) === String(selected.id))
  }, [selected, materials])

  if (loading && !graph) return <LoadingBlock label="Building schedule graph…" />

  if (!graph || !graph.nodes?.length) {
    return (
      <Card>
        <EmptyState
          icon={Network}
          title="No schedule loaded"
          description="Import a Primavera XML schedule from the Ingest page to visualize the activity network."
        />
      </Card>
    )
  }

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      <Card className="lg:col-span-2">
        <CardHeader
          title="Activity Network"
          subtitle={`${graph.nodes.length} activities · ${graph.links.length} dependencies`}
          icon={GitBranch}
          action={
            <div className="hidden items-center gap-3 text-xs text-muted sm:flex">
              <span className="flex items-center gap-1.5">
                <span className="inline-block h-2.5 w-4 rounded-sm border-2 border-danger/60" /> Critical path
              </span>
            </div>
          }
        />
        <CardBody className="!p-0">
          <div className="h-[560px] w-full rounded-b-xl">
            <ScheduleGraph graph={graph} colors={colors} onSelect={setSelected} />
          </div>
        </CardBody>
      </Card>

      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="card p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted">Activities</p>
            <p className="mt-1 text-2xl font-bold text-content">{graph.nodes.length}</p>
          </div>
          <div className="card p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted">On Critical Path</p>
            <p className="mt-1 text-2xl font-bold text-danger">{criticalCount}</p>
          </div>
        </div>

        <Card>
          <CardHeader
            title={selected ? selected.label : 'Activity details'}
            subtitle={selected ? `Activity #${selected.id}` : 'Select a node to inspect'}
            icon={Info}
          />
          <CardBody className="!pt-0">
            {!selected ? (
              <p className="py-6 text-center text-sm text-muted">
                Click any activity in the graph to see its schedule and linked materials.
              </p>
            ) : (
              <div className="space-y-4">
                <div className="flex flex-wrap items-center gap-2">
                  <ActivityStatusBadge status={selected.status} />
                  {selected.is_critical && <Badge tone="danger">Critical path</Badge>}
                </div>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <p className="text-[11px] uppercase tracking-wide text-muted">Start</p>
                    <p className="font-medium text-content">{formatDate(selected.start)}</p>
                  </div>
                  <div>
                    <p className="text-[11px] uppercase tracking-wide text-muted">End</p>
                    <p className="font-medium text-content">{formatDate(selected.end)}</p>
                  </div>
                </div>

                <div>
                  <p className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted">
                    <Package size={13} /> Linked materials ({selectedMaterials.length})
                  </p>
                  {selectedMaterials.length === 0 ? (
                    <p className="text-sm text-muted">No materials mapped to this activity.</p>
                  ) : (
                    <div className="space-y-2">
                      {selectedMaterials.map((m) => (
                        <div
                          key={m.id}
                          className="flex items-center justify-between gap-2 rounded-lg border border-border bg-surface-2/40 px-3 py-2"
                        >
                          <div className="min-w-0">
                            <div className="font-mono text-xs font-semibold text-content">{m.sku}</div>
                            <div className="truncate text-[11px] text-muted">{m.description}</div>
                          </div>
                          <div className="flex flex-col items-end gap-1">
                            <MaterialStatusBadge status={m.status} />
                            <span className={`text-[11px] font-semibold ${RISK_TEXT[riskTone(m.delay_probability)]}`}>
                              {pct(m.delay_probability)} risk
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardBody>
        </Card>
      </div>
    </div>
  )
}
