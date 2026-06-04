<script setup>
import { nextTick, onMounted, ref } from 'vue'
import { Bot, Leaf, MessageSquare, Search, Send, Settings } from 'lucide-vue-next'
import gsap from 'gsap'
import MetricCard from '../components/MetricCard.vue'

const metrics = [
  { label: '今日问答量', value: '2,184', trend: '18.7%', tone: 'blue', sparkline: [25, 24, 31, 28, 37, 33, 44, 32, 38, 40, 36, 48] },
  { label: '知识节点命中', value: '56,782', trend: '9.6%', tone: 'cyan', sparkline: [26, 33, 30, 36, 34, 41, 38, 46, 42, 49, 47, 55] },
  { label: '问答准确率', value: '92.6%', trend: '2.1%', tone: 'teal', sparkline: [32, 34, 31, 38, 36, 40, 39, 44, 42, 47, 45, 50] },
  { label: '热点生态主题', value: '海草床、珊瑚礁、红树林', trend: '5个', tone: 'rose', sparkline: [18, 20, 26, 22, 31, 25, 34, 30, 39, 35, 44, 41] },
]

const defaultMessages = [
  ['user', '什么是海草床？它对海洋生态系统有哪些作用？'],
  ['bot', '海草床是由海草植物在浅海海底形成的重要生态系统。它具有重要的生态功能：提供栖息与繁殖场所、固定沉积物改善水质、吸收和储存碳、支撑渔业资源并促进生物多样性。'],
  ['user', '中国沿海有哪些典型的海草床分布区域？'],
  ['bot', '中国海草床主要分布在广东沿江、福建厦门、海南三亚、广西北海、浙江舟山等沿海海域。其中海南的海草床面积较大，种类丰富，以海菖蒲、卵叶喜盐草等常见。'],
  ['user', '赤潮发生的原因有哪些？如何预警？'],
  ['bot', '赤潮通常由营养盐富集、水温升高、海流静稳、光照充足等因素引发。预警应结合遥感监测、浮标温盐、水质检测与历史数据建模进行综合评估。'],
  ['user', '如果要做近岸生态修复，应该优先关注哪些指标？'],
  ['bot', '近岸生态修复应优先关注水体营养盐、溶解氧、透明度、底质类型、生境连通性、关键物种恢复情况和人为扰动强度。对海草床、红树林和珊瑚礁等不同生态系统，还需要分别跟踪覆盖度、幼苗成活率、白化率和群落结构变化。'],
]

const botReplies = [
  '这是一个很好的海洋生态问题。根据知识库中的文献和监测数据分析，海洋生态系统是一个复杂的相互关联的系统，需要从多维度进行综合评估。',
  '根据最新的海洋监测数据和学术研究表明，该领域近年来取得了显著进展。建议参考国家海洋科学数据中心的最新报告获取详细信息。',
  '从生态学角度分析，这一问题涉及多个关键因素：水文条件、营养盐循环、生物群落结构以及人类活动影响。综合来看，需要采取多层次的保护与修复策略。',
  '基于当前的海洋生态知识图谱，这个问题可以从以下几个方面来理解：生态系统服务功能、生物多样性保护、环境监测技术和政策法规框架。',
]

const messages = ref([...defaultMessages])
const inputText = ref('')
const isTyping = ref(false)
const messagesEl = ref(null)
const showConfig = ref(false)

const modelInfo = ref([
  { name: '海洋生态问答智能体', version: 'v2.3', online: true, desc: '面向海洋生态知识问答、知识检索、关系推理与科普服务的智能体，支持多轮对话与上下文理解', tokens: '128K' },
])

function toggleModel(model) {
  model.online = !model.online
}

const circumference = 2 * Math.PI * 50 // r=50

const donutSegments = [
  { label: '90%以上', count: '28,764', percent: 50.7, color: '#1173ff' },
  { label: '70%-90%', count: '16,218', percent: 28.6, color: '#20d6ff' },
  { label: '50%-70%', count: '7,842', percent: 13.8, color: '#28e78f' },
  { label: '30%-50%', count: '2,964', percent: 5.2, color: '#f5a623' },
].map((seg, i, arr) => {
  const offset = arr.slice(0, i).reduce((s, p) => s + p.percent, 0)
  const len = (seg.percent / 100) * circumference
  return {
    ...seg,
    dasharray: `${len} ${circumference - len}`,
    dashoffset: circumference * (1 - offset / 100),
  }
})

function scrollToBottom() {
  nextTick(() => {
    if (messagesEl.value) {
      messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    }
  })
}

function sendMessage() {
  const text = inputText.value.trim()
  if (!text || isTyping.value) return

  messages.value.push(['user', text])
  inputText.value = ''
  scrollToBottom()

  isTyping.value = true
  const reply = botReplies[Math.floor(Math.random() * botReplies.length)]
  const delay = 800 + Math.random() * 1200

  setTimeout(() => {
    messages.value.push(['bot', reply])
    isTyping.value = false
    scrollToBottom()
  }, delay)
}

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

function fillPrompt(text) {
  inputText.value = text
  document.querySelector('.chat-input input')?.focus()
}

function clearMessages() {
  messages.value = []
  nextTick(() => {
    messages.value = [...defaultMessages]
  })
}

onMounted(() => {
  const tl = gsap.timeline({ defaults: { ease: 'power2.out' } })

  // Metric cards stagger in
  tl.from('.agent-search-metrics .metric-card', {
    y: 20, opacity: 0, duration: 0.6, stagger: 0.08,
  })

  // Page hero
  tl.from('.page-hero', {
    y: 16, opacity: 0, duration: 0.5, ease: 'power3.out',
  }, '-=0.3')

  // Chat panel slide in
  tl.from('.chat-panel', {
    x: -30, opacity: 0, duration: 0.5,
  }, '-=0.3')

  // Sidebar panels stagger in
  tl.from('.qa-aside > *', {
    y: 20, opacity: 0, duration: 0.5, stagger: 0.1,
  }, '-=0.3')

  scrollToBottom()
})
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
          <header class="panel-header"><h2>生态问答对话</h2><button @click="clearMessages">清空对话</button></header>
          <div ref="messagesEl" class="messages">
            <article v-for="(message, index) in messages" :key="index" :class="message[0]">
              <span><component :is="message[0] === 'user' ? Leaf : Bot" :size="18" /></span>
              <p>{{ message[1] }}</p>
            </article>
            <article v-if="isTyping" class="bot typing-indicator">
              <span><Bot :size="18" /></span>
              <p><i class="typing-dots"><b></b><b></b><b></b></i></p>
            </article>
          </div>
          <div class="prompt-chips">
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
