<script setup>
import AgentCard from './AgentCard.vue'
import DataSources from './DataSources.vue'
import KnowledgeGraph from './KnowledgeGraph.vue'
import MetricCard from './MetricCard.vue'
import TaskFeed from './TaskFeed.vue'

defineProps({
  dashboard: { type: Object, required: true },
})
</script>

<template>
  <section class="content-grid dashboard-grid">
    <div class="left-stack">
      <section class="panel agent-search-panel">
        <div class="section-heading">
          <div>
            <span class="heading-icon">▣</span>
            <h1>智能体检索</h1>
          </div>
        </div>
        <div class="filters">
          <button class="filter active">全部</button>
          <button class="filter">海洋监测</button>
          <button class="filter">生态分析</button>
          <button class="filter">航运预测</button>
          <button class="filter">灾害预警</button>
          <button class="filter">设备巡检</button>
        </div>
        <div class="toolbar-row">
          <div class="view-toggle"><button class="active">▦</button><button>☰</button></div>
          <select aria-label="排序">
            <option>综合排序</option>
          </select>
        </div>
        <div class="agent-grid">
          <AgentCard v-for="agent in dashboard.agents" :key="agent.name" :agent="agent" />
        </div>
        <div class="pager">
          <button>‹</button><button>‹</button><button class="active">1</button><button>2</button><button>3</button><button>4</button><button>5</button><span>...</span><button>12</button><button>›</button>
          <span class="total">共 72 项</span>
        </div>
      </section>

      <div class="bottom-panels">
        <TaskFeed :tasks="dashboard.tasks" />
        <DataSources :sources="dashboard.sources" />
      </div>
    </div>

    <div class="right-stack">
      <div class="metrics-grid">
        <MetricCard v-for="metric in dashboard.metrics" :key="metric.label" :metric="metric" />
      </div>
      <KnowledgeGraph :graph="dashboard.graph" />
    </div>
  </section>
</template>
