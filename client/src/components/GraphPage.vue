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
  <section class="page graph-page min-w-0">
    <div class="metrics-grid graph-metrics min-w-0">
      <MetricCard v-for="metric in dashboard.metrics" :key="metric.label" :metric="metric" />
    </div>
    <div class="graph-page-grid min-w-0">
      <KnowledgeGraph :graph="dashboard.graph" />
      <aside class="graph-aside min-w-0">
        <TaskFeed :tasks="dashboard.tasks" />
        <DataSources :sources="dashboard.sources" />
      </aside>
    </div>
  </section>
</template>
