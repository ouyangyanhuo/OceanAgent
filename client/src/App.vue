<script setup>
import { onMounted, ref } from 'vue'
import { Bell, CircleHelp, Plus, Search } from 'lucide-vue-next'
import SidebarNav from './components/SidebarNav.vue'
import MetricCard from './components/MetricCard.vue'
import AgentCard from './components/AgentCard.vue'
import TaskFeed from './components/TaskFeed.vue'
import DataSources from './components/DataSources.vue'
import KnowledgeGraph from './components/KnowledgeGraph.vue'
import { fallbackDashboard, fetchDashboard } from './services/dashboard'

const dashboard = ref(fallbackDashboard)

onMounted(async () => {
  dashboard.value = await fetchDashboard()
})
</script>

<template>
  <div class="app-shell">
    <SidebarNav />
    <main class="workspace">
      <header class="topbar">
        <div class="brand-inline">
          <div class="brand-mark">≈</div>
          <div>
            <strong>海洋智能体平台</strong>
            <span>Ocean Agent Intelligence Platform</span>
          </div>
        </div>
        <label class="global-search">
          <Search :size="22" />
          <input placeholder="搜索智能体 / 数据源 / 关系节点" />
        </label>
        <div class="top-actions">
          <button class="icon-button alert" aria-label="通知"><Bell :size="22" /><span>12</span></button>
          <button class="icon-button" aria-label="帮助"><CircleHelp :size="22" /></button>
          <div class="user-chip">
            <div class="avatar"></div>
            <span>海洋探索者</span>
          </div>
          <button class="primary-action">新建任务 <Plus :size="18" /></button>
        </div>
      </header>

      <section class="content-grid">
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

      <footer class="statusbar">
        <span>系统状态 <b class="dot"></b> 运行正常</span>
        <span>数据更新 <strong>2 分钟前</strong></span>
        <span>服务负载 <i><em style="width:42%"></em></i> 42%</span>
        <span>存储使用 <i><em style="width:68%"></em></i> 68%</span>
        <span>当前时间 <strong>2025-05-24&nbsp;&nbsp;10:30:45</strong></span>
      </footer>
    </main>
  </div>
</template>
