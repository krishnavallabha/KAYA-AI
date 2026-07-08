import { useState } from 'react'
import {
  Mail,
  Image as ImageIcon,
  CalendarRange,
  Upload,
  CheckCircle2,
  AlertCircle,
  Sparkles,
} from 'lucide-react'
import { api } from '../api/client'
import { useResource } from '../hooks/useApi'
import Card, { CardHeader, CardBody } from '../components/ui/Card'
import Spinner from '../components/ui/Spinner'
import { titleCase } from '../lib/format'

const SAMPLE_EMAIL = `Hi team,

Quick update on order SKU-482 (structural steel beams). The shipment has now left our Pune freight hub and is in transit. Due to a fabrication backlog we expect arrival around July 26 rather than the 15th.

Regards,
SteelCorp Dispatch`

export default function Ingest() {
  const { data: materials } = useResource(() => api.getMaterials(), { pollMs: 30000 })
  const skus = (materials || []).map((m) => m.sku)

  return (
    <div className="space-y-4">
      <div className="flex items-start gap-3 rounded-xl border border-primary/20 bg-primary/5 p-4">
        <Sparkles size={18} className="mt-0.5 shrink-0 text-primary" />
        <p className="text-sm text-muted">
          Feed raw supply-chain signals into the FlowSense pipeline. Each submission is parsed, reconciled
          by the Material Tracker, re-forecast, and checked for critical-path cascade impact.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <EmailPanel skus={skus} />
        <VisionPanel skus={skus} />
        <SchedulePanel />
      </div>
    </div>
  )
}

/* ---------------- shared result view ---------------- */
function ResultView({ state }) {
  if (!state) return null
  if (state.type === 'error') {
    return (
      <div className="mt-3 flex items-start gap-2 rounded-lg border border-danger/25 bg-danger/10 p-3 text-sm text-danger">
        <AlertCircle size={16} className="mt-0.5 shrink-0" />
        <span>{state.message}</span>
      </div>
    )
  }
  return (
    <div className="mt-3 rounded-lg border border-ok/25 bg-ok/10 p-3">
      <div className="mb-2 flex items-center gap-2 text-sm font-semibold text-ok">
        <CheckCircle2 size={16} /> {state.message}
      </div>
      {state.data && (
        <dl className="grid grid-cols-1 gap-x-4 gap-y-1.5 text-xs sm:grid-cols-2">
          {Object.entries(state.data).map(([k, v]) => (
            <div key={k} className="flex justify-between gap-3 border-b border-border/50 py-1 last:border-0">
              <dt className="text-muted">{titleCase(k)}</dt>
              <dd className="text-right font-medium text-content">{String(v ?? '—')}</dd>
            </div>
          ))}
        </dl>
      )}
    </div>
  )
}

function SkuField({ value, onChange, skus }) {
  return (
    <div>
      <label className="label">Material SKU</label>
      <input
        className="input"
        list="sku-list"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="SKU-482"
      />
      <datalist id="sku-list">
        {skus.map((s) => (
          <option key={s} value={s} />
        ))}
      </datalist>
    </div>
  )
}

/* ---------------- Email ---------------- */
function EmailPanel({ skus }) {
  const [sku, setSku] = useState('')
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)

  async function submit() {
    if (!sku.trim() || !text.trim()) {
      setResult({ type: 'error', message: 'SKU and email text are required.' })
      return
    }
    setBusy(true)
    setResult(null)
    try {
      const res = await api.ingestEmail(text, sku.trim())
      setResult({ type: 'ok', message: res.message, data: res.parsed_data })
    } catch (e) {
      setResult({ type: 'error', message: e.message || 'Ingest failed.' })
    } finally {
      setBusy(false)
    }
  }

  return (
    <Card className="flex flex-col">
      <CardHeader title="Vendor Email" subtitle="Extract status from unstructured text" icon={Mail} />
      <CardBody className="flex flex-1 flex-col gap-3 !pt-2">
        <SkuField value={sku} onChange={setSku} skus={skus} />
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <label className="label">Email body</label>
            <button
              type="button"
              className="mb-1.5 text-[11px] font-semibold text-primary hover:underline"
              onClick={() => {
                setText(SAMPLE_EMAIL)
                if (!sku) setSku('SKU-482')
              }}
            >
              Use sample
            </button>
          </div>
          <textarea
            className="input min-h-[140px] resize-y"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Paste the raw vendor email here…"
          />
        </div>
        <button className="btn-primary w-full" onClick={submit} disabled={busy}>
          {busy ? <Spinner size={14} /> : <Upload size={14} />}
          {busy ? 'Parsing…' : 'Ingest email'}
        </button>
        <ResultView state={result} />
      </CardBody>
    </Card>
  )
}

/* ---------------- Vision ---------------- */
function VisionPanel({ skus }) {
  const [sku, setSku] = useState('')
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)

  function onFile(e) {
    const f = e.target.files?.[0] || null
    setFile(f)
    setPreview(f ? URL.createObjectURL(f) : null)
  }

  async function submit() {
    if (!sku.trim() || !file) {
      setResult({ type: 'error', message: 'SKU and an image file are required.' })
      return
    }
    setBusy(true)
    setResult(null)
    try {
      const res = await api.ingestVision(sku.trim(), file)
      setResult({ type: 'ok', message: res.message, data: res.parsed_data })
    } catch (e) {
      setResult({ type: 'error', message: e.message || 'Ingest failed.' })
    } finally {
      setBusy(false)
    }
  }

  return (
    <Card className="flex flex-col">
      <CardHeader title="Delivery Photo" subtitle="Verify quantity & condition (OCR)" icon={ImageIcon} />
      <CardBody className="flex flex-1 flex-col gap-3 !pt-2">
        <SkuField value={sku} onChange={setSku} skus={skus} />
        <div className="flex-1">
          <label className="label">Image (packing slip / delivery)</label>
          <label className="flex min-h-[140px] cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-border bg-surface-2/40 p-4 text-center transition-colors hover:border-primary/50">
            {preview ? (
              <img src={preview} alt="preview" className="max-h-[120px] rounded-md object-contain" />
            ) : (
              <>
                <ImageIcon size={24} className="text-muted" />
                <span className="text-xs text-muted">Click to choose a .jpg / .png</span>
              </>
            )}
            <input type="file" accept="image/*" className="hidden" onChange={onFile} />
          </label>
          {file && <p className="mt-1.5 truncate text-[11px] text-muted">{file.name}</p>}
        </div>
        <button className="btn-primary w-full" onClick={submit} disabled={busy}>
          {busy ? <Spinner size={14} /> : <Upload size={14} />}
          {busy ? 'Analyzing…' : 'Ingest photo'}
        </button>
        <ResultView state={result} />
      </CardBody>
    </Card>
  )
}

/* ---------------- Schedule ---------------- */
function SchedulePanel() {
  const [file, setFile] = useState(null)
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)

  async function submit() {
    if (!file) {
      setResult({ type: 'error', message: 'A Primavera XML file is required.' })
      return
    }
    setBusy(true)
    setResult(null)
    try {
      const res = await api.ingestSchedule(file)
      setResult({
        type: 'ok',
        message: res.message,
        data: { activities_count: res.activities_count },
      })
    } catch (e) {
      setResult({ type: 'error', message: e.message || 'Ingest failed.' })
    } finally {
      setBusy(false)
    }
  }

  return (
    <Card className="flex flex-col">
      <CardHeader title="Project Schedule" subtitle="Import Primavera / MS Project XML" icon={CalendarRange} />
      <CardBody className="flex flex-1 flex-col gap-3 !pt-2">
        <div className="flex-1">
          <label className="label">Schedule file (.xml)</label>
          <label className="flex min-h-[196px] cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed border-border bg-surface-2/40 p-4 text-center transition-colors hover:border-primary/50">
            <CalendarRange size={26} className="text-muted" />
            <span className="text-xs text-muted">
              {file ? file.name : 'Click to choose a Primavera XML export'}
            </span>
            <input type="file" accept=".xml,text/xml,application/xml" className="hidden" onChange={(e) => setFile(e.target.files?.[0] || null)} />
          </label>
          <p className="mt-2 text-[11px] text-muted">
            Rebuilds the activity network and recomputes cascade impact. Invalid files fall back to a demo schedule.
          </p>
        </div>
        <button className="btn-primary w-full" onClick={submit} disabled={busy}>
          {busy ? <Spinner size={14} /> : <Upload size={14} />}
          {busy ? 'Importing…' : 'Ingest schedule'}
        </button>
        <ResultView state={result} />
      </CardBody>
    </Card>
  )
}
