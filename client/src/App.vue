<script setup>
import { computed, onMounted, ref } from 'vue'
import { Bell, CircleHelp, Plus, Search } from 'lucide-vue-next'
import SidebarNav from './components/SidebarNav.vue'
import AgentSearchPage from './components/AgentSearchPage.vue'
import BuoyDiagnosticsPage from './components/BuoyDiagnosticsPage.vue'
import EcoQaPage from './components/EcoQaPage.vue'
import FisheryAssessmentPage from './components/FisheryAssessmentPage.vue'
import GraphPage from './components/GraphPage.vue'
import RouteOptimizationPage from './components/RouteOptimizationPage.vue'
import { fallbackDashboard, fetchDashboard } from './services/dashboard'

const dashboard = ref(fallbackDashboard)
const activePage = ref('agents')

const searchPlaceholder = computed(() => {
  if (activePage.value === 'qa') return '搜索生态知识 / 数据源 / 关系节点'
  if (activePage.value === 'fishery') return '搜索渔场 / 鱼种 / 评估指标'
  if (activePage.value === 'route') return '搜索航线 / 港口 / 气象海况'
  if (activePage.value === 'buoy') return '搜索浮标 / 传感器 / 异常记录'
  if (activePage.value === 'graph') return '搜索关系节点 / 数据源 / 图谱实体'
  return '搜索智能体 / 数据源 / 关系节点'
})

onMounted(async () => {
  dashboard.value = await fetchDashboard()
})
</script>

<template>
  <div class="app-shell min-h-dvh" data-theme="dark">
    <!-- Topbar: 横跨整个顶部 -->
    <header class="topbar">
      <div class="brand">
        <div class="logo">≈</div>
        <div class="brand-text">
          <strong>海洋智能体平台</strong>
          <span>Ocean Agent Intelligence Platform</span>
        </div>
      </div>
      <label class="global-search">
        <Search :size="22" />
        <input :placeholder="searchPlaceholder" />
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

    <!-- 下面是 sidebar + 内容区 -->
    <div class="main-layout">
      <SidebarNav :active-page="activePage" @change-page="activePage = $event" />
      <main class="workspace min-w-0">
        <AgentSearchPage v-if="activePage === 'agents'" :dashboard="dashboard" />
        <GraphPage v-else-if="activePage === 'graph'" :dashboard="dashboard" />
        <EcoQaPage v-else-if="activePage === 'qa'" />
        <FisheryAssessmentPage v-else-if="activePage === 'fishery'" />
        <RouteOptimizationPage v-else-if="activePage === 'route'" />
        <BuoyDiagnosticsPage v-else-if="activePage === 'buoy'" />

        <footer class="statusbar">
          <span>系统状态 <b class="dot"></b> 运行正常</span>
          <span>数据更新 <strong>2 分钟前</strong></span>
          <span>服务负载 <i><em style="width:42%"></em></i> 42%</span>
          <span>存储使用 <i><em style="width:68%"></em></i> 68%</span>
          <span>当前时间 <strong>2025-05-24&nbsp;&nbsp;10:30:45</strong></span>
        </footer>
      </main>
    </div>
  </div>
</template>
