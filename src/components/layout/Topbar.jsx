import { Menu, Wifi, WifiOff } from 'lucide-react'
import ThemeToggle from '../ThemeToggle'
import { useConnection } from '../../hooks/useApi'

function ConnectionPill() {
  const live = useConnection()
  if (live === true) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-ok/25 bg-ok/10 px-2.5 py-1 text-xs font-semibold text-ok">
        <Wifi size={13} /> Live API
      </span>
    )
  }
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full border border-warn/25 bg-warn/10 px-2.5 py-1 text-xs font-semibold text-warn"
      title="Backend not reachable — showing bundled demo data"
    >
      <WifiOff size={13} /> Demo data
    </span>
  )
}

export default function Topbar({ title, subtitle, onMenu }) {
  return (
    <header className="sticky top-0 z-20 border-b border-border bg-bg/80 backdrop-blur">
      <div className="flex items-center gap-3 px-4 py-3 sm:px-6">
        <button
          onClick={onMenu}
          className="btn-ghost h-9 w-9 !px-0 lg:hidden"
          aria-label="Open menu"
        >
          <Menu size={18} />
        </button>

        <div className="min-w-0 flex-1">
          <h1 className="truncate text-lg font-bold tracking-tight text-content">{title}</h1>
          {subtitle && <p className="truncate text-xs text-muted">{subtitle}</p>}
        </div>

        <div className="flex items-center gap-2">
          <ConnectionPill />
          <ThemeToggle />
        </div>
      </div>
    </header>
  )
}
