<script setup>
import { ref } from 'vue'
import gsap from 'gsap'
import { onMounted } from 'vue'
import { FileDown, Image, FileJson, Network, Plus, Link, GitFork } from 'lucide-vue-next'
import KnowledgeGraph from '../components/KnowledgeGraph.vue'
import AppModal from '../components/common/AppModal.vue'
import { createSeedNode, connectNodes } from '../services/graph'

const NODE_TYPE_COLORS = {
  Buoy: '#22c55e', Observation: '#06b6d4',
  RiskFactor: '#f43f5e', RedTideEvent: '#f43f5e',
  Species: '#14b8a6', FisheryArea: '#22c55e', PreventionMeasure: '#f59e0b',
}
const NODE_TYPE_LABELS = {
  Buoy: '浮标', Observation: '观测',
  RiskFactor: '风险因子', RedTideEvent: '赤潮事件',
  Species: '物种', FisheryArea: '渔场', PreventionMeasure: '防治措施',
}
function getNodeColor(type) { return NODE_TYPE_COLORS[type] || '#3b82f6' }
function getNodeLabel(type) { return NODE_TYPE_LABELS[type] || type }

const pageRef = ref(null)
const graphRef = ref(null)

// 导出弹窗
const showExportModal = ref(false)
function handleExport(format) {
  graphRef.value?.exportGraph(format)
  showExportModal.value = false
}

// 节点操作弹窗：'menu' | 'seed' | 'connect' | ''
const opsMode = ref('')

// 新建种子节点
const seedDesc = ref('')
const seedLoading = ref(false)
const seedError = ref('')

async function handleCreateSeed() {
  if (!seedDesc.value.trim()) return
  seedLoading.value = true
  seedError.value = ''
  const desc = seedDesc.value.trim()

  // 关闭弹窗，显示加载动画
  opsMode.value = ''
  graphRef.value?.setExpanding(`创建「${desc}」种子节点`)

  const result = await createSeedNode(desc)
  if (result) {
    const allNewNodes = [result.seed_node, ...(result.new_nodes || [])]
    graphRef.value?.mergeNewData(allNewNodes, result.new_edges || [])
    seedDesc.value = ''
  } else {
    seedError.value = '创建失败，请检查后端服务'
  }
  graphRef.value?.clearExpanding()
  seedLoading.value = false
}

// 节点连接
const connectStep = ref(1)
const connectSource = ref(null)
const connectTarget = ref(null)
const connectLoading = ref(false)
const connectError = ref('')

function getNodeList() {
  return graphRef.value?.getNodes() || []
}

function selectConnectNode(node) {
  if (connectStep.value === 1) {
    connectSource.value = node
    connectStep.value = 2
  } else {
    if (node.id === connectSource.value?.id) return
    connectTarget.value = node
  }
}

async function handleConnect() {
  if (!connectSource.value || !connectTarget.value) return
  connectLoading.value = true
  connectError.value = ''

  const srcName = connectSource.value.name
  const tgtName = connectTarget.value.name

  // 关闭弹窗，显示加载动画
  opsMode.value = ''
  graphRef.value?.setExpanding(`连接「${srcName}」与「${tgtName}」`)

  const result = await connectNodes(connectSource.value.id, connectTarget.value.id)
  if (result) {
    graphRef.value?.mergeNewData([result.bridge_node], result.new_edges || [])
    resetConnect()
  } else {
    connectError.value = '连接失败，请检查后端服务'
  }
  graphRef.value?.clearExpanding()
  connectLoading.value = false
}

function resetConnect() {
  connectStep.value = 1
  connectSource.value = null
  connectTarget.value = null
  connectError.value = ''
}

function openOpsMenu() {
  opsMode.value = 'menu'
  seedDesc.value = ''
  seedError.value = ''
  resetConnect()
}

function closeOps() {
  opsMode.value = ''
}

onMounted(() => {
  if (!pageRef.value) return
  const ctx = gsap.context(() => {
    gsap.from('.graph-hero', { y: 16, opacity: 0, duration: 0.5, ease: 'power3.out' })
    gsap.from('.graph-page-grid', { y: 20, opacity: 0, duration: 0.6, ease: 'power3.out', delay: 0.15 })
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
        <button class="btn-primary ops-btn" @click="openOpsMenu">
          <Plus :size="14" />
          节点操作
        </button>
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

    <!-- 节点操作菜单弹窗 -->
    <AppModal :visible="opsMode === 'menu'" title="节点操作" width="400px" @close="closeOps">
      <div class="ops-menu">
        <button class="ops-card" @click="opsMode = 'seed'">
          <div class="ops-card-icon seed"><Plus :size="22" /></div>
          <div class="ops-card-info">
            <span class="ops-card-label">新建种子节点</span>
            <span class="ops-card-desc">输入内容，由 AI 自动生成节点和关联关系</span>
          </div>
        </button>
        <button class="ops-card" @click="opsMode = 'connect'">
          <div class="ops-card-icon connect"><Link :size="22" /></div>
          <div class="ops-card-info">
            <span class="ops-card-label">节点连接</span>
            <span class="ops-card-desc">选择两个节点，AI 分析并生成关联桥梁</span>
          </div>
        </button>
      </div>
    </AppModal>

    <!-- 新建种子节点弹窗 -->
    <AppModal :visible="opsMode === 'seed'" title="新建种子节点" width="460px" @close="closeOps">
      <div class="seed-form">
        <p class="form-hint">描述你想要添加的海洋实体（如观测站、浮标、海域等），AI 将自动生成对应的节点和关联关系。</p>
        <textarea
          v-model="seedDesc"
          class="form-textarea"
          placeholder="例如：东海北部叶绿素观测站、渤海湾溶解氧监测浮标..."
          rows="3"
          :disabled="seedLoading"
        />
        <div v-if="seedError" class="form-error">{{ seedError }}</div>
      </div>
      <template #footer>
        <button class="btn-modal-cancel" @click="closeOps">取消</button>
        <button class="btn-modal-confirm" :disabled="!seedDesc.trim() || seedLoading" @click="handleCreateSeed">
          {{ seedLoading ? '生成中...' : '生成节点' }}
        </button>
      </template>
    </AppModal>

    <!-- 节点连接弹窗 -->
    <AppModal :visible="opsMode === 'connect'" title="节点连接" width="460px" @close="closeOps">
      <div class="connect-form">
        <p class="form-hint">选择两个节点，AI 将分析它们之间的关系并生成中间桥梁节点。</p>

        <div class="connect-steps">
          <div class="connect-step" :class="{ active: connectStep === 1, done: connectSource }">
            <span class="step-num">1</span>
            <span>选择源节点</span>
            <span v-if="connectSource" class="step-selected">{{ connectSource.name }}</span>
          </div>
          <div class="connect-step" :class="{ active: connectStep === 2, done: connectTarget }">
            <span class="step-num">2</span>
            <span>选择目标节点</span>
            <span v-if="connectTarget" class="step-selected">{{ connectTarget.name }}</span>
          </div>
        </div>

        <div class="connect-node-list">
          <button
            v-for="node in getNodeList()"
            :key="node.id"
            class="connect-node-item"
            :class="{
              selected: connectSource?.id === node.id || connectTarget?.id === node.id,
              disabled: connectSource?.id === node.id && connectStep === 2,
            }"
            :disabled="connectSource?.id === node.id && connectStep === 2"
            @click="selectConnectNode(node)"
          >
            <span class="node-type-dot" :style="{ background: getNodeColor(node.type) }"></span>
            <span class="node-name">{{ node.name }}</span>
            <span class="node-type-label">{{ getNodeLabel(node.type) }}</span>
          </button>
        </div>

        <div v-if="connectError" class="form-error">{{ connectError }}</div>
      </div>
      <template #footer>
        <button class="btn-modal-cancel" @click="closeOps">取消</button>
        <button
          v-if="connectSource && connectTarget"
          class="btn-modal-confirm"
          :disabled="connectLoading"
          @click="handleConnect"
        >
          {{ connectLoading ? '连接中...' : '建立连接' }}
        </button>
      </template>
    </AppModal>
  </section>
</template>

<style scoped>
.export-btn {
  display: flex;
  align-items: center;
  gap: 6px;
}

.ops-btn {
  display: flex;
  align-items: center;
  gap: 6px;
}

/* ── 导出卡片 ── */
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

/* ── 节点操作菜单 ── */
.ops-menu {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ops-card {
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

.ops-card:hover {
  border-color: rgba(83, 171, 255, 0.5);
  background: rgba(22, 141, 255, 0.12);
  color: #fff;
  transform: translateY(-1px);
}

.ops-card-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.ops-card-icon.seed {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.25);
}

.ops-card-icon.connect {
  background: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.25);
}

.ops-card-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.ops-card-label {
  font-size: 14px;
  font-weight: 600;
}

.ops-card-desc {
  font-size: 12px;
  color: rgba(158, 200, 231, 0.55);
}

/* ── 公共表单 ── */
.form-hint {
  margin: 0;
  font-size: 13px;
  color: #8fb9df;
  line-height: 1.5;
}

.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid rgba(39, 151, 255, 0.25);
  border-radius: 8px;
  background: rgba(5, 22, 43, 0.7);
  color: #dff7ff;
  font-size: 13px;
  line-height: 1.5;
  resize: vertical;
  outline: none;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-textarea:focus {
  border-color: rgba(39, 151, 255, 0.5);
}

.form-textarea::placeholder {
  color: rgba(122, 176, 216, 0.4);
}

.form-error {
  font-size: 12px;
  color: #f43f5e;
}

/* ── 弹窗按钮 ── */
.btn-modal-cancel {
  padding: 8px 18px;
  border: 1px solid rgba(39, 151, 255, 0.25);
  border-radius: 8px;
  background: transparent;
  color: #8fb9df;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-modal-cancel:hover {
  border-color: rgba(39, 151, 255, 0.5);
  color: #fff;
}

.btn-modal-confirm {
  padding: 8px 18px;
  border: 1px solid rgba(83, 171, 255, 0.6);
  border-radius: 8px;
  background: linear-gradient(135deg, #1488ff, #0952f5);
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.btn-modal-confirm:hover:not(:disabled) {
  box-shadow: 0 4px 16px rgba(16, 118, 255, 0.4);
}

.btn-modal-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* ── 种子节点表单 ── */
.seed-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* ── 节点连接 ── */
.connect-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.connect-steps {
  display: flex;
  gap: 10px;
}

.connect-step {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  background: rgba(14, 51, 86, 0.3);
  border: 1px solid rgba(39, 151, 255, 0.12);
  font-size: 12px;
  color: #6b8aab;
  transition: all 0.2s;
}

.connect-step.active {
  border-color: rgba(83, 171, 255, 0.5);
  color: #b9d6ee;
}

.connect-step.done {
  border-color: rgba(34, 197, 94, 0.4);
  color: #4ade80;
}

.step-num {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: rgba(39, 151, 255, 0.2);
  display: grid;
  place-items: center;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
}

.step-selected {
  margin-left: auto;
  font-weight: 600;
  color: #4ade80;
  font-size: 11px;
}

.connect-node-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-height: 260px;
  overflow-y: auto;
}

.connect-node-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border: 1px solid transparent;
  border-radius: 7px;
  background: transparent;
  color: #b9d6ee;
  cursor: pointer;
  font-size: 13px;
  text-align: left;
  transition: all 0.15s;
}

.connect-node-item:hover:not(.disabled) {
  background: rgba(22, 141, 255, 0.1);
  border-color: rgba(39, 151, 255, 0.2);
}

.connect-node-item.selected {
  background: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
  color: #4ade80;
}

.connect-node-item.disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.node-type-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.node-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-type-label {
  font-size: 11px;
  color: rgba(158, 200, 231, 0.4);
  flex-shrink: 0;
}
</style>
