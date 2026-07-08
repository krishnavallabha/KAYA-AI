import { useEffect, useMemo } from 'react'
import ReactFlow, {
  Background,
  Controls,
  Handle,
  Position,
  MarkerType,
  useNodesState,
  useEdgesState,
} from 'reactflow'
import 'reactflow/dist/style.css'
import dagre from 'dagre'
import { formatDate } from '../../lib/format'

const NODE_W = 210
const NODE_H = 96

const STATUS_DOT = {
  COMPLETED: 'bg-ok',
  IN_PROGRESS: 'bg-info',
  NOT_STARTED: 'bg-muted',
}

/* ---- custom node ---- */
function ActivityNode({ data, selected }) {
  const critical = data.is_critical
  return (
    <div
      className={`w-[210px] rounded-xl border-2 bg-surface px-3 py-2.5 shadow-card transition-colors ${
        selected
          ? 'border-primary ring-2 ring-primary/30'
          : critical
            ? 'border-danger/60'
            : 'border-border'
      }`}
    >
      <Handle type="target" position={Position.Left} className="!h-2 !w-2 !border-0 !bg-muted" />
      <div className="flex items-center justify-between gap-2">
        <span className="text-[10px] font-semibold uppercase tracking-wide text-muted">
          #{data.id}
        </span>
        {critical && (
          <span className="rounded bg-danger/10 px-1.5 py-0.5 text-[9px] font-bold uppercase text-danger">
            Critical
          </span>
        )}
      </div>
      <div className="mt-0.5 truncate text-sm font-semibold text-content">{data.label}</div>
      <div className="mt-1 flex items-center gap-1.5">
        <span className={`h-1.5 w-1.5 rounded-full ${STATUS_DOT[data.status] || 'bg-muted'}`} />
        <span className="text-[10px] text-muted">
          {formatDate(data.start, { month: 'short', day: 'numeric' })} →{' '}
          {formatDate(data.end, { month: 'short', day: 'numeric' })}
        </span>
      </div>
      <Handle type="source" position={Position.Right} className="!h-2 !w-2 !border-0 !bg-muted" />
    </div>
  )
}

const nodeTypes = { activity: ActivityNode }

function layout(graph, colors) {
  const g = new dagre.graphlib.Graph()
  g.setDefaultEdgeLabel(() => ({}))
  g.setGraph({ rankdir: 'LR', nodesep: 40, ranksep: 90, marginx: 20, marginy: 20 })

  graph.nodes.forEach((n) => g.setNode(n.id, { width: NODE_W, height: NODE_H }))
  graph.links.forEach((e) => g.setEdge(e.source, e.target))
  dagre.layout(g)

  const criticalSet = new Set(graph.nodes.filter((n) => n.is_critical).map((n) => n.id))

  const rfNodes = graph.nodes.map((n) => {
    const p = g.node(n.id)
    return {
      id: n.id,
      type: 'activity',
      position: { x: p.x - NODE_W / 2, y: p.y - NODE_H / 2 },
      data: n,
    }
  })

  const rfEdges = graph.links.map((e) => {
    const onCritical = criticalSet.has(e.source) && criticalSet.has(e.target)
    return {
      id: `${e.source}-${e.target}`,
      source: e.source,
      target: e.target,
      type: 'smoothstep',
      animated: onCritical,
      label: e.type,
      labelBgPadding: [4, 2],
      labelBgStyle: { fill: colors.surface, fillOpacity: 0.9 },
      labelStyle: { fill: colors.muted, fontSize: 10, fontWeight: 600 },
      style: { stroke: onCritical ? colors.danger : colors.muted, strokeWidth: onCritical ? 2.4 : 1.6 },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: onCritical ? colors.danger : colors.muted,
        width: 16,
        height: 16,
      },
    }
  })

  return { rfNodes, rfEdges }
}

export default function ScheduleGraph({ graph, colors, onSelect }) {
  const { rfNodes, rfEdges } = useMemo(
    () => layout(graph, colors),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [graph, colors.danger, colors.muted, colors.surface],
  )

  const [nodes, setNodes, onNodesChange] = useNodesState(rfNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(rfEdges)

  useEffect(() => {
    setNodes(rfNodes)
    setEdges(rfEdges)
  }, [rfNodes, rfEdges, setNodes, setEdges])

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      nodeTypes={nodeTypes}
      onNodeClick={(_, node) => onSelect?.(node.data)}
      fitView
      fitViewOptions={{ padding: 0.2 }}
      minZoom={0.3}
      maxZoom={1.6}
      proOptions={{ hideAttribution: true }}
      nodesConnectable={false}
      nodesDraggable
    >
      <Background gap={18} size={1} color={colors.border} />
      <Controls showInteractive={false} />
    </ReactFlow>
  )
}
