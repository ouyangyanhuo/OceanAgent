<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { Bot, ChevronDown, Leaf, LoaderCircle, MessageSquare, Plus, Search, Send, Settings, Trash2, X } from 'lucide-vue-next'
import { marked } from 'marked'
import gsap from 'gsap'
import MetricCard from '../components/MetricCard.vue'

marked.setOptions({ gfm: true, breaks: true })

// ── Metrics（静态展示） ──
const metrics = [
  { label: '今日问答量', value: '2,184', trend: '18.7%', tone: 'blue', sparkline: [25, 24, 31, 28, 37, 33, 44, 32, 38, 40, 36, 48] },
  { label: '知识节点命中', value: '56,782', trend: '9.6%', tone: 'cyan', sparkline: [26, 33, 30, 36, 34, 41, 38, 46, 42, 49, 47, 55] },
  { label: '问答准确率', value: '92.6%', trend: '2.1%', tone: 'teal', sparkline: [32, 34, 31, 38, 36, 40, 39, 44, 42, 47, 45, 50] },
  { label: '热点生态主题', value: '海草床、珊瑚礁、红树林', trend: '5个', tone: 'rose', sparkline: [18, 20, 26, 22, 31, 25, 34, 30, 39, 35, 44, 41] },
]

const circumference = 2 * Math.PI * 50
const donutSegments = [
  { label: '90%以上', count: '28,764', percent: 50.7, color: '#1173ff' },
  { label: '70%-90%', count: '16,218', percent: 28.6, color: '#20d6ff' },
  { label: '50%-70%', count: '7,842', percent: 13.8, color: '#28e78f' },
  { label: '30%-50%', count: '2,964', percent: 5.2, color: '#f5a623' },
].map((seg, i, arr) => {
  const offset = arr.slice(0, i).reduce((s, p) => s + p.percent, 0)
  const len = (seg.percent / 100) * circumference
  return { ...seg, dasharray: `${len} ${circumference - len}`, dashoffset: circumference * (1 - offset / 100) }
})

// ── 对话管理 ──
const STORAGE_KEY = 'qa_conversations'
const ACTIVE_KEY = 'qa_active_id'

const conversations = ref([])
const activeConvId = ref('')
const showConvList = ref(false)
const inputText = ref('')
const isTyping = ref(false)
const messagesEl = ref(null)
const showConfig = ref(false)
const relatedNodes = ref([])
const relatedEdges = ref([])
let abortController = null

const modelInfo = ref([
  { name: '海洋生态问答智能体', version: 'v2.3', online: true, desc: '面向海洋生态知识问答、知识检索、关系推理与科普服务的智能体，支持多轮对话与上下文理解', tokens: '128K' },
])

function toggleModel(model) { model.online = !model.online }

/** 当前对话的消息列表 */
const messages = computed(() => {
  const conv = conversations.value.find(c => c.id === activeConvId.value)
  return conv ? conv.messages : []
})

/** 按时间倒序排列的对话列表 */
const sortedConvs = computed(() =>
  [...conversations.value].sort((a, b) => b.createdAt - a.createdAt),
)

function persist() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations.value))
  localStorage.setItem(ACTIVE_KEY, activeConvId.value)
}

function createConversation() {
  const conv = { id: crypto.randomUUID(), title: '新对话', messages: [], createdAt: Date.now() }
  conversations.value.push(conv)
  activeConvId.value = conv.id
  showConvList.value = false
  persist()
  scrollToBottom()
}

function switchConversation(id) {
  activeConvId.value = id
  showConvList.value = false
  relatedNodes.value = []
  relatedEdges.value = []
  persist()
  scrollToBottom()
}

function deleteConversation(id) {
  const idx = conversations.value.findIndex(c => c.id === id)
  if (idx === -1) return
  conversations.value.splice(idx, 1)
  if (activeConvId.value === id) {
    activeConvId.value = conversations.value.length ? conversations.value[0].id : ''
  }
  if (!conversations.value.length) createConversation()
  persist()
}

function clearCurrentMessages() {
  if (abortController) abortController.abort()
  isTyping.value = false
  relatedNodes.value = []
  relatedEdges.value = []
  const conv = conversations.value.find(c => c.id === activeConvId.value)
  if (conv) { conv.messages = []; persist() }
  scrollToBottom()
}

/** 对话标题自动取自第一条用户消息 */
function updateConvTitle(conv) {
  if (conv.title === '新对话') {
    const first = conv.messages.find(m => m.role === 'user')
    if (first) conv.title = first.text.slice(0, 20) + (first.text.length > 20 ? '...' : '')
  }
}

// ── Markdown 渲染 ──
function renderMarkdown(text) {
  if (!text) return ''
  try { return marked.parse(text) } catch { return text }
}

function scrollToBottom() {
  nextTick(() => { if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight })
}

// ── SSE 解析 ──
async function consumeSSE(reader, { onStatus, onContent, onDone }) {
  const decoder = new TextDecoder()
  let buffer = ''
  let currentEvent = ''
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''
    for (const line of lines) {
      if (line.startsWith('event: ')) { currentEvent = line.slice(7).trim() }
      else if (line.startsWith('data: ')) {
        try {
          const data = JSON.parse(line.slice(6))
          if (currentEvent === 'status') onStatus(data)
          else if (currentEvent === 'content') onContent(data.text || '')
          else if (currentEvent === 'done') onDone(data)
        } catch {}
        currentEvent = ''
      }
    }
  }
}

// ── 发送消息 ──
async function sendMessage() {
  const text = inputText.value.trim()
  if (!text || isTyping.value) return

  const conv = conversations.value.find(c => c.id === activeConvId.value)
  if (!conv) return

  conv.messages.push({ role: 'user', text })
  updateConvTitle(conv)
  inputText.value = ''
  scrollToBottom()

  isTyping.value = true
  relatedNodes.value = []
  relatedEdges.value = []
  abortController = new AbortController()

  conv.messages.push({ role: 'bot', text: '', status: '正在提取关键词...' })
  const botIdx = conv.messages.length - 1
  scrollToBottom()

  // 构建对话历史（最近 6 轮，排除当前问题）
  const history = conv.messages
    .slice(0, -2)
    .filter(m => m.text)
    .slice(-12)
    .map(m => ({ role: m.role, text: m.text }))

  try {
    const resp = await fetch('/api/agent/qa/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text, history }),
      signal: abortController.signal,
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)

    const reader = resp.body.getReader()
    const contentParts = []

    await consumeSSE(reader, {
      onStatus(data) { conv.messages[botIdx].status = data.message || 'AI 思考中...'; scrollToBottom() },
      onContent(chunk) { contentParts.push(chunk); conv.messages[botIdx].status = 'AI 输出中...' },
      onDone(data) {
        if (data.related_nodes) relatedNodes.value = data.related_nodes
        if (data.related_edges) relatedEdges.value = data.related_edges
      },
    })

    conv.messages[botIdx].text = contentParts.join('') || '未能获取到回答，请稍后重试。'
  } catch (err) {
    conv.messages[botIdx].text = err.name === 'AbortError'
      ? (conv.messages[botIdx].text || '已取消。')
      : '请求失败，请检查网络或后端服务是否正常运行。'
  } finally {
    conv.messages[botIdx].status = ''
    isTyping.value = false
    abortController = null
    persist()
    scrollToBottom()
  }
}

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage() }
}

function fillPrompt(text) {
  inputText.value = text
  document.querySelector('.chat-input input')?.focus()
}

// ── 生命周期 ──
onMounted(() => {
  // 从 localStorage 恢复对话
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
    if (saved.length) {
      conversations.value = saved
      activeConvId.value = localStorage.getItem(ACTIVE_KEY) || saved[0].id
    }
  } catch {}
  if (!conversations.value.length) createConversation()

  const tl = gsap.timeline({ defaults: { ease: 'power2.out' } })
  tl.from('.agent-search-metrics .metric-card', { y: 20, opacity: 0, duration: 0.6, stagger: 0.08 })
  tl.from('.page-hero', { y: 16, opacity: 0, duration: 0.5, ease: 'power3.out' }, '-=0.3')
  tl.from('.chat-panel', { x: -30, opacity: 0, duration: 0.5 }, '-=0.3')
  tl.from('.qa-aside > *', { y: 20, opacity: 0, duration: 0.5, stagger: 0.1 }, '-=0.3')
  scrollToBottom()
})

onUnmounted(() => { if (abortController) abortController.abort() })

// 持久化对话列表变更
watch(conversations, persist, { deep: true })
</script>

<template>
  <section class="page agent-search-page min-w-0">
    <!-- Metrics -->
    <div class="metrics-grid agent-search-metrics min-w-0">
      <MetricCard v-for="metric in metrics" :key="metric.label" :metric="metric" />
    </div>

    <!-- Main layout -->
    <div class="agent-search-layout min-w-0">
      <div class="agent-search-main min-w-0">
        <!-- Page hero -->
        <div class="page-hero">
          <div class="page-hero-icon"><Search :size="28" /></div>
          <div class="page-hero-text">
            <h1>海洋生态问答智能体</h1>
            <p>面向海洋生态知识问答、知识检索、关系推理与科普服务的智能体</p>
          </div>
          <div class="page-hero-meta">
            <span class="meta-badge"><MessageSquare :size="14" /> 多轮对话</span>
          </div>
          <div class="page-actions">
            <button @click="showConfig = true"><Settings :size="17" />对话配置</button>
          </div>
        </div>

        <!-- Chat panel -->
        <section class="panel chat-panel">
          <header class="panel-header">
            <div class="conv-header">
              <div class="conv-selector" @click="showConvList = !showConvList">
                <MessageSquare :size="14" />
                <span class="conv-title">{{ conversations.find(c => c.id === activeConvId)?.title || '对话' }}</span>
                <ChevronDown :size="14" :class="{ rotated: showConvList }" />
              </div>
              <div v-if="showConvList" class="conv-dropdown">
                <div class="conv-dropdown-header">
                  <span>对话列表</span>
                  <button class="conv-new-btn" @click.stop="createConversation"><Plus :size="14" /></button>
                </div>
                <ul>
                  <li v-for="conv in sortedConvs" :key="conv.id"
                      :class="{ active: conv.id === activeConvId }"
                      @click="switchConversation(conv.id)">
                    <span class="conv-item-title">{{ conv.title }}</span>
                    <span class="conv-item-count">{{ conv.messages.filter(m => m.role === 'user').length }} 问</span>
                    <button class="conv-del-btn" @click.stop="deleteConversation(conv.id)" title="删除对话">
                      <X :size="12" />
                    </button>
                  </li>
                </ul>
              </div>
            </div>
            <button class="clear-btn" @click="clearCurrentMessages"><Trash2 :size="14" /> 清空</button>
          </header>
          <div ref="messagesEl" class="messages">
            <!-- 空状态 -->
            <div v-if="!messages.length" class="empty-state">
              <div class="empty-icon"><MessageSquare :size="40" /></div>
              <p class="empty-title">输入问题开始对话</p>
              <p class="empty-desc">基于海洋知识图谱的智能问答，支持多轮对话</p>
              <div class="empty-chips">
                <button @click="fillPrompt('海洋生物多样性现状如何？')">海洋生物多样性现状如何？</button>
                <button @click="fillPrompt('珊瑚礁白化的原因及影响？')">珊瑚礁白化的原因及影响？</button>
                <button @click="fillPrompt('红树林生态价值有哪些？')">红树林生态价值有哪些？</button>
              </div>
            </div>
            <!-- 消息列表 -->
            <article v-for="(message, index) in messages" :key="index" :class="message.role">
              <span class="msg-avatar"><component :is="message.role === 'user' ? Leaf : Bot" :size="18" /></span>
              <p v-if="message.role === 'user'" class="msg-body">{{ message.text }}</p>
              <div v-else-if="message.text" class="msg-body md-content" v-html="renderMarkdown(message.text)"></div>
              <div v-else-if="message.status" class="msg-body thinking-body">
                <div class="thinking-indicator">
                  <LoaderCircle :size="16" class="spin" />
                  <span>{{ message.status }}</span>
                </div>
              </div>
            </article>
          </div>
          <div v-if="messages.length" class="prompt-chips">
            <button @click="fillPrompt('海洋生物多样性现状如何？')">海洋生物多样性现状如何？</button>
            <button @click="fillPrompt('珊瑚礁白化的原因及影响？')">珊瑚礁白化的原因及影响？</button>
            <button @click="fillPrompt('红树林生态价值有哪些？')">红树林生态价值有哪些？</button>
          </div>
          <label class="chat-input">
            <input
              v-model="inputText"
              placeholder="输入你的问题，Shift + Enter 换行，Enter 发送"
              @keydown="onKeydown"
            />
            <button @click="sendMessage"><Send :size="18" /></button>
          </label>
        </section>
      </div>

      <!-- Sidebar -->
      <aside class="agent-search-aside qa-aside min-w-0">
        <section v-if="relatedNodes.length" class="panel side-feed-panel">
          <header class="panel-header"><h2>图谱命中节点</h2></header>
          <ul>
            <li v-for="node in relatedNodes" :key="node.id">
              <span class="node-name">{{ node.name }}</span>
            </li>
          </ul>
        </section>
        <section class="panel side-feed-panel">
          <header class="panel-header"><h2>数据来源</h2></header>
          <ul>
            <li>Copernicus Marine Service <span>正常</span></li>
            <li>南海及邻近海区科学数据中心 <span>正常</span></li>
            <li>自然资源部海洋生态环境监测 <span>正常</span></li>
            <li>中科院海洋科学大数据中心 <span>正常</span></li>
            <li>中国海洋生物多样性数据库 <span>正常</span></li>
            <li>国家海洋科学数据中心 <span>正常</span></li>
            <li>卫星遥感海洋生态专题 <span>正常</span></li>
            <li>学术文献与知识库 <span>正常</span></li>
          </ul>
        </section>

        <section class="panel distribution-panel">
          <header class="panel-header"><h2>知识命中分布</h2></header>
          <div class="donut-row">
            <div class="donut-chart-wrapper">
              <svg class="donut-svg" viewBox="0 0 120 120">
                <circle class="donut-ring" cx="60" cy="60" r="50" />
                <circle
                  v-for="(seg, i) in donutSegments"
                  :key="i"
                  class="donut-segment"
                  :class="'seg-' + i"
                  cx="60" cy="60"
                  :r="50 - i * 11"
                  :stroke="seg.color"
                  :stroke-dasharray="seg.dasharray"
                  :stroke-dashoffset="seg.dashoffset"
                />
              </svg>
              <div class="donut-center">
                <span>命中分布</span>
                <strong>56,782</strong>
              </div>
            </div>
            <ul>
              <li v-for="(seg, i) in donutSegments" :key="i">
                <i class="seg-dot" :style="{ background: seg.color }"></i>
                <span>{{ seg.label }}</span>
                <b>{{ seg.count }}</b>
                <em>{{ seg.percent }}%</em>
              </li>
            </ul>
          </div>
        </section>
      </aside>
    </div>

    <!-- 对话配置弹窗 -->
    <Teleport to="body">
      <div v-if="showConfig" class="config-overlay" @click.self="showConfig = false">
        <div class="config-modal">
          <header class="config-header">
            <h2>对话配置</h2>
            <button class="config-close" @click="showConfig = false">&times;</button>
          </header>
          <div class="config-body">
            <div class="config-section">
              <h3>当前接入模型</h3>
              <div class="model-list">
                <div v-for="model in modelInfo" :key="model.name" class="model-item">
                  <div class="model-head">
                    <span class="model-name">{{ model.name }}</span>
                    <span class="model-version">{{ model.version }}</span>
                    <button
                      class="model-toggle"
                      :class="{ active: model.online }"
                      @click="toggleModel(model)"
                      :title="model.online ? '运行中 - 点击关闭' : '已关闭 - 点击开启'"
                    >
                      <i></i>
                      <span>{{ model.online ? '运行中' : '已关闭' }}</span>
                    </button>
                  </div>
                  <p class="model-desc">{{ model.desc }}</p>
                  <div class="model-meta">
                    <span>上下文窗口：<b>{{ model.tokens }}</b></span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </section>
</template>
