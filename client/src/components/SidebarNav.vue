<script setup>
import { Anchor, Fish, GitFork, MessageSquare, PanelLeftClose, PanelLeftOpen, RadioTower, SearchCheck } from 'lucide-vue-next'
import { ref } from 'vue'

const props = defineProps({
  activePage: { type: String, required: true },
})

const emit = defineEmits(['change-page'])

const isCollapsed = ref(false)

const navItems = [
  { label: '智能体检索', icon: SearchCheck, page: 'agents' },
  { label: '关系图谱', icon: GitFork, page: 'graph' },
  { label: '生态问答', icon: MessageSquare, page: 'qa' },
  { label: '渔场评估', icon: Fish, page: 'fishery' },
  { label: '航线优化', icon: Anchor, page: 'route' },
  { label: '浮标诊断', icon: RadioTower, page: 'buoy' },
]

function toggleSidebar() {
  isCollapsed.value = !isCollapsed.value
}
</script>

<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <nav>
      <button
        v-for="item in navItems"
        :key="item.label"
        :class="{ active: item.page === activePage }"
        :disabled="!item.page"
        :title="isCollapsed ? item.label : ''"
        @click="item.page && emit('change-page', item.page)"
      >
        <component :is="item.icon" :size="23" />
        <span v-if="!isCollapsed">{{ item.label }}</span>
      </button>
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
