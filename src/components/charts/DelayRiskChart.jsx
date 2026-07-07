import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Cell,
  ResponsiveContainer,
  Tooltip,
  CartesianGrid,
} from 'recharts'
import { useChartColors } from '../../hooks/useChartColors'
import { riskTone } from '../../lib/format'

export default function DelayRiskChart({ materials = [], limit = 6 }) {
  const c = useChartColors()
  const toneColor = { danger: c.danger, warn: c.warn, ok: c.ok }

  const data = [...materials]
    .sort((a, b) => (b.delay_probability || 0) - (a.delay_probability || 0))
    .slice(0, limit)
    .map((m) => ({
      sku: m.sku,
      value: Math.round((m.delay_probability || 0) * 100),
      tone: riskTone(m.delay_probability),
    }))

  if (!data.length) {
    return <div className="grid h-[240px] place-items-center text-sm text-muted">No data</div>
  }

  return (
    <ResponsiveContainer width="100%" height={240}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16, top: 4, bottom: 4 }}>
        <CartesianGrid horizontal={false} stroke={c.border} strokeDasharray="3 3" />
        <XAxis
          type="number"
          domain={[0, 100]}
          tickFormatter={(v) => `${v}%`}
          tick={{ fill: c.muted, fontSize: 11 }}
          axisLine={{ stroke: c.border }}
          tickLine={false}
        />
        <YAxis
          type="category"
          dataKey="sku"
          width={72}
          tick={{ fill: c.muted, fontSize: 11 }}
          axisLine={{ stroke: c.border }}
          tickLine={false}
        />
        <Tooltip
          cursor={{ fill: c.muted, fillOpacity: 0.08 }}
          contentStyle={{
            background: c.surface,
            border: `1px solid ${c.border}`,
            borderRadius: 10,
            color: c.text,
            fontSize: 12,
          }}
          formatter={(v) => [`${v}%`, 'Delay probability']}
        />
        <Bar dataKey="value" radius={[0, 5, 5, 0]} barSize={16}>
          {data.map((d, i) => (
            <Cell key={i} fill={toneColor[d.tone]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
