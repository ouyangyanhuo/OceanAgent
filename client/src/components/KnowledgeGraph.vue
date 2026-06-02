<script setup>
import { computed } from 'vue'
import { Expand, Maximize, MousePointer2, Move, Search, Settings, ZoomIn, ZoomOut } from 'lucide-vue-next'

const props = defineProps({
  graph: { type: Object, required: true },
})

const tools = [MousePointer2, Move, ZoomIn, ZoomOut, Maximize, Expand]

const allNodes = computed(() => [props.graph.center, ...props.graph.nodes])
const nodeMap = computed(() => Object.fromEntries(allNodes.value.map((node) => [node.id, node])))

const edges = computed(() =>
  props.graph.edges.map((edge) => ({
    ...edge,
    sourceNode: nodeMap.value[edge.source],
    targetNode: nodeMap.value[edge.target],
  })),
)
</script>

<template>
  <section class="panel graph-panel">
    <header class="graph-header">
      <h2>信息关系图谱</h2>
      <div class="graph-controls">
        <select><option>全部关系</option></select>
        <label><Search :size="17" /><input placeholder="搜索节点" /></label>
        <button aria-label="全屏"><Maximize :size="17" /></button>
        <button aria-label="关系"><Expand :size="17" /></button>
        <button aria-label="设置"><Settings :size="17" /></button>
      </div>
    </header>
    <div class="graph-canvas">
      <div class="graph-tools">
        <button v-for="tool in tools" :key="tool.name"><component :is="tool" :size="20" /></button>
      </div>
      <svg class="edge-layer" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
        <defs>
          <filter id="edgeGlow"><feGaussianBlur stdDeviation="0.6" result="blur" /><feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
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
        <span v-for="node in allNodes" :key="`mini-${node.id}`" :style="{ left: `${node.x}%`, top: `${node.y}%` }"></span>
      </div>
      <div class="legend">
        <span><i class="solid"></i>因果关系</span>
        <span><i class="dash"></i>相关关系</span>
        <span><b class="blue"></b>物理要素</span>
        <span><b class="green"></b>观测设备</span>
        <span><b class="rose"></b>现象事件</span>
        <span><b class="amber"></b>人类活动</span>
        <span><b class="violet"></b>行业领域</span>
      </div>
    </div>
  </section>
</template>
