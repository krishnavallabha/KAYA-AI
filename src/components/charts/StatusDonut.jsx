import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { STATUS_COLORS, useChartColors } from '../../hooks/useChartColors'
import { titleCase } from '../../lib/format'
import { MATERIAL_LIFECYCLE } from '../../lib/format'

export default function StatusDonut({ materials = [] }) {
  const c = useChartColors()

  const counts = MATERIAL_LIFECYCLE.map((status) => ({
    name: titleCase(status),
    key: status,
    value: materials.filter((m) => m.status === status).length,
  })).filter((d) => d.value > 0)

  const total = materials.length

  if (!total) {
    return <div className="grid h-[240px] place-items-center text-sm text-muted">No orders</div>
  }

  return (
    <div className="relative h-[240px]">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={counts}
            dataKey="value"
            nameKey="name"
            innerRadius={62}
            outerRadius={90}
            paddingAngle={2}
            stroke="none"
          >
            {counts.map((entry) => (
              <Cell key={entry.key} fill={STATUS_COLORS[entry.key]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: c.surface,
              border: `1px solid ${c.border}`,
              borderRadius: 10,
              color: c.text,
              fontSize: 12,
            }}
            itemStyle={{ color: c.text }}
          />
          <Legend
            verticalAlign="bottom"
            height={24}
            iconType="circle"
            iconSize={8}
            formatter={(value) => <span style={{ color: c.muted, fontSize: 12 }}>{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center pb-8">
        <span className="text-3xl font-bold text-content">{total}</span>
        <span className="text-xs text-muted">orders</span>
      </div>
    </div>
  )
}
