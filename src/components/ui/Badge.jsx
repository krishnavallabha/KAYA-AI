const TONES = {
  neutral: 'bg-surface-2 text-muted border-border',
  primary: 'bg-primary/10 text-primary border-primary/25',
  info: 'bg-info/10 text-info border-info/25',
  ok: 'bg-ok/10 text-ok border-ok/25',
  warn: 'bg-warn/10 text-warn border-warn/25',
  danger: 'bg-danger/10 text-danger border-danger/25',
}

export default function Badge({ tone = 'neutral', children, className = '', dot = false }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold whitespace-nowrap ${TONES[tone] || TONES.neutral} ${className}`}
    >
      {dot && <span className="h-1.5 w-1.5 rounded-full bg-current" />}
      {children}
    </span>
  )
}
