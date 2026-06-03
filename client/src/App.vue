<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bell, CircleHelp, FileText, Plus, Search, Sparkles } from 'lucide-vue-next'
import SidebarNav from './components/SidebarNav.vue'
import StatusBar from './components/StatusBar.vue'
import { useDashboardStore } from './stores/dashboard'

const dashboard = useDashboardStore()
const searchQuery = ref('')
const showDropdown = ref(false)

const router = useRouter()
const route = useRoute()

const pages = [
  { label: '智能体检索', page: 'agents' },
  { label: '关系图谱', page: 'graph' },
  { label: '生态问答', page: 'qa' },
  { label: '渔场评估', page: 'fishery' },
  { label: '航线优化', page: 'route' },
  { label: '浮标诊断', page: 'buoy' },
]

const pageRouteMap = {
  agents: '/agents',
  graph: '/graph',
  qa: '/qa',
  fishery: '/fishery',
  route: '/route',
  buoy: '/buoy',
}

const searchResults = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return { pages: [], agents: [] }

  const matchedPages = pages.filter(p =>
    p.label.toLowerCase().includes(q)
  )

  const matchedAgents = dashboard.data.agents.filter(a =>
    a.name.toLowerCase().includes(q)
    || a.description.toLowerCase().includes(q)
    || a.tags.some(t => t.toLowerCase().includes(q))
  )

  return { pages: matchedPages, agents: matchedAgents }
})

const hasResults = computed(() =>
  searchResults.value.pages.length > 0 || searchResults.value.agents.length > 0
)

function selectPage(page) {
  router.push(pageRouteMap[page])
  searchQuery.value = ''
  showDropdown.value = false
}

function selectAgent() {
  router.push('/agents')
  searchQuery.value = ''
  showDropdown.value = false
}

function onSearchBlur() {
  setTimeout(() => { showDropdown.value = false }, 150)
}

const searchPlaceholder = computed(() => {
  const path = route.path
  return '搜索页面 / 知识 /智能体'
})

onMounted(() => {
  dashboard.fetch()
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
      <div class="global-search-wrapper">
        <label class="global-search">
          <Search :size="22" />
          <input
            v-model="searchQuery"
            :placeholder="searchPlaceholder"
            @focus="showDropdown = true"
            @blur="onSearchBlur"
          />
        </label>
        <div v-if="showDropdown && searchQuery.trim() && hasResults" class="search-dropdown">
          <div v-if="searchResults.pages.length" class="search-group">
            <div class="search-group-label">页面</div>
            <button
              v-for="p in searchResults.pages"
              :key="p.page"
              class="search-item"
              @mousedown.prevent="selectPage(p.page)"
            >
              <FileText :size="16" />
              <span>{{ p.label }}</span>
            </button>
          </div>
          <div v-if="searchResults.agents.length" class="search-group">
            <div class="search-group-label">智能体</div>
            <button
              v-for="a in searchResults.agents"
              :key="a.name"
              class="search-item"
              @mousedown.prevent="selectAgent()"
            >
              <Sparkles :size="16" />
              <div class="search-item-text">
                <span>{{ a.name }}</span>
                <small>{{ a.description }}</small>
              </div>
            </button>
          </div>
        </div>
        <div v-else-if="showDropdown && searchQuery.trim() && !hasResults" class="search-dropdown">
          <div class="search-empty">无匹配结果</div>
        </div>
      </div>
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
      <SidebarNav />
      <main class="workspace min-w-0">
        <router-view />

        <StatusBar />
      </main>
    </div>
  </div>
</template>

<style scoped>
.global-search-wrapper {
  position: relative;
}

.global-search-wrapper .global-search {
  width: 100%;
}

.search-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: rgba(4, 17, 35, 0.98);
  border: 1px solid rgba(35, 137, 255, 0.3);
  border-radius: 10px;
  padding: 6px;
  z-index: 100;
  max-height: 360px;
  overflow-y: auto;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
}

.search-group {
  margin-bottom: 4px;
}

.search-group:last-child {
  margin-bottom: 0;
}

.search-group-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: rgba(158, 200, 231, 0.5);
  padding: 6px 10px 2px;
}

.search-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 8px 10px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  color: #dff7ff;
  font-size: 14px;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s;
}

.search-item:hover {
  background: rgba(35, 137, 255, 0.12);
}

.search-item svg {
  flex-shrink: 0;
  color: rgba(158, 200, 231, 0.6);
}

.search-item-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.search-item-text span {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.search-item-text small {
  font-size: 12px;
  color: rgba(158, 200, 231, 0.45);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.search-empty {
  padding: 16px;
  text-align: center;
  color: rgba(158, 200, 231, 0.4);
  font-size: 13px;
}
</style>
