/**
 * FlowSense API client.
 *
 * - Talks to the FastAPI backend at `${VITE_API_BASE_URL}/api/v1`.
 * - If the backend is unreachable (network error / timeout / non-2xx on read),
 *   it transparently falls back to a bundled, *interactive* demo store so the
 *   dashboard always works for demos and screenshots.
 * - Connection status is broadcast so the UI can show a "Demo data" banner.
 */

import {
  mockMaterials,
  mockActivities,
  mockScheduleGraph,
  mockAlerts,
  mockActions,
} from '../data/mockData'

export const API_BASE =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || 'http://localhost:8000'
export const API_V1 = `${API_BASE}/api/v1`

const REQUEST_TIMEOUT_MS = 4000

/* ---------------- connection status pub/sub ---------------- */
let liveBackend = null // null = unknown, true = live, false = demo fallback
const listeners = new Set()

function setLive(value) {
  if (liveBackend !== value) {
    liveBackend = value
    listeners.forEach((l) => l(value))
  }
}

export function onConnectionChange(cb) {
  listeners.add(cb)
  // fire immediately with current known state
  cb(liveBackend)
  return () => listeners.delete(cb)
}

export function isLive() {
  return liveBackend
}

/* ---------------- interactive in-memory demo store ---------------- */
const clone = (v) => JSON.parse(JSON.stringify(v))

const demo = {
  materials: clone(mockMaterials),
  activities: clone(mockActivities),
  graph: clone(mockScheduleGraph),
  alerts: clone(mockAlerts),
  actions: clone(mockActions),
}

/* ---------------- low-level fetch with timeout ---------------- */
async function request(path, { method = 'GET', body, headers, isForm } = {}) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)
  try {
    const res = await fetch(`${API_V1}${path}`, {
      method,
      headers: isForm ? headers : { 'Content-Type': 'application/json', ...headers },
      body: isForm ? body : body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    })
    if (!res.ok) {
      const text = await res.text().catch(() => '')
      const err = new Error(`HTTP ${res.status}: ${text || res.statusText}`)
      err.status = res.status
      throw err
    }
    setLive(true)
    const ct = res.headers.get('content-type') || ''
    return ct.includes('application/json') ? res.json() : res.text()
  } catch (err) {
    // A 4xx from a *reachable* backend is a real API error — surface it.
    if (err.status && err.status >= 400 && err.status < 500) {
      setLive(true)
      throw err
    }
    // Otherwise the backend is unreachable → demo mode.
    setLive(false)
    throw err
  } finally {
    clearTimeout(timer)
  }
}

/* ---------------- helpers for demo ingest simulation ---------------- */
const STATUS_KEYWORDS = [
  ['DELIVERED', /deliver|received|arrived|offloaded/i],
  ['IN_TRANSIT', /in transit|en route|on the way|dispatched|out for delivery/i],
  ['SHIPPED', /shipp|shipment|left (the )?(factory|yard)|bill of lading|bol/i],
  ['FABRICATING', /fabricat|in production|manufactur|being made/i],
  ['ORDERED', /order (placed|confirmed)|po (received|confirmed)/i],
]

function inferStatusFromText(text) {
  for (const [status, re] of STATUS_KEYWORDS) if (re.test(text)) return status
  return null
}

/* ============================================================
   Public API — each method returns live data, or demo on fallback.
   ============================================================ */
export const api = {
  /* ---- materials ---- */
  async getMaterials() {
    try {
      return await request('/materials/')
    } catch {
      return clone(demo.materials)
    }
  },

  async getMaterial(id) {
    try {
      return await request(`/materials/${id}`)
    } catch {
      const m = demo.materials.find((x) => x.id === Number(id))
      if (!m) throw new Error('Material not found')
      return clone(m)
    }
  },

  async createMaterial(payload) {
    try {
      return await request('/materials/', { method: 'POST', body: payload })
    } catch {
      const created = {
        id: Math.max(0, ...demo.materials.map((m) => m.id)) + 1,
        current_location: null,
        forecast_delivery_date: null,
        delay_probability: 0,
        confidence_score: 1,
        activity_id: null,
        description: null,
        quantity: 1,
        status: 'ORDERED',
        vendor_name: null,
        ...payload,
      }
      demo.materials.push(created)
      return clone(created)
    }
  },

  /* ---- schedule ---- */
  async getActivities() {
    try {
      return await request('/schedule/activities')
    } catch {
      return clone(demo.activities)
    }
  },

  async getScheduleGraph() {
    try {
      return await request('/schedule/graph')
    } catch {
      return clone(demo.graph)
    }
  },

  /* ---- alerts ---- */
  async getAlerts() {
    try {
      return await request('/alerts/')
    } catch {
      return clone(demo.alerts.filter((a) => !a.is_resolved))
    }
  },

  async resolveAlert(id) {
    try {
      return await request(`/alerts/${id}/resolve`, { method: 'POST' })
    } catch {
      const a = demo.alerts.find((x) => x.id === Number(id))
      if (a) a.is_resolved = true
      return { message: 'Alert marked as resolved' }
    }
  },

  /* ---- actions ---- */
  async getDrafts() {
    try {
      return await request('/actions/drafts')
    } catch {
      return clone(demo.actions.filter((a) => a.status === 'DRAFT'))
    }
  },

  async executeAction(id) {
    try {
      return await request(`/actions/${id}/execute`, { method: 'POST' })
    } catch {
      const a = demo.actions.find((x) => x.id === Number(id))
      if (a) a.status = 'SENT'
      return {
        message: `Action of type '${a?.action_type || 'EMAIL_VENDOR'}' was successfully executed (Simulated)`,
      }
    }
  },

  /* ---- ingest ---- */
  async ingestEmail(emailText, materialSku) {
    const form = new FormData()
    form.append('email_text', emailText)
    form.append('material_sku', materialSku)
    try {
      return await request('/ingest/email', { method: 'POST', body: form, isForm: true })
    } catch (err) {
      if (err.status) throw err // real API error (e.g. 404 unknown SKU)
      const mat = demo.materials.find((m) => m.sku === materialSku)
      if (!mat) {
        const e = new Error('Material SKU not found')
        e.status = 404
        throw e
      }
      const status = inferStatusFromText(emailText) || mat.status
      mat.status = status
      const parsed = {
        sku: materialSku,
        status,
        current_location: /delay|late|hold/i.test(emailText)
          ? mat.current_location
          : mat.current_location,
        estimated_delivery_date: mat.forecast_delivery_date,
        confidence_weight: 0.8,
        explanation: `(Demo) Extracted status "${status}" from email text.`,
      }
      return { message: 'Email ingested successfully', parsed_data: parsed }
    }
  },

  async ingestVision(materialSku, file) {
    const form = new FormData()
    form.append('material_sku', materialSku)
    form.append('file', file)
    try {
      return await request('/ingest/vision', { method: 'POST', body: form, isForm: true })
    } catch (err) {
      if (err.status) throw err
      const mat = demo.materials.find((m) => m.sku === materialSku)
      if (!mat) {
        const e = new Error('Material SKU not found')
        e.status = 404
        throw e
      }
      mat.status = 'DELIVERED'
      mat.current_location = 'Site warehouse'
      const parsed = {
        sku: materialSku,
        quantity_verified: mat.quantity,
        status: 'DELIVERED',
        condition: 'GOOD',
        explanation: `(Demo) Image verifies delivery of ${mat.quantity} units in good condition.`,
      }
      return { message: 'Vision photo ingested successfully', parsed_data: parsed }
    }
  },

  async ingestSchedule(file) {
    const form = new FormData()
    form.append('file', file)
    try {
      return await request('/ingest/schedule', { method: 'POST', body: form, isForm: true })
    } catch (err) {
      if (err.status) throw err
      return {
        message: 'Schedule ingested successfully',
        activities_count: demo.activities.length,
      }
    }
  },
}

export default api
