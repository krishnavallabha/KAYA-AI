import { useMemo, useState } from 'react'
import { Search, Plus, Package, MapPin, Building2, CalendarClock, Check } from 'lucide-react'
import { api } from '../api/client'
import { useResource } from '../hooks/useApi'
import Card from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import Meter from '../components/ui/Meter'
import Modal from '../components/ui/Modal'
import EmptyState from '../components/ui/EmptyState'
import { LoadingBlock } from '../components/ui/Spinner'
import { MaterialStatusBadge } from '../components/StatusBadges'
import {
  formatDate,
  delayDays,
  pct,
  riskTone,
  titleCase,
  MATERIAL_LIFECYCLE,
} from '../lib/format'

const STATUS_OPTIONS = ['ALL', ...MATERIAL_LIFECYCLE]

export default function Materials() {
  const { data: materials, loading, refresh } = useResource(() => api.getMaterials(), { pollMs: 20000 })
  const [query, setQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('ALL')
  const [selected, setSelected] = useState(null)
  const [creating, setCreating] = useState(false)

  const filtered = useMemo(() => {
    const list = materials || []
    return list.filter((m) => {
      const matchStatus = statusFilter === 'ALL' || m.status === statusFilter
      const q = query.trim().toLowerCase()
      const matchQuery =
        !q ||
        [m.sku, m.description, m.vendor_name].filter(Boolean).some((v) => v.toLowerCase().includes(q))
      return matchStatus && matchQuery
    })
  }, [materials, query, statusFilter])

  if (loading && !materials) return <LoadingBlock label="Loading orders…" />

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-1 flex-col gap-3 sm:flex-row sm:items-center">
          <div className="relative sm:w-72">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search SKU, vendor, description…"
              className="input pl-9"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input sm:w-44"
          >
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>
                {s === 'ALL' ? 'All statuses' : titleCase(s)}
              </option>
            ))}
          </select>
        </div>
        <button className="btn-primary" onClick={() => setCreating(true)}>
          <Plus size={16} /> New Order
        </button>
      </div>

      <Card className="overflow-hidden">
        {filtered.length === 0 ? (
          <EmptyState icon={Package} title="No matching orders" description="Try a different search or status filter." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[820px] text-sm">
              <thead>
                <tr className="border-b border-border bg-surface-2/60 text-left text-xs uppercase tracking-wide text-muted">
                  <th className="px-5 py-3 font-semibold">Order</th>
                  <th className="px-4 py-3 font-semibold">Vendor</th>
                  <th className="px-4 py-3 font-semibold">Status</th>
                  <th className="px-4 py-3 font-semibold">Promised</th>
                  <th className="px-4 py-3 font-semibold">Forecast</th>
                  <th className="px-4 py-3 font-semibold">Delay Risk</th>
                  <th className="px-4 py-3 font-semibold">Conf.</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filtered.map((m) => {
                  const d = delayDays(m.promised_delivery_date, m.forecast_delivery_date)
                  return (
                    <tr
                      key={m.id}
                      onClick={() => setSelected(m)}
                      className="cursor-pointer transition-colors hover:bg-surface-2/50"
                    >
                      <td className="px-5 py-3">
                        <div className="font-mono font-semibold text-content">{m.sku}</div>
                        <div className="max-w-[220px] truncate text-xs text-muted">{m.description}</div>
                      </td>
                      <td className="px-4 py-3 text-content">{m.vendor_name || '—'}</td>
                      <td className="px-4 py-3">
                        <MaterialStatusBadge status={m.status} />
                      </td>
                      <td className="px-4 py-3 text-muted">{formatDate(m.promised_delivery_date)}</td>
                      <td className="px-4 py-3">
                        <span className="text-content">{formatDate(m.forecast_delivery_date)}</span>
                        {d != null && d > 0 && (
                          <span className="ml-1 text-xs font-semibold text-danger">+{d}d</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <Meter value={m.delay_probability} tone={riskTone(m.delay_probability)} className="w-16" />
                          <span className="w-9 text-xs font-semibold text-content">{pct(m.delay_probability)}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-muted">{pct(m.confidence_score)}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
      <p className="px-1 text-xs text-muted">
        Showing {filtered.length} of {(materials || []).length} orders · click a row for details
      </p>

      <MaterialDetail material={selected} onClose={() => setSelected(null)} />
      <NewOrderModal
        open={creating}
        onClose={() => setCreating(false)}
        onCreated={() => {
          setCreating(false)
          refresh()
        }}
      />
    </div>
  )
}

/* ---------------- Detail modal ---------------- */
function MaterialDetail({ material, onClose }) {
  if (!material) return null
  const d = delayDays(material.promised_delivery_date, material.forecast_delivery_date)
  const stageIndex = MATERIAL_LIFECYCLE.indexOf(material.status)

  return (
    <Modal
      open={!!material}
      onClose={onClose}
      title={material.sku}
      subtitle={material.description}
      size="lg"
    >
      <div className="space-y-5">
        {/* Lifecycle stepper */}
        <div className="flex items-center">
          {MATERIAL_LIFECYCLE.map((stage, i) => {
            const done = i <= stageIndex
            return (
              <div key={stage} className="flex flex-1 items-center last:flex-none">
                <div className="flex flex-col items-center">
                  <span
                    className={`grid h-7 w-7 place-items-center rounded-full text-xs font-bold ${
                      done ? 'bg-primary text-primary-fg' : 'bg-surface-2 text-muted'
                    }`}
                  >
                    {done ? <Check size={14} /> : i + 1}
                  </span>
                  <span className={`mt-1 text-[10px] ${done ? 'text-content' : 'text-muted'}`}>
                    {titleCase(stage)}
                  </span>
                </div>
                {i < MATERIAL_LIFECYCLE.length - 1 && (
                  <div className={`mx-1 h-0.5 flex-1 ${i < stageIndex ? 'bg-primary' : 'bg-surface-2'}`} />
                )}
              </div>
            )
          })}
        </div>

        <div className="grid grid-cols-2 gap-4">
          <Field icon={Building2} label="Vendor" value={material.vendor_name || '—'} />
          <Field icon={MapPin} label="Current location" value={material.current_location || 'Unknown'} />
          <Field icon={Package} label="Quantity" value={material.quantity} />
          <Field icon={CalendarClock} label="Linked activity" value={material.activity_id ? `#${material.activity_id}` : '—'} />
          <Field icon={CalendarClock} label="Promised date" value={formatDate(material.promised_delivery_date)} />
          <Field
            icon={CalendarClock}
            label="FlowSense forecast"
            value={
              <span>
                {formatDate(material.forecast_delivery_date)}
                {d != null && d > 0 && <span className="ml-1 font-semibold text-danger">(+{d}d)</span>}
              </span>
            }
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <MetricBox label="Delay probability" value={pct(material.delay_probability)} tone={riskTone(material.delay_probability)} meter={material.delay_probability} />
          <MetricBox label="Confidence score" value={pct(material.confidence_score)} tone="info" meter={material.confidence_score} />
        </div>
      </div>
    </Modal>
  )
}

function Field({ icon: Icon, label, value }) {
  return (
    <div className="rounded-lg border border-border bg-surface-2/40 p-3">
      <div className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-muted">
        <Icon size={13} /> {label}
      </div>
      <div className="mt-1 text-sm font-medium text-content">{value}</div>
    </div>
  )
}

function MetricBox({ label, value, tone, meter }) {
  return (
    <div className="rounded-lg border border-border bg-surface-2/40 p-3">
      <div className="flex items-baseline justify-between">
        <span className="text-[11px] font-semibold uppercase tracking-wide text-muted">{label}</span>
        <span className="text-lg font-bold text-content">{value}</span>
      </div>
      <Meter value={meter} tone={tone} className="mt-2" />
    </div>
  )
}

/* ---------------- New order modal ---------------- */
const EMPTY = {
  sku: '',
  description: '',
  quantity: 1,
  status: 'ORDERED',
  vendor_name: '',
  current_location: '',
  promised_delivery_date: '',
  activity_id: '',
}

function NewOrderModal({ open, onClose, onCreated }) {
  const [form, setForm] = useState(EMPTY)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  async function submit() {
    if (!form.sku.trim() || !form.promised_delivery_date) {
      setError('SKU and promised delivery date are required.')
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      const payload = {
        sku: form.sku.trim(),
        description: form.description || null,
        quantity: Number(form.quantity) || 1,
        status: form.status,
        vendor_name: form.vendor_name || null,
        current_location: form.current_location || null,
        promised_delivery_date: new Date(form.promised_delivery_date).toISOString(),
        activity_id: form.activity_id ? Number(form.activity_id) : null,
      }
      await api.createMaterial(payload)
      setForm(EMPTY)
      onCreated()
    } catch (e) {
      setError(e.message || 'Failed to create order.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Track a new order"
      subtitle="Add a material order for FlowSense to monitor"
      size="lg"
      footer={
        <>
          <button className="btn-ghost" onClick={onClose} disabled={submitting}>
            Cancel
          </button>
          <button className="btn-primary" onClick={submit} disabled={submitting}>
            {submitting ? 'Creating…' : 'Create order'}
          </button>
        </>
      }
    >
      <div className="grid grid-cols-2 gap-4">
        <div className="col-span-1">
          <label className="label">SKU *</label>
          <input className="input" value={form.sku} onChange={set('sku')} placeholder="SKU-501" />
        </div>
        <div className="col-span-1">
          <label className="label">Quantity</label>
          <input className="input" type="number" min="1" value={form.quantity} onChange={set('quantity')} />
        </div>
        <div className="col-span-2">
          <label className="label">Description</label>
          <input className="input" value={form.description} onChange={set('description')} placeholder="Structural steel beams" />
        </div>
        <div className="col-span-1">
          <label className="label">Vendor</label>
          <input className="input" value={form.vendor_name} onChange={set('vendor_name')} placeholder="SteelCorp Ltd" />
        </div>
        <div className="col-span-1">
          <label className="label">Status</label>
          <select className="input" value={form.status} onChange={set('status')}>
            {MATERIAL_LIFECYCLE.map((s) => (
              <option key={s} value={s}>
                {titleCase(s)}
              </option>
            ))}
          </select>
        </div>
        <div className="col-span-1">
          <label className="label">Promised delivery *</label>
          <input className="input" type="date" value={form.promised_delivery_date} onChange={set('promised_delivery_date')} />
        </div>
        <div className="col-span-1">
          <label className="label">Linked activity ID</label>
          <input className="input" type="number" value={form.activity_id} onChange={set('activity_id')} placeholder="2" />
        </div>
        <div className="col-span-2">
          <label className="label">Current location</label>
          <input className="input" value={form.current_location} onChange={set('current_location')} placeholder="Vendor yard" />
        </div>
      </div>
      {error && <p className="mt-3 text-sm font-medium text-danger">{error}</p>}
    </Modal>
  )
}
