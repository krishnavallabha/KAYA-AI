import { useMemo } from 'react'
import { useTheme } from '../context/ThemeContext'

function readVar(name, fallback) {
  if (typeof window === 'undefined') return fallback
  const raw = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  if (!raw) return fallback
  const parts = raw.split(/\s+/)
  return `rgb(${parts.join(', ')})`
}

/**
 * Resolves the theme CSS variables into concrete rgb() strings for Recharts.
 * Recomputes whenever the theme flips so charts restyle instantly.
 */
export function useChartColors() {
  const { theme } = useTheme()
  return useMemo(
    () => ({
      primary: readVar('--c-primary', '#2563eb'),
      ok: readVar('--c-ok', '#16a34a'),
      warn: readVar('--c-warn', '#d97706'),
      danger: readVar('--c-danger', '#dc2626'),
      info: readVar('--c-info', '#0891b2'),
      muted: readVar('--c-text-muted', '#64748b'),
      border: readVar('--c-border', '#e2e8f0'),
      surface: readVar('--c-surface', '#ffffff'),
      text: readVar('--c-text', '#0f172a'),
    }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [theme],
  )
}

/** Fixed, theme-agnostic palette for material lifecycle stages. */
export const STATUS_COLORS = {
  ORDERED: '#94a3b8',
  FABRICATING: '#a855f7',
  SHIPPED: '#3b82f6',
  IN_TRANSIT: '#06b6d4',
  DELIVERED: '#22c55e',
}
