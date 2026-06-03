<script setup>
import { Anchor, Fish, GitFork, MessageSquare, PanelLeftClose, PanelLeftOpen, RadioTower, SearchCheck } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import gsap from 'gsap'

const route = useRoute()
const isCollapsed = ref(false)
const navRef = ref(null)

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

onMounted(() => {
  if (!navRef.value) return
  gsap.from(navRef.value.querySelectorAll('a'), {
    x: -16,
    opacity: 0,
    duration: 0.4,
    stagger: 0.05,
    ease: 'power3.out',
    delay: 0.1,
  })
})
</script>

<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <nav ref="navRef">
      <router-link
        v-for="item in navItems"
        :key="item.label"
        :to="item.to"
        :class="{ active: route.path === item.to }"
        :title="isCollapsed ? item.label : ''"
      >
        <component :is="item.icon" :size="20" />
        <span v-if="!isCollapsed">{{ item.label }}</span>
        <div v-if="route.path === item.to" class="active-indicator"></div>
      </router-link>
    </nav>
    <div v-if="!isCollapsed" class="radar-art">
      <div class="radar-rings"></div>
      <div class="ship">△</div>
    </div>
    <button class="toggle-btn" @click="toggleSidebar" :title="isCollapsed ? '展开菜单' : '收起菜单'">
      <component :is="isCollapsed ? PanelLeftOpen : PanelLeftClose" :size="18" />
    </button>
  </aside>
</template>
