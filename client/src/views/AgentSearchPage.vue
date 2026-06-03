<script setup>
import { ref } from 'vue'
import AgentCard from '../components/AgentCard.vue'
import DataSources from '../components/DataSources.vue'
import MetricCard from '../components/MetricCard.vue'
import TaskFeed from '../components/TaskFeed.vue'
import { useDashboardStore } from '../stores/dashboard'

const dashboard = useDashboardStore()

const toasts = ref([])
let toastId = 0

function handleInvoke(agent) {
  const id = ++toastId
  toasts.value.push({ id, name: agent.name })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 3000)
}
</script>

<template>
  <section class="page agent-search-page min-w-0">
    <div class="metrics-grid agent-search-metrics min-w-0">
      <MetricCard v-for="metric in dashboard.data.metrics" :key="metric.label" :metric="metric" />
    </div>

    <div class="agent-search-layout min-w-0">
      <div class="agent-search-main min-w-0">
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
          <div class="agent-grid expanded">
            <AgentCard v-for="agent in dashboard.data.agents" :key="agent.name" :agent="agent" @invoke="handleInvoke" />
          </div>
        </section>
      </div>

      <aside class="agent-search-aside min-w-0">
        <TaskFeed :tasks="dashboard.data.tasks" />
        <DataSources :sources="dashboard.data.sources" />
      </aside>
    </div>

    <!-- Toast 提示 -->
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div v-for="toast in toasts" :key="toast.id" class="toast">
          ✓ 已成功调用「{{ toast.name }}」
        </div>
      </TransitionGroup>
    </div>
  </section>
</template>
