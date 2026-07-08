import Badge from './ui/Badge'
import {
  MATERIAL_STATUS_TONE,
  ACTIVITY_STATUS_TONE,
  SEVERITY_TONE,
  ACTION_STATUS_TONE,
  titleCase,
} from '../lib/format'

export function MaterialStatusBadge({ status }) {
  return <Badge tone={MATERIAL_STATUS_TONE[status] || 'neutral'} dot>{titleCase(status)}</Badge>
}

export function ActivityStatusBadge({ status }) {
  return <Badge tone={ACTIVITY_STATUS_TONE[status] || 'neutral'}>{titleCase(status)}</Badge>
}

export function SeverityBadge({ severity }) {
  return <Badge tone={SEVERITY_TONE[severity] || 'neutral'} dot>{titleCase(severity)}</Badge>
}

export function ActionStatusBadge({ status }) {
  return <Badge tone={ACTION_STATUS_TONE[status] || 'neutral'}>{titleCase(status)}</Badge>
}
