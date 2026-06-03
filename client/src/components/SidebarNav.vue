<script setup>
import { Anchor, Fish, GitFork, MessageSquare, PanelLeftClose, PanelLeftOpen, RadioTower, SearchCheck } from 'lucide-vue-next'
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const isCollapsed = ref(false)

const navItems = [
  { label: '智能体检索', icon: SearchCheck, to: '/agents' },
  { label: '关系图谱', icon: GitFork, to: '/graph' },
  { label: '生态问答', icon: MessageSquare, to: '/qa' },
  { label: '渔场评估', icon: Fish, to: '/fishery' },
  { label: '航线优化', icon: Anchor, to: '/route' },
  { label: '浮标诊断', icon: RadioTower, to: '/buoy' },
]

function toggleSidebar() {
  isCollapsed.value = !isCollapsed.value
}
</script>

<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <nav>
      <router-link
        v-for="item in navItems"
        :key="item.label"
        :to="item.to"
        :class="{ active: route.path === item.to }"
        :title="isCollapsed ? item.label : ''"
      >
        <component :is="item.icon" :size="23" />
        <span v-if="!isCollapsed">{{ item.label }}</span>
      </router-link>
    </nav>
    <div v-if="!isCollapsed" class="radar-art">
      <div class="radar-rings"></div>
      <div class="ship">△</div>
    </div>
    <button class="toggle-btn" @click="toggleSidebar" :title="isCollapsed ? '展开菜单' : '收起菜单'">
      <component :is="isCollapsed ? PanelLeftOpen : PanelLeftClose" :size="20" />
    </button>
  </aside>
</template>
