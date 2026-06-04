<script setup>
import { ref } from 'vue'
import gsap from 'gsap'
import { onMounted } from 'vue'
import { FileDown, Image, FileJson, Network } from 'lucide-vue-next'
import KnowledgeGraph from '../components/KnowledgeGraph.vue'
import AppModal from '../components/common/AppModal.vue'

const pageRef = ref(null)
const graphRef = ref(null)
const showExportModal = ref(false)

function handleExport(format) {
  graphRef.value?.exportGraph(format)
  showExportModal.value = false
}

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
        <button class="btn-secondary export-btn" @click="showExportModal = true">
          <FileDown :size="14" />
          导出图谱
        </button>
        <button class="btn-primary">新建节点</button>
      </div>
    </div>
    <div class="graph-page-grid">
      <KnowledgeGraph ref="graphRef" />
    </div>

    <!-- 导出弹窗 -->
    <AppModal v-model:visible="showExportModal" title="导出图谱" width="400px">
      <div class="export-options">
        <button class="export-card" @click="handleExport('png')">
          <div class="export-card-icon png"><Image :size="22" /></div>
          <div class="export-card-info">
            <span class="export-card-label">PNG 图片</span>
            <span class="export-card-desc">高清截图，适合演示与分享</span>
          </div>
        </button>
        <button class="export-card" @click="handleExport('json')">
          <div class="export-card-icon json"><FileJson :size="22" /></div>
          <div class="export-card-info">
            <span class="export-card-label">JSON 数据</span>
            <span class="export-card-desc">原始结构数据，适合导入与备份</span>
          </div>
        </button>
      </div>
    </AppModal>
  </section>
</template>

<style scoped>
.export-btn {
  display: flex;
  align-items: center;
  gap: 6px;
}

.export-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.export-card {
  display: flex;
  align-items: center;
  gap: 14px;
  width: 100%;
  padding: 14px 16px;
  border: 1px solid rgba(39, 151, 255, 0.15);
  border-radius: 10px;
  background: rgba(14, 51, 86, 0.3);
  color: #b9d6ee;
  cursor: pointer;
  text-align: left;
  transition: all 0.2s;
}

.export-card:hover {
  border-color: rgba(83, 171, 255, 0.5);
  background: rgba(22, 141, 255, 0.12);
  color: #fff;
  transform: translateY(-1px);
}

.export-card-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.export-card-icon.png {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.25);
}

.export-card-icon.json {
  background: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.25);
}

.export-card-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.export-card-label {
  font-size: 14px;
  font-weight: 600;
}

.export-card-desc {
  font-size: 12px;
  color: rgba(158, 200, 231, 0.55);
}
</style>
