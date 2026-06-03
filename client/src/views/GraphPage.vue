<script setup>
import { inject } from 'vue'
import { Network } from 'lucide-vue-next'
import DataSources from '../components/DataSources.vue'
import KnowledgeGraph from '../components/KnowledgeGraph.vue'
import MetricCard from '../components/MetricCard.vue'
import TaskFeed from '../components/TaskFeed.vue'

const dashboard = inject('dashboard')
</script>

<template>
  <section class="page graph-page">
    <div class="qa-hero graph-hero min-w-0">
      <div class="agent-orb graph-orb"><Network :size="34" /></div>
      <div>
        <h1>关系图谱</h1>
        <p>海洋环境事件与各要素之间的关联关系可视化</p>
      </div>
      <div class="page-actions">
        <button class="btn-secondary">导出图谱</button>
        <button class="btn-primary">新建节点</button>
      </div>
    </div>
    <div class="metrics-grid graph-metrics">
      <MetricCard v-for="metric in dashboard.metrics" :key="metric.label" :metric="metric" />
    </div>
    <div class="graph-page-grid">
      <KnowledgeGraph />
      <aside class="graph-aside">
        <TaskFeed :tasks="dashboard.tasks" />
        <DataSources :sources="dashboard.sources" />
      </aside>
    </div>
  </section>
</template>
