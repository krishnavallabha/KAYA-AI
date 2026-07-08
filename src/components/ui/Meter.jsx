const FILL = {
  ok: 'bg-ok',
  warn: 'bg-warn',
  danger: 'bg-danger',
  info: 'bg-info',
  primary: 'bg-primary',
}

/** Compact horizontal meter for 0..1 values (delay prob, confidence, etc.). */
export default function Meter({ value = 0, tone = 'primary', className = '' }) {
  const pct = Math.max(0, Math.min(100, Math.round((Number(value) || 0) * 100)))
  return (
    <div className={`h-1.5 w-full overflow-hidden rounded-full bg-surface-2 ${className}`}>
      <div
        className={`h-full rounded-full transition-all duration-500 ${FILL[tone] || FILL.primary}`}
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}
