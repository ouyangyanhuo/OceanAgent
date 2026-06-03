<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import gsap from 'gsap'

const now = ref(new Date())
let timer = null
let loadTween = null

// 数据更新时间：固定为今天凌晨 2:00:00
const lastUpdate = (() => {
  const today = new Date()
  return new Date(today.getFullYear(), today.getMonth(), today.getDate(), 2, 0, 0)
})()

function formatTime(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  const h = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')
  const s = String(date.getSeconds()).padStart(2, '0')
  return `${y}-${m}-${d}&nbsp;&nbsp;${h}:${min}:${s}`
}

function timeAgo(from) {
  const diffMs = now.value - from
  const hours = Math.floor(diffMs / 3600000)
  const minutes = Math.floor((diffMs % 3600000) / 60000)
  if (hours > 0) return `${hours} 小时 ${minutes} 分钟前`
  return `${minutes} 分钟前`
}

function animateLoadBar(el) {
  const target = gsap.utils.random(40, 70, 1)
  loadTween = gsap.to(el, {
    width: `${target}%`,
    duration: gsap.utils.random(5, 10),
    ease: 'sine.inOut',
    onComplete: () => animateLoadBar(el),
  })
}

onMounted(() => {
  timer = setInterval(() => { now.value = new Date() }, 1000)
  const barEl = document.querySelector('.load-bar em')
  if (barEl) animateLoadBar(barEl)
})

onUnmounted(() => {
  clearInterval(timer)
  loadTween?.kill()
})
</script>

<template>
  <footer class="statusbar">
    <span>系统状态 <b class="dot"></b> 运行正常</span>
    <span>数据更新 <strong v-html="timeAgo(lastUpdate)"></strong></span>
    <span>服务负载 <i class="load-bar"><em style="width:45%"></em></i></span>
    <span>存储使用 <i><em style="width:68%"></em></i> 68%</span>
    <span>当前时间 <strong v-html="formatTime(now)"></strong></span>
  </footer>
</template>
