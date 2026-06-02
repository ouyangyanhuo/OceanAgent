<script setup>
import { Box, Database, GitFork, Home, Network, SearchCheck, Settings, Workflow } from 'lucide-vue-next'

const navItems = [
  { label: '工作台', icon: Home },
  { label: '智能体检索', icon: SearchCheck, active: true },
  { label: '关系图谱', icon: GitFork },
  { label: '数据中心', icon: Database },
  { label: '任务编排', icon: Workflow },
  { label: '模型管理', icon: Box },
  { label: '系统设置', icon: Settings },
]
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
      <a v-for="item in navItems" :key="item.label" :class="{ active: item.active }">
        <component :is="item.icon" :size="23" />
        <span>{{ item.label }}</span>
      </a>
    </nav>
    <div class="radar-art">
      <div class="radar-rings"></div>
      <div class="ship">△</div>
    </div>
    <button class="collapse-button">收起菜单</button>
  </aside>
</template>
