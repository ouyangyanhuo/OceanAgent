<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import {
  Expand,
  GitFork,
  Maximize,
  MousePointer2,
  Move,
  Search,
  Settings,
  X,
  ZoomIn,
  ZoomOut,
} from 'lucide-vue-next'
import { fetchExpandOptions, fetchGraph, expandNode as apiExpandNode } from '../services/graph'

/* ── 常量映射 ── */
const NODE_TYPE_COLORS = {
  SeaArea: 'blue',
  Buoy: 'green',
  Observation: 'cyan',
  RiskFactor: 'rose',
  RedTideEvent: 'rose',
  CurrentField: 'blue',
  Species: 'teal',
  FisheryArea: 'green',
  Route: 'violet',
  PreventionMeasure: 'amber',
  Agent: 'violet',
  Report: 'amber',
}

const NODE_TYPE_LABELS = {
  SeaArea: '海域',
  Buoy: '浮标',
  Observation: '观测',
  RiskFactor: '风险因子',
  RedTideEvent: '赤潮事件',
  CurrentField: '海流场',
  Species: '物种',
  FisheryArea: '渔场',
  Route: '航线',
  PreventionMeasure: '防治措施',
  Agent: '智能体',
  Report: '报告',
}

const RELATION_LABELS = {
  located_in: '位于',
  monitored_by: '被监测',
  observed_by: '被观测',
  has_observation: '包含观测',
  has_risk_event: '存在风险事件',
  affected_by: '受影响',
  indicates: '指示',
  may_trigger: '可能引发',
  mitigated_by: '被缓解',
  correlated_with: '相关',
  suitable_for: '适宜',
  route_passes_through: '航线经过',
  influences: '影响',
  generates_report: '生成报告',
}

const SOLID_RELATIONS = new Set([
  'located_in', 'monitored_by', 'observed_by', 'has_observation',
  'has_risk_event', 'affected_by', 'indicates', 'may_trigger',
  'mitigated_by', 'influences', 'generates_report',
])

/* ── 状态 ── */
const graphNodes = ref([])
const graphEdges = ref([])
const loading = ref(true)
const selectedNode = ref(null)
const expandOptions = ref([])
const expanding = ref(false)
const searchQuery = ref('')
const filterRelation = ref('all')
const canvasRef = ref(null)

/* ── 画布变换 ── */
const transform = reactive({ x: 0, y: 0, scale: 1 })
const isDragging = ref(false)
const dragStart = reactive({ x: 0, y: 0 })

/* ── 工具栏 ── */
const tools = [
  { icon: MousePointer2, label: '选择', mode: 'select' },
  { icon: Move, label: '拖拽', mode: 'drag' },
  { icon: ZoomIn, label: '放大', mode: 'zoomIn' },
  { icon: ZoomOut, label: '缩小', mode: 'zoomOut' },
  { icon: Maximize, label: '适应画布', mode: 'fit' },
  { icon: Expand, label: '展开', mode: 'expand' },
]
const activeTool = ref(0)

/* ── 力导向布局 ── */
const layoutPositions = ref({})

function runForceLayout(nodes, edges, width = 900, height = 600) {
  const positions = {}
  const n = nodes.length
  if (n === 0) return positions

  // 初始位置：圆形分布
  const cx = width / 2
  const cy = height / 2
  const radius = Math.min(width, height) * 0.32

  nodes.forEach((node, i) => {
    const angle = (2 * Math.PI * i) / n
    positions[node.id] = {
      x: cx + radius * Math.cos(angle) + (Math.random() - 0.5) * 40,
      y: cy + radius * Math.sin(angle) + (Math.random() - 0.5) * 40,
    }
  })

  // 参数
  const k = Math.sqrt((width * height) / n) * 0.85 // 理想距离
  const iterations = 120
  const gravity = 0.06
  const repulsion = k * k
  const damping = 0.85

  const velocities = {}
  nodes.forEach((node) => { velocities[node.id] = { x: 0, y: 0 } })

  const edgeSet = new Set(edges.map((e) => `${e.source}|${e.target}`))

  for (let iter = 0; iter < iterations; iter++) {
    const temp = 1 - iter / iterations // 降温

    // 排斥力
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        const a = nodes[i].id
        const b = nodes[j].id
        let dx = positions[a].x - positions[b].x
        let dy = positions[a].y - positions[b].y
        const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1)
        const force = repulsion / (dist * dist)
        const fx = (dx / dist) * force * temp
        const fy = (dy / dist) * force * temp
        velocities[a].x += fx
        velocities[a].y += fy
        velocities[b].x -= fx
        velocities[b].y -= fy
      }
    }

    // 吸引力（边）
    edges.forEach((edge) => {
      const sa = positions[edge.source]
      const sb = positions[edge.target]
      if (!sa || !sb) return
      let dx = sb.x - sa.x
      let dy = sb.y - sa.y
      const dist = Math.max(Math.sqrt(dx * dx + dy * dy), 1)
      const force = (dist * dist) / k
      const fx = (dx / dist) * force * temp * 0.4
      const fy = (dy / dist) * force * temp * 0.4
      velocities[edge.source].x += fx
      velocities[edge.source].y += fy
      velocities[edge.target].x -= fx
      velocities[edge.target].y -= fy
    })

    // 向心力
    nodes.forEach((node) => {
      const pos = positions[node.id]
      velocities[node.id].x += (cx - pos.x) * gravity * temp
      velocities[node.id].y += (cy - pos.y) * gravity * temp
    })

    // 应用速度
    nodes.forEach((node) => {
      const vel = velocities[node.id]
      vel.x *= damping
      vel.y *= damping
      positions[node.id].x += vel.x
      positions[node.id].y += vel.y

      // 边界约束
      const margin = 60
      positions[node.id].x = Math.max(margin, Math.min(width - margin, positions[node.id].x))
      positions[node.id].y = Math.max(margin, Math.min(height - margin, positions[node.id].y))
    })
  }

  return positions
}

/* ── 计算属性 ── */
const nodeById = computed(() => {
  const map = {}
  graphNodes.value.forEach((n) => { map[n.id] = n })
  return map
})

const visibleEdges = computed(() => {
  if (filterRelation.value === 'all') return graphEdges.value
  return graphEdges.value.filter((e) => e.relation === filterRelation.value)
})

const relationTypes = computed(() => {
  const set = new Set(graphEdges.value.map((e) => e.relation))
  return [...set]
})

const usedNodeTypes = computed(() => {
  const set = new Set(graphNodes.value.map((n) => n.type))
  return [...set]
})

const graphStats = computed(() => `${graphNodes.value.length} 个节点 · ${graphEdges.value.length} 条关系`)

/* ── 数据加载 ── */
async function loadGraph() {
  loading.value = true
  const data = await fetchGraph()
  graphNodes.value = data.nodes || []
  graphEdges.value = data.edges || []
  loading.value = false

  await nextTick()
  relayout()
}

function relayout() {
  const canvas = canvasRef.value
  const w = canvas?.clientWidth || 900
  const h = canvas?.clientHeight || 600
  layoutPositions.value = runForceLayout(graphNodes.value, graphEdges.value, w, h)
  fitCanvas()
}

function fitCanvas() {
  const canvas = canvasRef.value
  if (!canvas || graphNodes.value.length === 0) return

  const w = canvas.clientWidth
  const h = canvas.clientHeight
  const positions = layoutPositions.value

  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity
  Object.values(positions).forEach((p) => {
    minX = Math.min(minX, p.x)
    maxX = Math.max(maxX, p.x)
    minY = Math.min(minY, p.y)
    maxY = Math.max(maxY, p.y)
  })

  const padding = 100
  const graphW = maxX - minX + padding * 2
  const graphH = maxY - minY + padding * 2
  const scale = Math.min(w / graphW, h / graphH, 1.5)
  const cx = (minX + maxX) / 2
  const cy = (minY + maxY) / 2

  transform.scale = scale
  transform.x = w / 2 - cx * scale
  transform.y = h / 2 - cy * scale
}

/* ── 交互 ── */
function onNodeClick(node) {
  if (selectedNode.value?.id === node.id) {
    selectedNode.value = null
    expandOptions.value = []
    return
  }
  selectedNode.value = node
  loadExpandOptions(node.id)
}

async function loadExpandOptions(nodeId) {
  const data = await fetchExpandOptions(nodeId)
  expandOptions.value = data.options || []
}

async function handleExpand(expandType) {
  if (!selectedNode.value || expanding.value) return
  expanding.value = true

  const result = await apiExpandNode(selectedNode.value.id, expandType)
  if (result) {
    // 合并新节点
    const existingIds = new Set(graphNodes.value.map((n) => n.id))
    const newNodes = (result.new_nodes || []).filter((n) => !existingIds.has(n.id))
    graphNodes.value.push(...newNodes)

    // 合并新边
    const existingEdgeIds = new Set(graphEdges.value.map((e) => e.id))
    const newEdges = (result.new_edges || []).filter((e) => !existingEdgeIds.has(e.id))
    graphEdges.value.push(...newEdges)

    // 更新展开状态
    if (result.center_node) {
      const idx = graphNodes.value.findIndex((n) => n.id === result.center_node.id)
      if (idx !== -1) graphNodes.value[idx] = result.center_node
    }

    // 重新布局
    await nextTick()
    relayout()

    // 刷新展开选项
    if (selectedNode.value) {
      loadExpandOptions(selectedNode.value.id)
    }
  }
  expanding.value = false
}

function onCanvasMouseDown(e) {
  if (tools[activeTool.value].mode === 'drag' || e.shiftKey) {
    isDragging.value = true
    dragStart.x = e.clientX - transform.x
    dragStart.y = e.clientY - transform.y
    e.preventDefault()
  }
}

function onCanvasMouseMove(e) {
  if (isDragging.value) {
    transform.x = e.clientX - dragStart.x
    transform.y = e.clientY - dragStart.y
  }
}

function onCanvasMouseUp() {
  isDragging.value = false
}

function onCanvasWheel(e) {
  const delta = e.deltaY > 0 ? 0.92 : 1.08
  const rect = canvasRef.value.getBoundingClientRect()
  const mx = e.clientX - rect.left
  const my = e.clientY - rect.top

  transform.x = mx - (mx - transform.x) * delta
  transform.y = my - (my - transform.y) * delta
  transform.scale *= delta
  transform.scale = Math.max(0.2, Math.min(3, transform.scale))
  e.preventDefault()
}

function setTool(index) {
  const mode = tools[index].mode
  if (mode === 'fit') {
    fitCanvas()
    return
  }
  if (mode === 'zoomIn') {
    transform.scale = Math.min(3, transform.scale * 1.25)
    return
  }
  if (mode === 'zoomOut') {
    transform.scale = Math.max(0.2, transform.scale * 0.8)
    return
  }
  if (mode === 'expand' && selectedNode.value) {
    const first = expandOptions.value.find((o) => !o.expanded)
    if (first) handleExpand(first.expand_type)
    return
  }
  activeTool.value = index
}

function closeDetail() {
  selectedNode.value = null
  expandOptions.value = []
}

/* ── 节点位置辅助 ── */
function nodePos(nodeId) {
  return layoutPositions.value[nodeId] || { x: 0, y: 0 }
}

/* ── 搜索高亮 ── */
const highlightedIds = computed(() => {
  if (!searchQuery.value.trim()) return null
  const q = searchQuery.value.trim().toLowerCase()
  return new Set(
    graphNodes.value
      .filter((n) => n.name.toLowerCase().includes(q))
      .map((n) => n.id),
  )
})

function isDimmed(nodeId) {
  if (!highlightedIds.value) return false
  return !highlightedIds.value.has(nodeId)
}

/* ── 生命周期 ── */
onMounted(() => {
  loadGraph()
})
</script>

<template>
  <section class="panel graph-panel">
    <!-- 头部 -->
    <header class="graph-header">
      <div class="graph-header-left">
        <h2>信息关系图谱</h2>
        <span class="graph-stats">{{ graphStats }}</span>
      </div>
      <div class="graph-controls">
        <div class="graph-search">
          <Search :size="16" />
          <input v-model="searchQuery" placeholder="搜索节点..." />
        </div>
        <select v-model="filterRelation" class="graph-select">
          <option value="all">全部关系</option>
          <option v-for="r in relationTypes" :key="r" :value="r">
            {{ RELATION_LABELS[r] || r }}
          </option>
        </select>
        <div class="graph-actions">
          <button aria-label="全屏" title="全屏"><Maximize :size="16" /></button>
          <button aria-label="设置" title="设置"><Settings :size="16" /></button>
        </div>
      </div>
    </header>

    <!-- 画布 -->
    <div
      ref="canvasRef"
      class="graph-canvas"
      @mousedown="onCanvasMouseDown"
      @mousemove="onCanvasMouseMove"
      @mouseup="onCanvasMouseUp"
      @mouseleave="onCanvasMouseUp"
      @wheel="onCanvasWheel"
    >
      <!-- 工具栏 -->
      <div class="graph-tools">
        <button
          v-for="(tool, index) in tools"
          :key="tool.label"
          :class="{ active: activeTool === index }"
          :title="tool.label"
          @click="setTool(index)"
        >
          <component :is="tool.icon" :size="18" />
        </button>
      </div>

      <!-- 世界坐标容器：统一处理平移缩放 -->
      <div
        class="world-wrapper"
        :style="{ transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})` }"
      >
        <!-- SVG 边层 -->
        <svg class="edge-layer">
          <defs>
            <filter id="edgeGlow">
              <feGaussianBlur stdDeviation="0.6" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <g v-for="edge in visibleEdges" :key="edge.id">
            <line
              :x1="nodePos(edge.source).x"
              :y1="nodePos(edge.source).y"
              :x2="nodePos(edge.target).x"
              :y2="nodePos(edge.target).y"
              :class="{ dashed: !SOLID_RELATIONS.has(edge.relation) }"
              filter="url(#edgeGlow)"
            />
            <text
              class="edge-label"
              :x="(nodePos(edge.source).x + nodePos(edge.target).x) / 2"
              :y="(nodePos(edge.source).y + nodePos(edge.target).y) / 2 - 6"
            >
              {{ RELATION_LABELS[edge.relation] || edge.relation }}
            </text>
          </g>
        </svg>

        <!-- 节点层 -->
        <div
          v-for="node in graphNodes"
          :key="node.id"
          class="graph-node"
          :class="[
            `tone-${NODE_TYPE_COLORS[node.type] || 'blue'}`,
            { core: node.type === 'SeaArea', dimmed: isDimmed(node.id), selected: selectedNode?.id === node.id },
          ]"
          :style="{
            left: `${nodePos(node.id).x}px`,
            top: `${nodePos(node.id).y}px`,
          }"
          @click="onNodeClick(node)"
        >
          <span>{{ node.name }}</span>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="graph-loading">
        <div class="graph-loading-spinner"></div>
        <span>加载图谱数据...</span>
      </div>

      <!-- 缩略图 -->
      <div class="mini-map">
        <div class="mini-map-header"><span>缩略图</span></div>
        <div class="mini-map-content">
          <span
            v-for="node in graphNodes"
            :key="`mini-${node.id}`"
            :style="{
              left: `${((nodePos(node.id).x || 0) / 1000) * 100}%`,
              top: `${((nodePos(node.id).y || 0) / 700) * 100}%`,
            }"
          ></span>
        </div>
      </div>

      <!-- 图例 -->
      <div class="legend">
        <div class="legend-section">
          <span class="legend-title">关系类型</span>
          <span v-for="r in relationTypes" :key="r">
            <i :class="{ dash: !SOLID_RELATIONS.has(r) }"></i>{{ RELATION_LABELS[r] || r }}
          </span>
        </div>
        <div class="legend-section">
          <span class="legend-title">节点类型</span>
          <span v-for="t in usedNodeTypes" :key="t">
            <b :class="NODE_TYPE_COLORS[t] || 'blue'"></b>{{ NODE_TYPE_LABELS[t] || t }}
          </span>
        </div>
      </div>
    </div>

    <!-- 节点详情面板 -->
    <Transition name="slide">
      <div v-if="selectedNode" class="node-detail">
        <div class="node-detail-header">
          <div>
            <span class="node-detail-type" :class="`tone-${NODE_TYPE_COLORS[selectedNode.type] || 'blue'}`">
              {{ NODE_TYPE_LABELS[selectedNode.type] || selectedNode.type }}
            </span>
            <h3>{{ selectedNode.name }}</h3>
          </div>
          <button class="node-detail-close" @click="closeDetail"><X :size="18" /></button>
        </div>

        <div class="node-detail-body">
          <div v-if="Object.keys(selectedNode.properties).length" class="node-detail-section">
            <span class="node-detail-label">属性</span>
            <div class="node-detail-props">
              <div v-for="(val, key) in selectedNode.properties" :key="key" class="node-detail-prop">
                <span class="prop-key">{{ key }}</span>
                <span class="prop-val">{{ val }}</span>
              </div>
            </div>
          </div>

          <div class="node-detail-section">
            <span class="node-detail-label">扩展方向</span>
            <div v-if="expandOptions.length" class="expand-options">
              <button
                v-for="opt in expandOptions"
                :key="opt.expand_type"
                class="expand-btn"
                :class="{ expanded: opt.expanded }"
                :disabled="opt.expanded || expanding"
                @click="handleExpand(opt.expand_type)"
              >
                <GitFork :size="14" />
                <span>{{ opt.label }}</span>
                <span v-if="opt.expanded" class="expand-badge">已扩展</span>
                <span v-else-if="expanding" class="expand-badge loading">扩展中...</span>
              </button>
            </div>
            <div v-else class="node-detail-empty">无可用扩展方向</div>
          </div>

          <div class="node-detail-section">
            <span class="node-detail-label">元数据</span>
            <div class="node-detail-meta">
              <span>来源: {{ selectedNode.metadata?.source || '-' }}</span>
              <span>版本: {{ selectedNode.metadata?.version || '-' }}</span>
              <span>创建: {{ selectedNode.metadata?.created_at || '-' }}</span>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </section>
</template>
