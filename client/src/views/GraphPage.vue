<script setup>
import { onMounted, ref } from 'vue'
import gsap from 'gsap'
import { Network } from 'lucide-vue-next'
import KnowledgeGraph from '../components/KnowledgeGraph.vue'

const pageRef = ref(null)

onMounted(() => {
  if (!pageRef.value) return
  const ctx = gsap.context(() => {
    gsap.from('.graph-hero', {
      y: 16,
      opacity: 0,
      duration: 0.5,
      ease: 'power3.out',
    })
    gsap.from('.graph-page-grid', {
      y: 20,
      opacity: 0,
      duration: 0.6,
      ease: 'power3.out',
      delay: 0.15,
    })
  }, pageRef.value)
  return () => ctx.revert()
})
</script>

<template>
  <section ref="pageRef" class="page graph-page">
    <div class="graph-hero min-w-0">
      <div class="graph-hero-left">
        <div class="agent-orb graph-orb"><Network :size="28" /></div>
        <div class="graph-hero-text">
          <h1>关系图谱</h1>
          <p>海洋环境事件与各要素之间的关联关系可视化</p>
        </div>
      </div>
      <div class="page-actions">
        <button class="btn-secondary">导出图谱</button>
        <button class="btn-primary">新建节点</button>
      </div>
    </div>
    <div class="graph-page-grid">
      <KnowledgeGraph />
    </div>
  </section>
</template>
