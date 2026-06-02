<script setup>
import { Anchor, Fish, GitFork, MessageSquare, Network, RadioTower, SearchCheck } from 'lucide-vue-next'

const navItems = [
  { label: '智能体检索', icon: SearchCheck, page: 'agents' },
  { label: '关系图谱', icon: GitFork, page: 'graph' },
  { label: '生态问答', icon: MessageSquare, page: 'qa' },
  { label: '渔场评估', icon: Fish, page: 'fishery' },
  { label: '航线优化', icon: Anchor, page: 'route' },
  { label: '浮标诊断', icon: RadioTower, page: 'buoy' },
]

defineProps({
  activePage: { type: String, required: true },
})

const emit = defineEmits(['change-page'])
</script>

<template>
  <aside class="sidebar">
    <div class="brand">
      <div class="logo"><Network :size="30" /></div>
      <div>
        <strong>海洋智能体平台</strong>
        <span>Ocean Agent Intelligence Platform</span>
      </div>
    </div>
    <nav>
      <button
        v-for="item in navItems"
        :key="item.label"
        :class="{ active: item.page === activePage }"
        :disabled="!item.page"
        @click="item.page && emit('change-page', item.page)"
      >
        <component :is="item.icon" :size="23" />
        <span>{{ item.label }}</span>
      </button>
    </nav>
    <div class="radar-art">
      <div class="radar-rings"></div>
      <div class="ship">△</div>
    </div>
    <button class="collapse-button">收起菜单</button>
  </aside>
</template>
