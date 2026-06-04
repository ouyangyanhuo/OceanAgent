<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import cytoscape from 'cytoscape'
import {
  Bot,
  Database,
  Expand,
  Eye,
  EyeOff,
  GitFork,
  Maximize,
  Minimize,
  MousePointer2,
  Move,
  RefreshCw,
  Search,
  Settings,
  WifiOff,
  X,
  ZoomIn,
  ZoomOut,
} from 'lucide-vue-next'
import { fetchExpandOptions, fetchGraph, expandNode as apiExpandNode } from '../services/graph'

/* ── 常量映射 ── */
const NODE_TYPE_COLORS = {
  SeaArea: '#3b82f6',
  Buoy: '#22c55e',
  Observation: '#06b6d4',
  RiskFactor: '#f43f5e',
  RedTideEvent: '#f43f5e',
  CurrentField: '#3b82f6',
  Species: '#14b8a6',
  FisheryArea: '#22c55e',
  Route: '#8b5cf6',
  PreventionMeasure: '#f59e0b',
  Agent: '#8b5cf6',
  Report: '#f59e0b',
}

const NODE_TYPE_TONES = {
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
const loadError = ref(false)
const loadErrorMsg = ref('')
const selectedNode = ref(null)
const expandOptions = ref([])
const expanding = ref(false)
const expandingLabel = ref('')
const searchQuery = ref('')
const filterRelation = ref('all')
const cyContainerRef = ref(null)
const canvasWrapperRef = ref(null)

let cy = null

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

/* ── 全屏 ── */
const isFullscreen = ref(false)

function toggleFullscreen() {
  const el = canvasWrapperRef.value
  if (!el) return
  if (!document.fullscreenElement) {
    el.requestFullscreen().catch(() => {})
  } else {
    document.exitFullscreen().catch(() => {})
  }
}

function onFullscreenChange() {
  isFullscreen.value = !!document.fullscreenElement
  // 全屏切换后 Cytoscape 需要 resize
  if (cy) {
    setTimeout(() => cy.resize(), 100)
  }
}

/* ── 设置面板 ── */
const showSettings = ref(false)
const settings = ref({
  showEdgeLabels: true,
  showLegend: true,
  animateLayout: true,
})

function toggleSetting(key) {
  settings.value[key] = !settings.value[key]
  if (key === 'showEdgeLabels' && cy) {
    cy.edges().forEach((e) => {
      e.style('label', settings.value.showEdgeLabels ? (RELATION_LABELS[e.data('relation')] || e.data('relation')) : '')
    })
  }
}

/* ── 计算属性 ── */
const relationTypes = computed(() => {
  const set = new Set(graphEdges.value.map((e) => e.relation))
  return [...set]
})

const usedNodeTypes = computed(() => {
  const set = new Set(graphNodes.value.map((n) => n.type))
  return [...set]
})

const graphStats = computed(() => `${graphNodes.value.length} 个节点 · ${graphEdges.value.length} 条关系`)

/* ── 属性过滤辅助 ── */
function hasNonDescriptionProps(node) {
  const props = node?.properties || {}
  return Object.keys(props).filter((k) => k !== 'description').length > 0
}

function filteredProps(node) {
  const props = node?.properties || {}
  const result = {}
  for (const [k, v] of Object.entries(props)) {
    if (k !== 'description') result[k] = v
  }
  return result
}

/* ── Cytoscape 初始化 ── */
function toElements(nodes, edges) {
  const nodeElements = nodes.map((n) => {
    const type = n.type || 'Observation'
    return {
      data: {
        id: n.id,
        label: n.name,
        color: NODE_TYPE_COLORS[type] || '#3b82f6',
        nodeType: type,
        size: type === 'SeaArea' ? 70 : 46,
        isCore: type === 'SeaArea',
        raw: n,
      },
    }
  })
  const edgeElements = edges.map((e) => ({
    data: {
      id: e.id,
      source: e.source,
      target: e.target,
      label: settings.value.showEdgeLabels ? (RELATION_LABELS[e.relation] || e.relation) : '',
      relation: e.relation,
      raw: e,
    },
    classes: SOLID_RELATIONS.has(e.relation) ? '' : 'dashed',
  }))
  return [...nodeElements, ...edgeElements]
}

function initCytoscape() {
  if (cy) {
    cy.destroy()
    cy = null
  }

  const elements = toElements(graphNodes.value, graphEdges.value)

  cy = cytoscape({
    container: cyContainerRef.value,
    elements,
    style: [
      /* ── 基础节点样式 ── */
      {
        selector: 'node',
        style: {
          'label': 'data(label)',
          'shape': 'ellipse',
          'width': 'data(size)',
          'height': 'data(size)',
          'background-color': 'data(color)',
          'background-opacity': 0.88,
          'text-valign': 'bottom',
          'text-margin-y': 8,
          'font-size': 11,
          'font-weight': 600,
          'color': '#e2e8f0',
          'border-width': 2.5,
          'border-color': 'data(color)',
          'border-opacity': 0.8,
          'text-outline-width': 2,
          'text-outline-color': '#06192f',
          'text-wrap': 'wrap',
          'text-max-width': '90px',
          'overlay-opacity': 0,
          'transition-property': 'border-width, border-color, background-opacity',
          'transition-duration': '0.2s',
          'shadow-color': 'data(color)',
          'shadow-blur': 8,
          'shadow-opacity': 0.3,
          'shadow-offset-x': 0,
          'shadow-offset-y': 0,
        },
      },
      /* ── 核心节点（SeaArea）：更大 + 强发光 ── */
      {
        selector: 'node[?isCore]',
        style: {
          'width': 80,
          'height': 80,
          'font-size': 14,
          'font-weight': 700,
          'border-width': 3,
          'border-color': '#60a5fa',
          'shadow-blur': 20,
          'shadow-opacity': 0.6,
          'background-opacity': 0.95,
        },
      },
      /* ── 选中节点 ── */
      {
        selector: 'node:selected',
        style: {
          'border-width': 4,
          'border-color': '#fbbf24',
          'background-opacity': 1,
          'overlay-color': '#fbbf24',
          'overlay-padding': 5,
          'overlay-opacity': 0.2,
          'shadow-blur': 24,
          'shadow-opacity': 0.6,
          'shadow-color': '#fbbf24',
        },
      },
      /* ── 暗淡节点 ── */
      {
        selector: 'node.dimmed',
        style: {
          'opacity': 0.15,
        },
      },
      /* ── 边基础样式：直线 ── */
      {
        selector: 'edge',
        style: {
          'width': 1.8,
          'line-color': 'rgba(25, 207, 255, 0.5)',
          'target-arrow-color': 'rgba(25, 207, 255, 0.5)',
          'target-arrow-shape': 'triangle',
          'arrow-scale': 0.8,
          'curve-style': 'straight',
          'label': 'data(label)',
          'font-size': 9,
          'color': 'rgba(180, 210, 240, 0.7)',
          'text-rotation': 'autorotate',
          'text-outline-width': 1.5,
          'text-outline-color': '#06192f',
          'text-margin-y': -6,
          'overlay-opacity': 0,
          'transition-property': 'line-color, opacity',
          'transition-duration': '0.2s',
        },
      },
      /* ── 虚线边 ── */
      {
        selector: 'edge.dashed',
        style: {
          'line-style': 'dashed',
          'line-dash-pattern': [6, 4],
          'line-color': 'rgba(241, 154, 252, 0.5)',
          'target-arrow-color': 'rgba(241, 154, 252, 0.5)',
          'curve-style': 'straight',
        },
      },
      /* ── 暗淡边 ── */
      {
        selector: 'edge.dimmed',
        style: {
          'opacity': 0.1,
        },
      },
    ],
    layout: {
      name: 'cose',
      animate: settings.value.animateLayout,
      animationDuration: 800,
      randomize: true,
      nodeRepulsion: () => 60000,
      idealEdgeLength: () => 180,
      edgeElasticity: () => 80,
      gravity: 0.08,
      numIter: 1200,
      initialTemp: 300,
      coolingFactor: 0.95,
      minTemp: 1.0,
      padding: 60,
    },
    minZoom: 0.2,
    maxZoom: 3,
    wheelSensitivity: 0.3,
    boxSelectionEnabled: false,
  })

  // 布局完成后消除重叠并聚焦中心节点
  // ready 做初步去重；layoutstop 做完整去重 + 聚焦
  cy.ready(() => {
    resolveOverlaps()
  })
  cy.one('layoutstop', () => {
    resolveOverlaps()
    resolveEdgeOverlaps()
    resolveEdgeCrossings()
    // 延迟聚焦，确保节点位置已稳定
    setTimeout(() => focusCenterNode(), 60)
  })

  // 事件绑定
  cy.on('tap', 'node', (evt) => {
    const raw = evt.target.data('raw')
    onNodeClick(raw)
  })

  cy.on('tap', (evt) => {
    if (evt.target === cy) {
      closeDetail()
    }
  })

  // 鼠标样式
  cy.on('mouseover', 'node', () => {
    if (cyContainerRef.value) cyContainerRef.value.style.cursor = 'pointer'
  })
  cy.on('mouseout', 'node', () => {
    if (cyContainerRef.value) cyContainerRef.value.style.cursor = 'default'
  })

  // 拖拽时实时排斥附近节点，防止重叠
  let repelRaf = null
  cy.on('position', 'node', (evt) => {
    const dragged = evt.target
    if (!dragged.grabbed()) return
    if (repelRaf) return
    repelRaf = requestAnimationFrame(() => {
      repelRaf = null
      repelFromNode(dragged)
    })
  })

  // 松手后再做一轮全局消除残余
  cy.on('free', 'node', () => {
    resolveOverlaps()
    resolveEdgeOverlaps()
  })
}

/* ── 拖拽节点排斥周围节点 ── */
function repelFromNode(dragged) {
  if (!cy) return
  const pd = dragged.position()
  const rd = Math.max(dragged.width(), dragged.height()) / 2 + 18

  cy.nodes().forEach((other) => {
    if (other.id() === dragged.id()) return
    const po = other.position()
    let dx = po.x - pd.x
    let dy = po.y - pd.y
    const dist = Math.sqrt(dx * dx + dy * dy) || 1
    const ro = Math.max(other.width(), other.height()) / 2 + 18
    const minDist = rd + ro

    if (dist < minDist) {
      const push = minDist - dist + 2
      const nx = dx / dist
      const ny = dy / dist
      other.position({ x: po.x + nx * push, y: po.y + ny * push })
    }
  })
}

/* ── 消除节点重叠 ── */
function resolveOverlaps() {
  if (!cy) return
  const nodes = cy.nodes()
  const n = nodes.length
  if (n < 2) return

  // 每个节点的有效半径（含标签间距）
  const radiusOf = (node) => {
    const w = node.width()
    const h = node.height()
    return Math.max(w, h) / 2 + 18
  }

  // 迭代推开重叠，最多 80 轮
  for (let round = 0; round < 80; round++) {
    let moved = false
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        const a = nodes[i]
        const b = nodes[j]
        const pa = a.position()
        const pb = b.position()
        let dx = pa.x - pb.x
        let dy = pa.y - pb.y
        const dist = Math.sqrt(dx * dx + dy * dy) || 1
        const minDist = radiusOf(a) + radiusOf(b)
        if (dist < minDist) {
          const overlap = (minDist - dist) / 2 + 1
          const nx = dx / dist
          const ny = dy / dist
          a.position({ x: pa.x + nx * overlap, y: pa.y + ny * overlap })
          b.position({ x: pb.x - nx * overlap, y: pb.y - ny * overlap })
          moved = true
        }
      }
    }
    if (!moved) break
  }
}

/* ── 检测线段是否穿过矩形 ── */
function segmentHitsRect(x1, y1, x2, y2, rx1, ry1, rx2, ry2) {
  // 快速排除
  const minX = Math.min(x1, x2), maxX = Math.max(x1, x2)
  const minY = Math.min(y1, y2), maxY = Math.max(y1, y2)
  if (maxX < rx1 || minX > rx2 || maxY < ry1 || minY > ry2) return false

  const dx = x2 - x1, dy = y2 - y1
  let tmin = 0, tmax = 1

  const update = (p, d, min, max) => {
    if (Math.abs(d) < 1e-10) return p >= min && p <= max
    const t1 = (min - p) / d, t2 = (max - p) / d
    const tl = Math.min(t1, t2), th = Math.max(t1, t2)
    tmin = Math.max(tmin, tl)
    tmax = Math.min(tmax, th)
    return tmin <= tmax
  }

  return update(x1, dx, rx1, rx2) && update(y1, dy, ry1, ry2) && tmin > 0.02 && tmax < 0.98
}

/* ── 消除边与节点的穿越：移动节点来规避 ── */
function resolveEdgeOverlaps() {
  if (!cy) return

  // 多轮迭代，每轮检测所有边并推开冲突节点
  for (let round = 0; round < 20; round++) {
    let fixed = false
    const edges = cy.edges()

    for (let i = 0; i < edges.length; i++) {
      const edge = edges[i]
      const srcId = edge.data('source')
      const tgtId = edge.data('target')
      const srcNode = cy.getElementById(srcId)
      const tgtNode = cy.getElementById(tgtId)
      if (!srcNode.length || !tgtNode.length) continue

      const sp = srcNode.position()
      const tp = tgtNode.position()

      // 检测与哪些非端点节点碰撞
      cy.nodes().forEach((node) => {
        if (node.id() === srcId || node.id() === tgtId) return
        const np = node.position()
        const hw = node.width() / 2 + 14
        const hh = node.height() / 2 + 14

        if (!segmentHitsRect(sp.x, sp.y, tp.x, tp.y, np.x - hw, np.y - hh, np.x + hw, np.y + hh)) return

        fixed = true

        // 计算边的方向向量和法向量
        const edx = tp.x - sp.x, edy = tp.y - sp.y
        const eLen = Math.sqrt(edx * edx + edy * edy) || 1
        // 法向量（垂直于边方向）
        const nx = -edy / eLen, ny = edx / eLen

        // 计算阻挡节点在法向量方向上的偏移量（需要推开多少才能避开）
        // 简化：把阻挡节点沿法向量推离边
        const dot = (np.x - sp.x) * nx + (np.y - sp.y) * ny
        const pushDir = dot >= 0 ? 1 : -1
        const pushDist = Math.max(hw, hh) * 0.4 + 8

        // 把阻挡节点推开
        node.position({
          x: np.x + nx * pushDir * pushDist,
          y: np.y + ny * pushDir * pushDist,
        })
      })
    }
    if (!fixed) break
  }
}

/* ── 消除边-边交叉：移动共享端点附近的节点 ── */
function resolveEdgeCrossings() {
  if (!cy) return
  const edges = cy.edges().toArray()

  function crossProduct(ax, ay, bx, by) { return ax * by - ay * bx }

  function segmentsCross(x1, y1, x2, y2, x3, y3, x4, y4) {
    const d1x = x2 - x1, d1y = y2 - y1
    const d2x = x4 - x3, d2y = y4 - y3
    const denom = crossProduct(d1x, d1y, d2x, d2y)
    if (Math.abs(denom) < 1e-10) return false
    const t = crossProduct(x3 - x1, y3 - y1, d2x, d2y) / denom
    const u = crossProduct(x3 - x1, y3 - y1, d1x, d1y) / denom
    return t > 0.15 && t < 0.85 && u > 0.15 && u < 0.85
  }

  for (let round = 0; round < 10; round++) {
    let fixed = false
    for (let i = 0; i < edges.length; i++) {
      for (let j = i + 1; j < edges.length; j++) {
        const e1 = edges[i], e2 = edges[j]
        const s1 = e1.data('source'), t1 = e1.data('target')
        const s2 = e2.data('source'), t2 = e2.data('target')
        // 跳过共享端点的边
        if (s1 === s2 || s1 === t2 || t1 === s2 || t1 === t2) continue

        const p1 = cy.getElementById(s1).position()
        const p2 = cy.getElementById(t1).position()
        const p3 = cy.getElementById(s2).position()
        const p4 = cy.getElementById(t2).position()
        if (!p1 || !p2 || !p3 || !p4) continue

        if (segmentsCross(p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, p4.x, p4.y)) {
          fixed = true
          // 移动 e1 的 target 节点，沿 e2 法向量偏移
          const dx = p4.x - p3.x, dy = p4.y - p3.y
          const len = Math.sqrt(dx * dx + dy * dy) || 1
          const nx = -dy / len, ny = dx / len
          const node = cy.getElementById(t1)
          const np = node.position()
          node.position({ x: np.x + nx * 20, y: np.y + ny * 20 })
        }
      }
    }
    if (!fixed) break
  }
}

/* ── 聚焦中心节点 ── */
function focusCenterNode() {
  if (!cy || cy.nodes().length === 0) return

  // 优先找 SeaArea 核心节点，否则取第一个
  const coreNode = cy.nodes().filter((n) => n.data('isCore')).first()
  const target = coreNode.length > 0 ? coreNode : cy.nodes().first()
  if (!target || target.length === 0) return

  // 取该节点及其邻居
  const neighborhood = target.neighborhood().add(target)

  // 聚焦局部或全图
  if (neighborhood.length >= 3) {
    cy.fit(neighborhood, 60)
  } else {
    cy.fit(undefined, 40)
  }
}

/* ── 数据加载 ── */
async function loadGraph() {
  loading.value = true
  loadError.value = false
  loadErrorMsg.value = ''

  const result = await fetchGraph()

  if (!result.ok) {
    loading.value = false
    loadError.value = true
    loadErrorMsg.value = result.error || '无法连接到图数据库'
    return
  }

  graphNodes.value = result.data.nodes || []
  graphEdges.value = result.data.edges || []
  loading.value = false

  await nextTick()
  initCytoscape()
}

/* ── 搜索高亮 ── */
watch(searchQuery, (q) => {
  if (!cy) return
  const trimmed = q.trim().toLowerCase()
  if (!trimmed) {
    cy.nodes().removeClass('dimmed')
    cy.edges().removeClass('dimmed')
    return
  }
  const matchIds = new Set(
    graphNodes.value
      .filter((n) => n.name.toLowerCase().includes(trimmed))
      .map((n) => n.id),
  )
  cy.nodes().forEach((n) => {
    n.toggleClass('dimmed', !matchIds.has(n.id()))
  })
  cy.edges().forEach((e) => {
    const src = e.data('source')
    const tgt = e.data('target')
    e.toggleClass('dimmed', !matchIds.has(src) && !matchIds.has(tgt))
  })
})

/* ── 关系筛选 ── */
watch(filterRelation, (val) => {
  if (!cy) return
  cy.edges().forEach((e) => {
    if (val === 'all') {
      e.style('display', 'element')
    } else {
      e.style('display', e.data('relation') === val ? 'element' : 'none')
    }
  })
})

/* ── 交互 ── */
function onNodeClick(node) {
  if (selectedNode.value?.id === node.id) {
    selectedNode.value = null
    expandOptions.value = []
    return
  }
  selectedNode.value = node
  loadExpandOptions(node.id)

  // 高亮选中节点
  if (cy) {
    cy.nodes().unselect()
    const cyNode = cy.getElementById(node.id)
    if (cyNode.length) cyNode.select()
  }
}

async function loadExpandOptions(nodeId) {
  const data = await fetchExpandOptions(nodeId)
  expandOptions.value = data.options || []
}

async function handleExpand(expandType) {
  if (!selectedNode.value || expanding.value) return
  expanding.value = true
  // 找到对应扩展选项的中文标签
  const opt = expandOptions.value.find((o) => o.expand_type === expandType)
  expandingLabel.value = opt?.label || expandType

  const result = await apiExpandNode(selectedNode.value.id, expandType)
  if (result) {
    // 合并新节点到本地数据
    const existingIds = new Set(graphNodes.value.map((n) => n.id))
    const newNodes = (result.new_nodes || []).filter((n) => !existingIds.has(n.id))
    graphNodes.value.push(...newNodes)

    // 合并新边到本地数据
    const existingEdgeIds = new Set(graphEdges.value.map((e) => e.id))
    const newEdges = (result.new_edges || []).filter((e) => !existingEdgeIds.has(e.id))
    graphEdges.value.push(...newEdges)

    // 更新展开状态
    if (result.center_node) {
      const idx = graphNodes.value.findIndex((n) => n.id === result.center_node.id)
      if (idx !== -1) graphNodes.value[idx] = result.center_node
    }

    // 向 Cytoscape 添加新元素并重新布局
    if (cy) {
      const newCyElements = toElements(
        [...newNodes, ...(result.center_node ? [result.center_node] : [])],
        newEdges,
      )
      // 去掉已存在的元素
      const filtered = newCyElements.filter((el) => !cy.getElementById(el.data.id).length)
      if (filtered.length) {
        cy.add(filtered)
      }
      // 更新中心节点数据
      if (result.center_node) {
        const cyNode = cy.getElementById(result.center_node.id)
        if (cyNode.length) {
          cyNode.data('raw', result.center_node)
        }
      }
      // 重新布局
      const expandLayout = cy.layout({
        name: 'cose',
        animate: settings.value.animateLayout,
        animationDuration: 600,
        randomize: false,
        nodeRepulsion: () => 60000,
        idealEdgeLength: () => 180,
        edgeElasticity: () => 80,
        gravity: 0.08,
        numIter: 800,
        initialTemp: 200,
        coolingFactor: 0.95,
        minTemp: 1.0,
        padding: 60,
      })
      expandLayout.one('layoutstop', () => {
        resolveOverlaps()
        resolveEdgeOverlaps()
        resolveEdgeCrossings()
      })
      expandLayout.run()
    }

    // 刷新展开选项
    if (selectedNode.value) {
      loadExpandOptions(selectedNode.value.id)
    }
  }
  expanding.value = false
}

function setTool(index) {
  const mode = tools[index].mode
  if (mode === 'fit') {
    if (cy) cy.fit(undefined, 40)
    return
  }
  if (mode === 'zoomIn') {
    if (cy) cy.zoom({ level: cy.zoom() * 1.25, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } })
    return
  }
  if (mode === 'zoomOut') {
    if (cy) cy.zoom({ level: cy.zoom() * 0.8, renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 } })
    return
  }
  if (mode === 'expand' && selectedNode.value) {
    const first = expandOptions.value.find((o) => !o.expanded)
    if (first) handleExpand(first.expand_type)
    return
  }
  activeTool.value = index

  // 切换拖拽/选择模式
  if (cy) {
    if (mode === 'drag') {
      cy.autoungrabify(false)
    } else {
      cy.autoungrabify(true)
    }
  }
}

function closeDetail() {
  selectedNode.value = null
  expandOptions.value = []
  if (cy) cy.nodes().unselect()
}

/* ── 点击外部关闭设置面板 ── */
function onDocumentClick(e) {
  if (showSettings.value && !e.target.closest('.settings-wrapper')) {
    showSettings.value = false
  }
}

/* ── 生命周期 ── */
onMounted(() => {
  loadGraph()
  document.addEventListener('fullscreenchange', onFullscreenChange)
  document.addEventListener('click', onDocumentClick)
})

onBeforeUnmount(() => {
  if (cy) {
    cy.destroy()
    cy = null
  }
  document.removeEventListener('fullscreenchange', onFullscreenChange)
  document.removeEventListener('click', onDocumentClick)
})

/* ── 导出 ── */
function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

async function exportGraph(format) {
  if (!cy) return
  const ts = new Date().toISOString().slice(0, 10)

  if (format === 'png') {
    const blob = await cy.png({ output: 'blob-promise', full: true, bg: '#06192f', scale: 2 })
    downloadBlob(blob, `ocean-graph-${ts}.png`)
  } else if (format === 'json') {
    const data = {
      nodes: graphNodes.value,
      edges: graphEdges.value,
    }
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    downloadBlob(blob, `ocean-graph-${ts}.json`)
  }
}

defineExpose({ exportGraph })
</script>

<template>
  <section class="panel graph-panel">
    <!-- 头部 -->
    <header class="graph-header">
      <div class="graph-header-top">
        <h2>信息关系图谱</h2>
        <div class="graph-header-right">
          <div class="agent-status-pill">
            <Bot :size="14" />
            <span>多智能体在线</span>
            <i class="agent-dot"></i>
          </div>
          <span v-if="!loadError" class="graph-stats">{{ graphStats }}</span>
        </div>
      </div>
      <div class="graph-controls">
        <div class="graph-search">
          <Search :size="16" />
          <input v-model="searchQuery" placeholder="搜索节点..." :disabled="loadError" />
        </div>
        <select v-model="filterRelation" class="graph-select" :disabled="loadError">
          <option value="all">全部关系</option>
          <option v-for="r in relationTypes" :key="r" :value="r">
            {{ RELATION_LABELS[r] || r }}
          </option>
        </select>
        <div class="graph-actions">
          <button
            aria-label="全屏"
            :title="isFullscreen ? '退出全屏' : '全屏'"
            @click="toggleFullscreen"
          >
            <Minimize v-if="isFullscreen" :size="16" />
            <Maximize v-else :size="16" />
          </button>
          <div class="settings-wrapper">
            <button
              aria-label="设置"
              title="设置"
              :class="{ active: showSettings }"
              @click.stop="showSettings = !showSettings"
            >
              <Settings :size="16" />
            </button>
            <Transition name="dropdown">
              <div v-if="showSettings" class="settings-dropdown">
                <label class="settings-item" @click.stop="toggleSetting('showEdgeLabels')">
                  <span>
                    <Eye v-if="settings.showEdgeLabels" :size="14" />
                    <EyeOff v-else :size="14" />
                    边标签
                  </span>
                  <span class="settings-toggle" :class="{ on: settings.showEdgeLabels }"></span>
                </label>
                <label class="settings-item" @click.stop="toggleSetting('showLegend')">
                  <span>
                    <Eye v-if="settings.showLegend" :size="14" />
                    <EyeOff v-else :size="14" />
                    图例
                  </span>
                  <span class="settings-toggle" :class="{ on: settings.showLegend }"></span>
                </label>
                <label class="settings-item" @click.stop="toggleSetting('animateLayout')">
                  <span>
                    <Eye v-if="settings.animateLayout" :size="14" />
                    <EyeOff v-else :size="14" />
                    布局动画
                  </span>
                  <span class="settings-toggle" :class="{ on: settings.animateLayout }"></span>
                </label>
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </header>

    <!-- 画布 -->
    <div ref="canvasWrapperRef" class="graph-canvas">
      <!-- 工具栏 -->
      <div class="graph-tools">
        <button
          v-for="(tool, index) in tools"
          :key="tool.label"
          :class="{ active: activeTool === index }"
          :title="tool.label"
          :disabled="loadError"
          @click="setTool(index)"
        >
          <component :is="tool.icon" :size="18" />
        </button>
      </div>

      <!-- Cytoscape 容器 -->
      <div ref="cyContainerRef" class="cy-container"></div>

      <!-- 连接失败占位符 -->
      <div v-if="loadError" class="graph-error">
        <div class="graph-error-icon">
          <WifiOff :size="48" />
        </div>
        <div class="graph-error-title">无法连接到图数据库</div>
        <div class="graph-error-desc">{{ loadErrorMsg }}</div>
        <div class="graph-error-hint">
          <Database :size="14" />
          <span>请确认后端服务已启动（默认 http://localhost:8000）</span>
        </div>
        <button class="graph-error-retry" @click="loadGraph">
          <RefreshCw :size="14" />
          重新连接
        </button>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="graph-loading">
        <div class="graph-loading-spinner"></div>
        <span>加载图谱数据...</span>
      </div>

      <!-- 扩展动画覆盖层 -->
      <Transition name="expand-overlay">
        <div v-if="expanding" class="expand-overlay">
          <div class="expand-overlay-content">
            <div class="expand-radar">
              <div class="expand-radar-ring"></div>
              <div class="expand-radar-ring delay-1"></div>
              <div class="expand-radar-ring delay-2"></div>
              <div class="expand-radar-dot"></div>
            </div>
            <div class="expand-text">
              <span class="expand-title">正在调用智能体</span>
              <span class="expand-subtitle">搜寻「{{ expandingLabel }}」相关数据中...</span>
            </div>
            <div class="expand-progress">
              <div class="expand-progress-bar"></div>
            </div>
          </div>
        </div>
      </Transition>

      <!-- 节点详情面板（放在 canvas 内，全屏时可见） -->
      <Transition name="slide">
        <div v-if="selectedNode" class="node-detail" @click.stop>
          <div class="node-detail-header">
            <div>
              <span class="node-detail-type" :class="`tone-${NODE_TYPE_TONES[selectedNode.type] || 'blue'}`">
                {{ NODE_TYPE_LABELS[selectedNode.type] || selectedNode.type }}
              </span>
              <h3>{{ selectedNode.name }}</h3>
            </div>
            <button class="node-detail-close" @click="closeDetail"><X :size="18" /></button>
          </div>

          <div class="node-detail-body">
            <!-- description 独立展示 -->
            <div v-if="selectedNode.properties?.description" class="node-detail-description">
              <div class="desc-bar"></div>
              <p>{{ selectedNode.properties.description }}</p>
            </div>

            <!-- 其他属性（排除 description） -->
            <div v-if="hasNonDescriptionProps(selectedNode)" class="node-detail-section">
              <span class="node-detail-label">属性</span>
              <div class="node-detail-props">
                <div
                  v-for="(val, key) in filteredProps(selectedNode)"
                  :key="key"
                  class="node-detail-prop"
                >
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

      <!-- 图例 -->
      <div v-if="settings.showLegend && !loadError" class="legend">
        <div class="legend-section">
          <span class="legend-title">关系类型</span>
          <span v-for="r in relationTypes" :key="r">
            <i :class="{ dash: !SOLID_RELATIONS.has(r) }"></i>{{ RELATION_LABELS[r] || r }}
          </span>
        </div>
        <div class="legend-section">
          <span class="legend-title">节点类型</span>
          <span v-for="t in usedNodeTypes" :key="t">
            <b :style="{ background: NODE_TYPE_COLORS[t] || '#3b82f6' }"></b>{{ NODE_TYPE_LABELS[t] || t }}
          </span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.cy-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

/* ── 头部两行布局 ── */
.graph-header-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.graph-header-top h2 {
  margin: 0;
}

.graph-header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* ── 多智能体在线胶囊 ── */
.agent-status-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px 4px 10px;
  border-radius: 20px;
  background: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.3);
  color: #4ade80;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  flex-shrink: 0;
}

.agent-status-pill .agent-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 6px rgba(34, 197, 94, 0.6);
  animation: agent-pulse 2s ease-in-out infinite;
  margin-left: 2px;
}

@keyframes agent-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

/* ── 设置面板 ── */
.settings-wrapper {
  position: relative;
}

.settings-wrapper button.active {
  border-color: rgba(83, 171, 255, 0.6);
  color: #fff;
  background: rgba(22, 141, 255, 0.2);
}

.settings-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  width: 180px;
  background: rgba(7, 31, 58, 0.96);
  border: 1px solid rgba(39, 151, 255, 0.28);
  border-radius: 8px;
  padding: 6px;
  z-index: 50;
  backdrop-filter: blur(12px);
}

.settings-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 10px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 12px;
  color: #b9d6ee;
  transition: background 0.15s;
}

.settings-item:hover {
  background: rgba(22, 141, 255, 0.12);
  color: #fff;
}

.settings-item span:first-child {
  display: flex;
  align-items: center;
  gap: 8px;
}

.settings-toggle {
  width: 32px;
  height: 18px;
  border-radius: 9px;
  background: rgba(75, 143, 210, 0.3);
  position: relative;
  transition: background 0.2s;
  flex-shrink: 0;
}

.settings-toggle::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #8fb9df;
  transition: all 0.2s;
}

.settings-toggle.on {
  background: rgba(34, 197, 94, 0.5);
}

.settings-toggle.on::after {
  left: 17px;
  background: #22c55e;
}

/* ── 设置面板动画 ── */
.dropdown-enter-active {
  animation: dropdown-in 0.15s ease-out;
}

.dropdown-leave-active {
  animation: dropdown-in 0.1s ease-in reverse;
}

@keyframes dropdown-in {
  from {
    opacity: 0;
    transform: translateY(-6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* ── 连接错误占位符 ── */
.graph-error {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  z-index: 10;
  color: #8fb9df;
}

.graph-error-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: rgba(244, 63, 94, 0.08);
  border: 1px solid rgba(244, 63, 94, 0.25);
  display: grid;
  place-items: center;
  color: #f43f5e;
  margin-bottom: 4px;
}

.graph-error-title {
  font-size: 18px;
  font-weight: 600;
  color: #e2e8f0;
}

.graph-error-desc {
  font-size: 13px;
  color: #6b8aab;
  max-width: 400px;
  text-align: center;
  line-height: 1.5;
}

.graph-error-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #4a7a9e;
  padding: 8px 14px;
  background: rgba(14, 51, 86, 0.3);
  border-radius: 6px;
  border: 1px solid rgba(39, 151, 255, 0.1);
}

.graph-error-retry {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
  padding: 10px 24px;
  border: 1px solid rgba(39, 151, 255, 0.4);
  border-radius: 8px;
  background: rgba(22, 141, 255, 0.15);
  color: #60a5fa;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.graph-error-retry:hover {
  background: rgba(22, 141, 255, 0.3);
  border-color: rgba(39, 151, 255, 0.6);
  color: #93c5fd;
}

/* ── 扩展动画覆盖层 ── */
.expand-overlay {
  position: absolute;
  inset: 0;
  z-index: 30;
  display: grid;
  place-items: center;
  background: rgba(4, 14, 30, 0.88);
  backdrop-filter: blur(6px);
}

.expand-overlay-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 28px;
}

/* 雷达扫描动画 */
.expand-radar {
  position: relative;
  width: 120px;
  height: 120px;
}

.expand-radar-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid rgba(34, 197, 94, 0.5);
  animation: radar-ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;
}

.expand-radar-ring.delay-1 {
  animation-delay: 0.5s;
}

.expand-radar-ring.delay-2 {
  animation-delay: 1s;
}

.expand-radar-dot {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 14px;
  height: 14px;
  margin: -7px 0 0 -7px;
  border-radius: 50%;
  background: #22c55e;
  box-shadow: 0 0 20px #22c55e, 0 0 40px rgba(34, 197, 94, 0.4);
  animation: radar-dot 2s linear infinite;
}

@keyframes radar-ping {
  0% {
    transform: scale(0.2);
    opacity: 1;
  }
  100% {
    transform: scale(1.2);
    opacity: 0;
  }
}

@keyframes radar-dot {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.3); opacity: 0.7; }
  100% { transform: scale(1); opacity: 1; }
}

/* 文字 */
.expand-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.expand-title {
  font-size: 20px;
  font-weight: 700;
  color: #e2e8f0;
  letter-spacing: 0.04em;
}

.expand-subtitle {
  font-size: 14px;
  color: #60a5fa;
  animation: text-pulse 1.5s ease-in-out infinite;
}

@keyframes text-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* 进度条 */
.expand-progress {
  width: 240px;
  height: 3px;
  border-radius: 2px;
  background: rgba(75, 143, 210, 0.2);
  overflow: hidden;
}

.expand-progress-bar {
  height: 100%;
  border-radius: 2px;
  background: linear-gradient(90deg, #22c55e, #3b82f6);
  animation: progress-slide 2s ease-in-out infinite;
}

@keyframes progress-slide {
  0% { width: 0%; margin-left: 0; }
  50% { width: 60%; margin-left: 20%; }
  100% { width: 0%; margin-left: 100%; }
}

/* 过渡动画 */
.expand-overlay-enter-active {
  animation: overlay-in 0.3s ease-out;
}

.expand-overlay-leave-active {
  animation: overlay-in 0.25s ease-in reverse;
}

@keyframes overlay-in {
  from {
    opacity: 0;
    backdrop-filter: blur(0);
  }
  to {
    opacity: 1;
    backdrop-filter: blur(6px);
  }
}
</style>
