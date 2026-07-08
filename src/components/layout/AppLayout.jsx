import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import { AlertTriangle } from 'lucide-react'
import Sidebar from './Sidebar'
import Topbar from './Topbar'
import { useConnection } from '../../hooks/useApi'

const PAGE_META = {
  '/': { title: 'Command Center', subtitle: 'Skyline Tower — Phase 2 · live supply-chain status' },
  '/materials': { title: 'Material Orders', subtitle: 'Every tracked order across all sources' },
  '/schedule': { title: 'Schedule Graph', subtitle: 'Activity network & critical-path impact' },
  '/alerts': { title: 'Alerts', subtitle: 'Unresolved risk & conflict notifications' },
  '/actions': { title: 'Action Drafts', subtitle: 'AI-drafted responses awaiting approval' },
  '/ingest': { title: 'Ingest Data', subtitle: 'Feed emails, photos & schedules into the pipeline' },
}

export default function AppLayout() {
  const [menuOpen, setMenuOpen] = useState(false)
  const { pathname } = useLocation()
  const meta = PAGE_META[pathname] || { title: 'FlowSense', subtitle: '' }
  const live = useConnection()

  return (
    <div className="min-h-screen bg-bg">
      <Sidebar open={menuOpen} onClose={() => setMenuOpen(false)} />
      <div className="lg:pl-64">
        <Topbar title={meta.title} subtitle={meta.subtitle} onMenu={() => setMenuOpen(true)} />
        
        {live === false && (
          <div className="bg-warn/10 border-b border-warn/25 px-4 py-2 sm:px-6 flex items-center gap-2 text-sm text-warn">
            <AlertTriangle size={16} className="shrink-0" />
            <span>
              <strong>Demo Mode:</strong> The FlowSense backend is currently unreachable. Showing bundled demo fallback data.
            </span>
          </div>
        )}

        <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

