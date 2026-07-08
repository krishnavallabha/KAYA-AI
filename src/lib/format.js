/* Shared formatting + status styling helpers. */

export function formatDate(value, opts = {}) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '—'
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    ...opts,
  })
}

export function formatDateTime(value) {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '—'
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

/** Whole-day difference forecast - promised (positive = late). */
export function delayDays(promised, forecast) {
  if (!promised || !forecast) return null
  const p = new Date(promised)
  const f = new Date(forecast)
  if (Number.isNaN(p.getTime()) || Number.isNaN(f.getTime())) return null
  return Math.round((f - p) / (1000 * 60 * 60 * 24))
}

export function relativeTime(value) {
  if (!value) return '—'
  const d = new Date(value)
  const diff = (Date.now() - d.getTime()) / 1000
  const abs = Math.abs(diff)
  const sign = diff >= 0 ? 'ago' : 'from now'
  if (abs < 60) return 'just now'
  if (abs < 3600) return `${Math.round(abs / 60)}m ${sign}`
  if (abs < 86400) return `${Math.round(abs / 3600)}h ${sign}`
  return `${Math.round(abs / 86400)}d ${sign}`
}

export const pct = (v) => `${Math.round((Number(v) || 0) * 100)}%`

export function titleCase(s) {
  if (!s) return ''
  return String(s)
    .toLowerCase()
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

/* ---- Material status → tone (maps to Badge tone) ---- */
export const MATERIAL_STATUS_TONE = {
  ORDERED: 'neutral',
  FABRICATING: 'info',
  SHIPPED: 'info',
  IN_TRANSIT: 'info',
  DELIVERED: 'ok',
}

/* Ordered list for lifecycle progress bars */
export const MATERIAL_LIFECYCLE = [
  'ORDERED',
  'FABRICATING',
  'SHIPPED',
  'IN_TRANSIT',
  'DELIVERED',
]

export const ACTIVITY_STATUS_TONE = {
  NOT_STARTED: 'neutral',
  IN_PROGRESS: 'info',
  COMPLETED: 'ok',
}

export const SEVERITY_TONE = {
  INFO: 'info',
  WARNING: 'warn',
  CRITICAL: 'danger',
}

export const ACTION_STATUS_TONE = {
  DRAFT: 'warn',
  APPROVED: 'info',
  SENT: 'ok',
}

/** Delay-probability → tone for coloring risk. */
export function riskTone(p) {
  const v = Number(p) || 0
  if (v >= 0.6) return 'danger'
  if (v >= 0.3) return 'warn'
  return 'ok'
}
