<script setup>
import { onMounted, ref } from 'vue'
import gsap from 'gsap'
import { Bot, Search } from 'lucide-vue-next'
import AgentCard from '../components/AgentCard.vue'
import DataSources from '../components/DataSources.vue'
import MetricCard from '../components/MetricCard.vue'
import TaskFeed from '../components/TaskFeed.vue'
import { useDashboardStore } from '../stores/dashboard'

const dashboard = useDashboardStore()

const toasts = ref([])
let toastId = 0
const pageRef = ref(null)

function handleInvoke(agent) {
  const id = ++toastId
  toasts.value.push({ id, name: agent.name })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 3000)
}

onMounted(() => {
  if (!pageRef.value) return

  const ctx = gsap.context(() => {
    // Metrics stagger
    gsap.from('.agent-search-metrics .metric-card', {
      y: 20,
      opacity: 0,
      duration: 0.6,
      stagger: 0.08,
      ease: 'power3.out',
    })

    // Page hero
    gsap.from('.page-hero', {
      y: 16,
      opacity: 0,
      duration: 0.5,
      ease: 'power3.out',
      delay: 0.2,
    })

    // Agent cards stagger
    gsap.from('.agent-grid .agent-card', {
      y: 24,
      opacity: 0,
      duration: 0.6,
      stagger: 0.1,
      ease: 'power3.out',
      delay: 0.35,
    })

    // Sidebar panels
    gsap.from('.agent-search-aside > *', {
      y: 20,
      opacity: 0,
      duration: 0.5,
      stagger: 0.1,
      ease: 'power3.out',
      delay: 0.5,
    })
  }, pageRef.value)

  return () => ctx.revert()
})
</script>

<template>
  <section ref="pageRef" class="page agent-search-page min-w-0">
    <!-- Metrics -->
    <div class="metrics-grid agent-search-metrics min-w-0">
      <MetricCard v-for="metric in dashboard.data.metrics" :key="metric.label" :metric="metric" />
    </div>

    <!-- Main layout -->
    <div class="agent-search-layout min-w-0">
      <div class="agent-search-main min-w-0">
        <!-- Page hero -->
        <div class="page-hero">
          <div class="page-hero-icon"><Search :size="28" /></div>
          <div class="page-hero-text">
            <h1>智能体检索</h1>
            <p>检索并调用海洋智能体，执行监测、分析、预测等任务</p>
          </div>
          <div class="page-hero-meta">
            <span class="meta-badge"><Bot :size="14" /> {{ dashboard.data.agents.length }} 个智能体</span>
          </div>
        </div>

        <!-- Agent grid -->
        <section class="panel agent-search-panel">
          <div class="agent-grid expanded">
            <AgentCard v-for="agent in dashboard.data.agents" :key="agent.name" :agent="agent" @invoke="handleInvoke" />
          </div>
        </section>
      </div>

      <!-- Sidebar -->
      <aside class="agent-search-aside min-w-0">
        <TaskFeed :tasks="dashboard.data.tasks" />
        <DataSources :sources="dashboard.data.sources" />
      </aside>
    </div>

    <!-- Toast -->
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div v-for="toast in toasts" :key="toast.id" class="toast">
          ✓ 已成功调用「{{ toast.name }}」
        </div>
      </TransitionGroup>
    </div>
  </section>
</template>
