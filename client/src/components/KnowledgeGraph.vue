<script setup>
import { computed, ref } from 'vue'
import { Expand, Maximize, MousePointer2, Move, Search, Settings, ZoomIn, ZoomOut } from 'lucide-vue-next'

const props = defineProps({
  graph: { type: Object, required: true },
})

const tools = [
  { icon: MousePointer2, label: '选择' },
  { icon: Move, label: '拖拽' },
  { icon: ZoomIn, label: '放大' },
  { icon: ZoomOut, label: '缩小' },
  { icon: Maximize, label: '适应画布' },
  { icon: Expand, label: '展开' },
]

const activeTool = ref(0)

const allNodes = computed(() => [props.graph.center, ...props.graph.nodes])
const nodeMap = computed(() => Object.fromEntries(allNodes.value.map((node) => [node.id, node])))

const edges = computed(() =>
  props.graph.edges.map((edge) => ({
    ...edge,
    sourceNode: nodeMap.value[edge.source],
    targetNode: nodeMap.value[edge.target],
  })),
)

function setTool(index) {
  activeTool.value = index
}
</script>

<template>
  <section class="panel graph-panel">
    <header class="graph-header">
      <div class="graph-header-left">
        <h2>信息关系图谱</h2>
        <span class="graph-stats">{{ allNodes.length }} 个节点 · {{ edges.length }} 条关系</span>
      </div>
      <div class="graph-controls">
        <div class="graph-search">
          <Search :size="16" />
          <input placeholder="搜索节点..." />
        </div>
        <select class="graph-select">
          <option>全部关系</option>
          <option>因果关系</option>
          <option>相关关系</option>
        </select>
        <div class="graph-actions">
          <button aria-label="全屏" title="全屏"><Maximize :size="16" /></button>
          <button aria-label="展开" title="展开图谱"><Expand :size="16" /></button>
          <button aria-label="设置" title="设置"><Settings :size="16" /></button>
        </div>
      </div>
    </header>
    <div class="graph-canvas">
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
      <svg class="edge-layer" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
        <defs>
          <filter id="edgeGlow">
            <feGaussianBlur stdDeviation="0.6" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <line
          v-for="edge in edges"
          :key="`${edge.source}-${edge.target}`"
          :x1="edge.sourceNode.x"
          :y1="edge.sourceNode.y"
          :x2="edge.targetNode.x"
          :y2="edge.targetNode.y"
          :class="{ dashed: edge.kind === '相关关系' }"
          filter="url(#edgeGlow)"
        />
      </svg>
      <div
        v-for="node in allNodes"
        :key="node.id"
        class="graph-node"
        :class="[`tone-${node.tone}`, { core: node.id === 'event' }]"
        :style="{ left: `${node.x}%`, top: `${node.y}%` }"
      >
        <span>{{ node.label }}</span>
      </div>
      <div class="mini-map">
        <div class="mini-map-header">
          <span>缩略图</span>
        </div>
        <div class="mini-map-content">
          <span
            v-for="node in allNodes"
            :key="`mini-${node.id}`"
            :style="{ left: `${node.x}%`, top: `${node.y}%` }"
          ></span>
        </div>
      </div>
      <div class="legend">
        <div class="legend-section">
          <span class="legend-title">关系类型</span>
          <span><i class="solid"></i>因果关系</span>
          <span><i class="dash"></i>相关关系</span>
        </div>
        <div class="legend-section">
          <span class="legend-title">节点类型</span>
          <span><b class="blue"></b>物理要素</span>
          <span><b class="green"></b>观测设备</span>
          <span><b class="rose"></b>现象事件</span>
          <span><b class="amber"></b>人类活动</span>
          <span><b class="violet"></b>行业领域</span>
        </div>
      </div>
    </div>
  </section>
</template>
