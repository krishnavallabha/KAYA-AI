import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Package,
  Network,
  Bell,
  Send,
  Upload,
  X,
  Activity,
} from 'lucide-react'

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/materials', label: 'Materials', icon: Package },
  { to: '/schedule', label: 'Schedule Graph', icon: Network },
  { to: '/alerts', label: 'Alerts', icon: Bell },
  { to: '/actions', label: 'Action Drafts', icon: Send },
  { to: '/ingest', label: 'Ingest Data', icon: Upload },
]

function Brand() {
  return (
    <div className="flex items-center gap-2.5 px-5 py-5">
      <span className="grid h-9 w-9 place-items-center rounded-lg bg-primary text-primary-fg shadow-sm">
        <Activity size={20} />
      </span>
      <div className="leading-tight">
        <div className="text-sm font-bold tracking-tight text-content">FlowSense</div>
        <div className="text-[10px] font-medium uppercase tracking-wider text-muted">
          Supply Chain AI
        </div>
      </div>
    </div>
  )
}

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {/* Mobile backdrop */}
      {open && (
        <div
          className="fixed inset-0 z-30 bg-black/50 lg:hidden"
          onClick={onClose}
          aria-hidden
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-border bg-surface transition-transform duration-200 lg:translate-x-0 ${
          open ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex items-center justify-between">
          <Brand />
          <button
            onClick={onClose}
            className="mr-3 rounded-lg p-1.5 text-muted hover:bg-surface-2 lg:hidden"
            aria-label="Close menu"
          >
            <X size={18} />
          </button>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-2">
          {NAV.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted hover:bg-surface-2 hover:text-content'
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-border px-5 py-4">
          <p className="text-[11px] leading-relaxed text-muted">
            Action Layer · Live PM dashboard
            <br />
            Kaya AI Hackathon 2026
          </p>
        </div>
      </aside>
    </>
  )
}
