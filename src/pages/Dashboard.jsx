import { useMemo } from 'react'
import { Link } from 'react-router-dom'
import {
  Package,
  Truck,
  AlertTriangle,
  Bell,
  ArrowRight,
  TrendingUp,
  ShieldAlert,
} from 'lucide-react'
import { api } from '../api/client'
import { useResource } from '../hooks/useApi'
import StatCard from '../components/ui/StatCard'
import Card, { CardHeader, CardBody } from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import Meter from '../components/ui/Meter'
import { LoadingBlock } from '../components/ui/Spinner'
import StatusDonut from '../components/charts/StatusDonut'
import DelayRiskChart from '../components/charts/DelayRiskChart'
import {
  formatDate,
  delayDays,
  pct,
  riskTone,
  relativeTime,
  SEVERITY_TONE,
  titleCase,
} from '../lib/format'

const POLL = 15000

export default function Dashboard() {
  const { data: materials, loading } = useResource(() => api.getMaterials(), { pollMs: POLL })
  const { data: alerts } = useResource(() => api.getAlerts(), { pollMs: POLL })
  const { data: drafts } = useResource(() => api.getDrafts(), { pollMs: POLL })

  const stats = useMemo(() => {
    const list = materials || []
    const inTransit = list.filter((m) => ['IN_TRANSIT', 'SHIPPED'].includes(m.status)).length
    const atRisk = list.filter((m) => (m.delay_probability || 0) >= 0.5).length
    const delivered = list.filter((m) => m.status === 'DELIVERED').length
    return { total: list.length, inTransit, atRisk, delivered }
  }, [materials])

  const criticalAlerts = (alerts || []).filter((a) => a.severity === 'CRITICAL')

  const atRiskMaterials = useMemo(
    () =>
      [...(materials || [])]
        .filter((m) => (m.delay_probability || 0) >= 0.3)
        .sort((a, b) => (b.delay_probability || 0) - (a.delay_probability || 0))
        .slice(0, 5),
    [materials],
  )

  if (loading && !materials) return <LoadingBlock label="Loading command center…" />

  return (
    <div className="space-y-6">
      {/* Critical banner */}
      {criticalAlerts.length > 0 && (
        <div className="flex flex-col gap-3 rounded-xl border border-danger/30 bg-danger/10 p-4 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-start gap-3">
            <span className="mt-0.5 grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-danger/15 text-danger animate-pulse-ring">
              <ShieldAlert size={18} />
            </span>
            <div>
              <p className="text-sm font-semibold text-content">
                {criticalAlerts.length} critical-path {criticalAlerts.length === 1 ? 'impact' : 'impacts'} detected
              </p>
              <p className="text-sm text-muted">{criticalAlerts[0].message}</p>
            </div>
          </div>
          <Link to="/alerts" className="btn-danger shrink-0">
            Review alerts <ArrowRight size={16} />
          </Link>
        </div>
      )}

      {/* KPIs */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Tracked Orders" value={stats.total} icon={Package} accent="primary" sub={`${stats.delivered} delivered`} />
        <StatCard label="In Transit" value={stats.inTransit} icon={Truck} accent="info" sub="shipped or en route" />
        <StatCard label="At Risk" value={stats.atRisk} icon={AlertTriangle} accent="warn" sub="≥ 50% delay probability" />
        <StatCard
          label="Critical Alerts"
          value={criticalAlerts.length}
          icon={Bell}
          accent="danger"
          pulse={criticalAlerts.length > 0}
          sub={`${(drafts || []).length} drafts ready`}
        />
      </div>

      {/* Charts */}
      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="lg:col-span-2">
          <CardHeader title="Order Status Mix" subtitle="Distribution across lifecycle" icon={Package} />
          <CardBody>
            <StatusDonut materials={materials || []} />
          </CardBody>
        </Card>
        <Card className="lg:col-span-3">
          <CardHeader
            title="Delay Risk — Top Orders"
            subtitle="FlowSense forecast delay probability"
            icon={TrendingUp}
          />
          <CardBody>
            <DelayRiskChart materials={materials || []} />
          </CardBody>
        </Card>
      </div>

      {/* At-risk + alerts */}
      <div className="grid gap-4 lg:grid-cols-5">
        <Card className="lg:col-span-3">
          <CardHeader
            title="At-Risk Materials"
            subtitle="Forecast slip vs. promised date"
            icon={AlertTriangle}
            action={
              <Link to="/materials" className="btn-ghost !py-1.5 text-xs">
                All orders <ArrowRight size={14} />
              </Link>
            }
          />
          <CardBody className="!pt-2">
            {atRiskMaterials.length === 0 ? (
              <p className="py-8 text-center text-sm text-muted">Nothing at risk right now.</p>
            ) : (
              <div className="divide-y divide-border">
                {atRiskMaterials.map((m) => {
                  const d = delayDays(m.promised_delivery_date, m.forecast_delivery_date)
                  return (
                    <div key={m.id} className="flex items-center gap-4 py-3">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-sm font-semibold text-content">{m.sku}</span>
                          <Badge tone={riskTone(m.delay_probability)}>{pct(m.delay_probability)} risk</Badge>
                        </div>
                        <p className="truncate text-xs text-muted">
                          {m.description} · {m.vendor_name}
                        </p>
                      </div>
                      <div className="hidden w-28 sm:block">
                        <Meter value={m.delay_probability} tone={riskTone(m.delay_probability)} />
                      </div>
                      <div className="w-24 shrink-0 text-right">
                        {d != null && d > 0 ? (
                          <span className="text-sm font-semibold text-danger">+{d}d late</span>
                        ) : (
                          <span className="text-sm font-semibold text-ok">on time</span>
                        )}
                        <p className="text-[11px] text-muted">{formatDate(m.forecast_delivery_date)}</p>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </CardBody>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader
            title="Active Alerts"
            subtitle="Unresolved"
            icon={Bell}
            action={
              <Link to="/alerts" className="btn-ghost !py-1.5 text-xs">
                View all <ArrowRight size={14} />
              </Link>
            }
          />
          <CardBody className="!pt-2">
            {(alerts || []).length === 0 ? (
              <p className="py-8 text-center text-sm text-muted">No active alerts.</p>
            ) : (
              <div className="space-y-3">
                {(alerts || []).slice(0, 4).map((a) => (
                  <div key={a.id} className="rounded-lg border border-border bg-surface-2/50 p-3">
                    <div className="mb-1 flex items-center justify-between gap-2">
                      <Badge tone={SEVERITY_TONE[a.severity]} dot>
                        {titleCase(a.severity)}
                      </Badge>
                      <span className="text-[11px] text-muted">{relativeTime(a.created_at)}</span>
                    </div>
                    <p className="text-sm text-content">{a.message}</p>
                  </div>
                ))}
              </div>
            )}
          </CardBody>
        </Card>
      </div>
    </div>
  )
}
