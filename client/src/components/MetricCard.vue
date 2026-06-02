<script setup>
import { Bot, Link2, Search, Share2 } from 'lucide-vue-next'

const props = defineProps({
  metric: { type: Object, required: true },
})

const iconMap = {
  接入智能体: Bot,
  今日检索: Search,
  知识节点: Share2,
  关系边数: Link2,
}

function sparklinePath(values) {
  const max = Math.max(...values)
  const min = Math.min(...values)
  return values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * 100
      const y = 42 - ((value - min) / (max - min || 1)) * 34
      return `${index === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`
    })
    .join(' ')
}
</script>

<template>
  <article class="metric-card" :class="`tone-${metric.tone}`">
    <div class="metric-top">
      <div class="metric-icon"><component :is="iconMap[metric.label]" :size="26" /></div>
      <span>{{ metric.label }}</span>
    </div>
    <strong>{{ metric.value }}</strong>
    <p>较昨日 <b>↑ {{ metric.trend }}</b></p>
    <svg viewBox="0 0 100 48" preserveAspectRatio="none" aria-hidden="true">
      <path :d="sparklinePath(metric.sparkline)" />
    </svg>
  </article>
</template>
