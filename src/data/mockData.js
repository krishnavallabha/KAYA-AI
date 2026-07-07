/**
 * Bundled demo data — used as a graceful fallback when the FlowSense
 * FastAPI backend is unreachable, so the dashboard always renders for
 * demos and screenshots. Field names mirror backend/schemas.py exactly.
 *
 * Storyline: Order SKU-482 (structural steel) is late; the cascade engine
 * flags a critical-path impact of 11 days; an escalation email is drafted.
 */

export const mockMaterials = [
  {
    id: 1,
    sku: 'SKU-482',
    description: 'Structural steel beams (W12x40)',
    quantity: 24,
    status: 'IN_TRANSIT',
    current_location: 'Freight hub, Pune',
    vendor_name: 'SteelCorp Ltd',
    promised_delivery_date: '2026-07-15T00:00:00',
    activity_id: 2,
    forecast_delivery_date: '2026-07-26T00:00:00',
    delay_probability: 0.78,
    confidence_score: 0.91,
  },
  {
    id: 2,
    sku: 'SKU-994',
    description: 'Rebar panels #6 grade 60',
    quantity: 50,
    status: 'FABRICATING',
    current_location: 'SteelCorp fab yard, Nashik',
    vendor_name: 'ConcreteSupply Co',
    promised_delivery_date: '2026-07-22T00:00:00',
    activity_id: 5,
    forecast_delivery_date: '2026-07-24T00:00:00',
    delay_probability: 0.34,
    confidence_score: 0.88,
  },
  {
    id: 3,
    sku: 'SKU-233',
    description: 'Galvanized metal decking sheets',
    quantity: 120,
    status: 'ORDERED',
    current_location: null,
    vendor_name: 'DeckPro Industries',
    promised_delivery_date: '2026-07-28T00:00:00',
    activity_id: 3,
    forecast_delivery_date: '2026-07-31T00:00:00',
    delay_probability: 0.41,
    confidence_score: 0.72,
  },
  {
    id: 4,
    sku: 'SKU-660',
    description: 'HVAC ducting, spiral 12"',
    quantity: 40,
    status: 'SHIPPED',
    current_location: 'Regional DC, Mumbai',
    vendor_name: 'AirFlow Systems',
    promised_delivery_date: '2026-07-19T00:00:00',
    activity_id: 4,
    forecast_delivery_date: '2026-07-20T00:00:00',
    delay_probability: 0.18,
    confidence_score: 0.9,
  },
  {
    id: 5,
    sku: 'SKU-118',
    description: 'Anchor bolts, M24 galvanized',
    quantity: 500,
    status: 'DELIVERED',
    current_location: 'Site warehouse',
    vendor_name: 'FastenRight',
    promised_delivery_date: '2026-07-05T00:00:00',
    activity_id: 2,
    forecast_delivery_date: '2026-07-04T00:00:00',
    delay_probability: 0.02,
    confidence_score: 0.98,
  },
  {
    id: 6,
    sku: 'SKU-905',
    description: 'Curtain wall glass panels',
    quantity: 60,
    status: 'FABRICATING',
    current_location: 'GlassWorks plant, Chennai',
    vendor_name: 'GlassWorks Co',
    promised_delivery_date: '2026-08-05T00:00:00',
    activity_id: 6,
    forecast_delivery_date: '2026-08-12T00:00:00',
    delay_probability: 0.63,
    confidence_score: 0.8,
  },
  {
    id: 7,
    sku: 'SKU-347',
    description: 'Concrete mix additive (retarder)',
    quantity: 200,
    status: 'IN_TRANSIT',
    current_location: 'En route, NH48',
    vendor_name: 'ConcreteSupply Co',
    promised_delivery_date: '2026-07-16T00:00:00',
    activity_id: 5,
    forecast_delivery_date: '2026-07-17T00:00:00',
    delay_probability: 0.22,
    confidence_score: 0.86,
  },
  {
    id: 8,
    sku: 'SKU-512',
    description: 'Electrical conduit, EMT 2"',
    quantity: 300,
    status: 'ORDERED',
    current_location: null,
    vendor_name: 'VoltLine Supplies',
    promised_delivery_date: '2026-07-30T00:00:00',
    activity_id: 4,
    forecast_delivery_date: '2026-08-01T00:00:00',
    delay_probability: 0.29,
    confidence_score: 0.7,
  },
  {
    id: 9,
    sku: 'SKU-088',
    description: 'Steel connection plates & gussets',
    quantity: 180,
    status: 'SHIPPED',
    current_location: 'Freight hub, Pune',
    vendor_name: 'SteelCorp Ltd',
    promised_delivery_date: '2026-07-14T00:00:00',
    activity_id: 2,
    forecast_delivery_date: '2026-07-21T00:00:00',
    delay_probability: 0.66,
    confidence_score: 0.89,
  },
  {
    id: 10,
    sku: 'SKU-701',
    description: 'Waterproof membrane rolls',
    quantity: 90,
    status: 'DELIVERED',
    current_location: 'Site warehouse',
    vendor_name: 'SealTech',
    promised_delivery_date: '2026-07-03T00:00:00',
    activity_id: 1,
    forecast_delivery_date: '2026-07-03T00:00:00',
    delay_probability: 0.0,
    confidence_score: 0.97,
  },
]

export const mockActivities = [
  {
    id: 1,
    project_id: 1,
    name: 'Foundation Pour',
    scheduled_start: '2026-07-01T00:00:00',
    scheduled_end: '2026-07-06T00:00:00',
    actual_start: '2026-07-01T00:00:00',
    actual_end: '2026-07-06T00:00:00',
    is_critical_path: true,
    status: 'COMPLETED',
  },
  {
    id: 2,
    project_id: 1,
    name: 'Steel Erection',
    scheduled_start: '2026-07-12T00:00:00',
    scheduled_end: '2026-07-21T00:00:00',
    actual_start: null,
    actual_end: null,
    is_critical_path: true,
    status: 'NOT_STARTED',
  },
  {
    id: 3,
    project_id: 1,
    name: 'Metal Decking',
    scheduled_start: '2026-07-22T00:00:00',
    scheduled_end: '2026-07-28T00:00:00',
    actual_start: null,
    actual_end: null,
    is_critical_path: true,
    status: 'NOT_STARTED',
  },
  {
    id: 4,
    project_id: 1,
    name: 'MEP Rough-in',
    scheduled_start: '2026-07-22T00:00:00',
    scheduled_end: '2026-08-02T00:00:00',
    actual_start: null,
    actual_end: null,
    is_critical_path: false,
    status: 'NOT_STARTED',
  },
  {
    id: 5,
    project_id: 1,
    name: 'Concrete Pour (Slab)',
    scheduled_start: '2026-07-29T00:00:00',
    scheduled_end: '2026-08-05T00:00:00',
    actual_start: null,
    actual_end: null,
    is_critical_path: true,
    status: 'NOT_STARTED',
  },
  {
    id: 6,
    project_id: 1,
    name: 'Curtain Wall Install',
    scheduled_start: '2026-08-06T00:00:00',
    scheduled_end: '2026-08-18T00:00:00',
    actual_start: null,
    actual_end: null,
    is_critical_path: false,
    status: 'NOT_STARTED',
  },
]

export const mockScheduleGraph = {
  nodes: mockActivities.map((a) => ({
    id: String(a.id),
    label: a.name,
    start: a.scheduled_start,
    end: a.scheduled_end,
    is_critical: a.is_critical_path,
    status: a.status,
  })),
  links: [
    { source: '1', target: '2', type: 'FS' },
    { source: '2', target: '3', type: 'FS' },
    { source: '2', target: '4', type: 'FS' },
    { source: '3', target: '5', type: 'FS' },
    { source: '4', target: '5', type: 'FS' },
    { source: '5', target: '6', type: 'FS' },
  ],
}

export const mockAlerts = [
  {
    id: 1,
    project_id: 1,
    material_id: 1,
    message:
      'Material SKU SKU-482 delay impacts project critical path by 11 days.',
    severity: 'CRITICAL',
    is_resolved: false,
    created_at: '2026-07-07T09:12:00',
  },
  {
    id: 2,
    project_id: 1,
    material_id: 9,
    message:
      'Material SKU SKU-088 forecast slip of 7 days may delay Steel Erection.',
    severity: 'WARNING',
    is_resolved: false,
    created_at: '2026-07-07T08:40:00',
  },
  {
    id: 3,
    project_id: 1,
    material_id: 6,
    message:
      'Signal conflict on SKU-905: vendor portal status differs from latest email.',
    severity: 'WARNING',
    is_resolved: false,
    created_at: '2026-07-06T17:20:00',
  },
]

export const mockActions = [
  {
    id: 1,
    alert_id: 1,
    action_type: 'EMAIL_VENDOR',
    draft_content: `Subject: URGENT: Delivery Delay Escalation - SKU: SKU-482

Dear SteelCorp Ltd Team,

We are writing regarding order SKU-482 (Structural steel beams), currently forecast to arrive on 2026-07-26 against a promised date of 2026-07-15 — an 11-day slip.

This delay directly impacts the following critical-path activities on our schedule:
  - Steel Erection
  - Metal Decking
  - Concrete Pour (Slab)

As a result, projected project completion is now at risk by 11 days. We require the following within 24 hours:
  1. Current transit logs and precise location for this shipment.
  2. Available expediting options and associated lead-time reductions.
  3. A firm, revised delivery commitment.

Given the critical-path exposure, we ask that you treat this as a priority escalation.

Regards,
Project Controls
FlowSense — on behalf of the Project Management Office`,
    status: 'DRAFT',
    created_at: '2026-07-07T09:12:05',
  },
  {
    id: 2,
    alert_id: 2,
    action_type: 'EMAIL_VENDOR',
    draft_content: `Subject: Delivery Risk Notice - SKU: SKU-088

Dear SteelCorp Ltd Team,

Order SKU-088 (Steel connection plates & gussets) shows a forecast slip of 7 days versus the promised date of 2026-07-14. These components are required to begin Steel Erection.

Please confirm the current shipping status and whether partial early delivery of the erection-critical plates is possible.

Regards,
Project Controls
FlowSense — on behalf of the Project Management Office`,
    status: 'DRAFT',
    created_at: '2026-07-07T08:40:10',
  },
]

export const mockProject = {
  id: 1,
  name: 'Skyline Tower — Phase 2',
  description: 'Mixed-use high-rise, structural + envelope package',
  created_at: '2026-06-01T00:00:00',
}
