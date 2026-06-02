<script setup>
import DataSources from './DataSources.vue'
import KnowledgeGraph from './KnowledgeGraph.vue'
import MetricCard from './MetricCard.vue'
import TaskFeed from './TaskFeed.vue'

defineProps({
  dashboard: { type: Object, required: true },
})
</script>

<template>
  <section class="page graph-page">
    <div class="graph-page-header">
      <div class="graph-page-title">
        <h1>关系图谱</h1>
        <p>海洋环境事件与各要素之间的关联关系可视化</p>
      </div>
      <div class="graph-page-actions">
        <button class="btn-secondary">导出图谱</button>
        <button class="btn-primary">新建节点</button>
      </div>
    </div>
    <div class="metrics-grid graph-metrics">
      <MetricCard v-for="metric in dashboard.metrics" :key="metric.label" :metric="metric" />
    </div>
    <div class="graph-page-grid">
      <KnowledgeGraph :graph="dashboard.graph" />
      <aside class="graph-aside">
        <TaskFeed :tasks="dashboard.tasks" />
        <DataSources :sources="dashboard.sources" />
      </aside>
    </div>
  </section>
</template>
