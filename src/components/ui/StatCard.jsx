const ACCENTS = {
  primary: 'text-primary bg-primary/10',
  ok: 'text-ok bg-ok/10',
  warn: 'text-warn bg-warn/10',
  danger: 'text-danger bg-danger/10',
  info: 'text-info bg-info/10',
  neutral: 'text-muted bg-surface-2',
}

export default function StatCard({ label, value, sub, icon: Icon, accent = 'primary', pulse = false }) {
  return (
    <div className="card animate-fade-in p-5">
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted">{label}</p>
        {Icon && (
          <span
            className={`grid h-9 w-9 place-items-center rounded-lg ${ACCENTS[accent] || ACCENTS.primary} ${pulse ? 'animate-pulse-ring' : ''}`}
          >
            <Icon size={18} />
          </span>
        )}
      </div>
      <div className="mt-3 text-3xl font-bold tracking-tight text-content">{value}</div>
      {sub && <p className="mt-1 text-xs text-muted">{sub}</p>}
    </div>
  )
}
