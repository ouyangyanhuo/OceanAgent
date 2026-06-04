<script setup>
import { ref, watch, onMounted } from 'vue'
import { AlertTriangle, Bot, CheckCircle2, Flame, Link2, Play, Search, Share2, Target } from 'lucide-vue-next'

const props = defineProps({
  metric: { type: Object, required: true },
})

const iconMap = {
  接入智能体: Bot,
  今日检索: Search,
  知识节点: Share2,
  关系边数: Link2,
  执行中任务: Play,
  已完成任务: CheckCircle2,
  异常任务: AlertTriangle,
  智能体协同次数: Share2,
  今日问答量: Bot,
  知识节点命中: Target,
  问答准确率: CheckCircle2,
  热点生态主题: Flame,
}

const displayValue = ref('')
let animFrame = null

/** 解析 value 字符串，提取数字部分和前后缀 */
function parseNumericValue(val) {
  if (typeof val !== 'string') return null
  // 匹配：前缀（可选）+ 数字（含逗号/小数）+ 后缀（可选）
  const m = val.match(/^([\d,]+\.?\d*)(.*)$/)
  if (!m) return null
  const numStr = m[1].replace(/,/g, '')
  const num = parseFloat(numStr)
  if (isNaN(num)) return null
  return { target: num, suffix: m[2], hasComma: m[1].includes(','), decimals: (m[1].split('.')[1] || '').length }
}

/** 格式化数字回原始样式 */
function formatNumber(num, info) {
  let fixed = num.toFixed(info.decimals)
  if (info.hasComma) {
    const parts = fixed.split('.')
    parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',')
    fixed = parts.join('.')
  }
  return fixed + info.suffix
}

/** 缓动函数：先快后慢 */
function easeOutCubic(t) {
  return 1 - Math.pow(1 - t, 3)
}

/** 播放数字滚动动画 */
function animateValue(target, suffix, info) {
  if (animFrame) cancelAnimationFrame(animFrame)
  const duration = 1200
  const start = performance.now()

  function tick(now) {
    const elapsed = now - start
    const progress = Math.min(elapsed / duration, 1)
    const eased = easeOutCubic(progress)
    const current = target * eased
    displayValue.value = formatNumber(current, info)

    if (progress < 1) {
      animFrame = requestAnimationFrame(tick)
    }
  }
  animFrame = requestAnimationFrame(tick)
}

function initAnimation() {
  const info = parseNumericValue(props.metric.value)
  if (info && info.target > 0) {
    displayValue.value = formatNumber(0, info)
    animateValue(info.target, info.suffix, info)
  } else {
    displayValue.value = props.metric.value
  }
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

onMounted(initAnimation)
watch(() => props.metric.value, initAnimation)
</script>

<template>
  <article class="metric-card" :class="`tone-${metric.tone}`">
    <div class="metric-top">
      <div class="metric-icon"><component :is="iconMap[metric.label] || Bot" :size="26" /></div>
      <span>{{ metric.label }}</span>
    </div>
    <strong>{{ displayValue }}</strong>
    <p>较昨日 <b>↑ {{ metric.trend }}</b></p>
    <svg viewBox="0 0 100 48" preserveAspectRatio="none" aria-hidden="true">
      <path :d="sparklinePath(metric.sparkline)" />
    </svg>
  </article>
</template>
