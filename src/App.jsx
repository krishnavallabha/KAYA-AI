import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import { LoadingBlock } from './components/ui/Spinner'

// Route-level code splitting: heavy deps (React Flow, Recharts) load on demand.
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Materials = lazy(() => import('./pages/Materials'))
const Schedule = lazy(() => import('./pages/Schedule'))
const Alerts = lazy(() => import('./pages/Alerts'))
const Actions = lazy(() => import('./pages/Actions'))
const Ingest = lazy(() => import('./pages/Ingest'))
const RAGAssistant = lazy(() => import('./pages/RAGAssistant'))

function Page({ children }) {
  return <Suspense fallback={<LoadingBlock />}>{children}</Suspense>
}

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Page><Dashboard /></Page>} />
        <Route path="/materials" element={<Page><Materials /></Page>} />
        <Route path="/schedule" element={<Page><Schedule /></Page>} />
        <Route path="/alerts" element={<Page><Alerts /></Page>} />
        <Route path="/actions" element={<Page><Actions /></Page>} />
        <Route path="/ingest" element={<Page><Ingest /></Page>} />\n        <Route path="/rag" element={<Page><RAGAssistant /></Page>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
