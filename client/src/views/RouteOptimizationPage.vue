<script setup>
import { ref, onMounted } from 'vue'
import { AlertTriangle, Bot, FileText, Fuel, Navigation, Share2, ShipWheel, Send, User, Loader2 } from 'lucide-vue-next'
import gsap from 'gsap'
import MetricCard from '../components/MetricCard.vue'

const metrics = [
  { label: '当前推荐航线', value: 'A1 航线', trend: '推荐中', tone: 'blue', sparkline: [15, 18, 23, 28, 35, 42, 50, 58, 64, 71, 77, 83] },
  { label: '预计航行时间', value: '78.6 小时', trend: '6.9%', tone: 'cyan', sparkline: [46, 42, 38, 36, 35, 33, 31, 30, 29, 27, 26, 24] },
  { label: '省油率', value: '12.4%', trend: '28.7吨', tone: 'teal', sparkline: [20, 24, 23, 29, 32, 31, 36, 38, 39, 42, 45, 48] },
  { label: '高风险海域', value: '2 处', trend: '1处', tone: 'rose', sparkline: [38, 34, 30, 26, 22, 20, 18, 17, 16, 15, 14, 13] },
]

const plans = [
  ['A1 (推荐)', '1,468', '78.6', '203.6', '12.4%', '低', '★★★★★'],
  ['A2 (备选)', '1,586', '84.2', '226.8', '4.6%', '中', '★★★★☆'],
  ['A3 (备选)', '1,634', '87.5', '238.9', '1.1%', '高', '★★★☆☆'],
]

const routeMetrics = ['风速', '浪高', '海流速度', '能见度', '预计燃油消耗', 'ETA 偏差']
const routeMetricValues = ['8.6', '2.1', '1.2', '9.6', '203.6', '-1.3']
const routeMetricUnits = ['m/s', 'm', 'kn', 'km', '吨', '%']

const allDataSources = [
  { name: '全球数值预报模式(GFS)', url: 'https://www.ncdc.noaa.gov/data-access/model-data/model-datasets/global-forcast-system-gfs' },
  { name: '全球波浪模型(WW3)', url: 'https://polar.ncep.noaa.gov/waves/wavewatch/' },
  { name: '全球海流模型(HYCOM)', url: 'https://www.hycom.org/' },
  { name: '港口AIS实时数据', url: 'https://www.marinetraffic.com/' },
  { name: '船舶历史航行数据', url: 'https://www.imo.org/en/OurWork/Safety/Pages/AIS.aspx' },
  { name: '海事通告与公告', url: 'https://www.imo.org/en/OurWork/Safety/Pages/AIS.aspx' },
]

const modelStatuses = ['航线优化模型', '气候融合模型', '海况风险评估模型', '燃油消耗预测模型', 'ETA 预测模型']

const segmentRisks = [
  { segment: 'S1', risk: '强风大浪', level: '高', time: '05-24 14:00 - 20:00' },
  { segment: 'S2', risk: '对流天气', level: '中', time: '05-24 20:00 - 05-25 02:00' },
  { segment: 'S3', risk: '海流强', level: '中', time: '05-25 02:00 - 08:00' },
  { segment: 'S4', risk: '能见度低', level: '低', time: '05-25 08:00 - 14:00' },
  { segment: 'S5', risk: '适航风险', level: '低', time: '05-25 14:00 - 20:00' },
]

const showDataSourceModal = ref(false)
const showChatModal = ref(false)
const showShareModal = ref(false)
const clickedSources = ref(new Set())
const chatMessages = ref([])
const chatInput = ref('')
const isLoading = ref(false)
const conversationId = ref('')

const initChat = () => {
  chatMessages.value = [{ role: 'assistant', content: '您好！我是航线优化智能体助手。请问有什么可以帮助您的？' }]
  conversationId.value = ''
}
const openChat = () => { showChatModal.value = true; initChat() }

const sendToCoze = async (message) => {
  isLoading.value = true
  try {
    const res = await fetch('/api/coze/chat', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, conversation_id: conversationId.value || null }),
    })
    const data = await res.json()
    if (data.success) {
      if (data.conversation_id) conversationId.value = data.conversation_id
      chatMessages.value.push({ role: 'assistant', content: data.message })
    } else {
      chatMessages.value.push({ role: 'assistant', content: data.message || '抱歉，智能体暂时无法回复。' })
    }
  } catch {
    chatMessages.value.push({ role: 'assistant', content: '连接智能体时出现问题，请检查网络后重试。' })
  } finally { isLoading.value = false }
}

const sendMessage = async () => {
  if (!chatInput.value.trim() || isLoading.value) return
  const msg = chatInput.value.trim()
  chatMessages.value.push({ role: 'user', content: msg })
  chatInput.value = ''
  await sendToCoze(msg)
}

const clickDataSource = (s) => { if (s.url) { window.open(s.url, '_blank'); clickedSources.value.add(s.name); clickedSources.value = new Set(clickedSources.value) } }
const isSourceClicked = (n) => clickedSources.value.has(n)
const goToMapView = () => window.open('https://www.openstreetmap.org/export/embed.html?bbox=115,20,130,35&layer=mapnik', '_blank')

const generateReport = () => {
  const t = new Date().toLocaleString('zh-CN')
  const blob = new Blob([`航线优化智能体报告\n==================\n生成时间：${t}\n\n一、航线概览\n最优航线：A1 | 上海港→那霸港 | 1,468km | 78.6h\n\n二、关键指标\n风速 8.6m/s | 浪高 2.1m | 海流 1.2kn | 能见度 9.6km | 燃油 203.6吨\n\n三、方案对比\nA1推荐 1,468km 78.6h 203.6t 12.4% 低风险 ★★★★★\nA2备选 1,586km 84.2h 226.8t 4.6%  中风险 ★★★★☆\nA3备选 1,634km 87.5h 238.9t 1.1%  高风险 ★★★☆☆\n\n四、优化建议\n1. 推荐A1航线，综合能效与风险最佳\n2. 关注S1强风大浪区域\n3. 优化航速可节油2.3吨\n`], { type: 'text/plain;charset=utf-8' })
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `航线优化报告_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')}.txt`; a.click(); URL.revokeObjectURL(a.href)
}

const shareText = '航线优化智能体报告 - A1航线 上海港→那霸港 1,468km 78.6h 节油12.4%'
const shareToWechat = () => { navigator.clipboard.writeText(shareText).then(() => alert('已复制到剪贴板')); showShareModal.value = false }
const shareToQQ = () => { window.open(`http://connect.qq.com/widget/shareqq/index.html?title=航线优化报告&summary=${encodeURIComponent(shareText)}`, '_blank'); showShareModal.value = false }

onMounted(() => {
  const ctx = gsap.context(() => {
    gsap.from('.route-metrics .metric-card', { y: 20, opacity: 0, duration: 0.6, stagger: 0.08, ease: 'power3.out' })
    gsap.from('.page-hero', { y: 16, opacity: 0, duration: 0.5, ease: 'power3.out', delay: 0.2 })
    gsap.from('.route-main > *:not(.page-hero):not(.route-metrics)', { y: 24, opacity: 0, duration: 0.6, stagger: 0.1, ease: 'power3.out', delay: 0.35 })
    gsap.from('.route-aside > *', { y: 20, opacity: 0, duration: 0.5, stagger: 0.1, ease: 'power3.out', delay: 0.5 })
  })
  return () => ctx.revert()
})
</script>

<template>
  <section class="page agent-search-page min-w-0">

    <!-- ── 指标卡片 ── -->
    <div class="metrics-grid route-metrics min-w-0">
      <MetricCard v-for="m in metrics" :key="m.label" :metric="m" />
    </div>

    <!-- ── 主布局 ── -->
    <div class="agent-search-layout min-w-0">
      <div class="agent-search-main route-main min-w-0">

        <!-- 页首 -->
        <div class="page-hero">
          <div class="page-hero-icon route-hero-icon"><ShipWheel :size="28" /></div>
          <div class="page-hero-text">
            <h1>航线优化智能体</h1>
            <p>船舶航线规划 · 气象海况融合 · 风险规避 · 能效优化</p>
          </div>
          <div class="page-hero-meta">
            <span class="meta-badge"><Navigation :size="14" /> 3 条航线</span>
          </div>
          <div class="page-actions">
            <button @click="openChat"><Bot :size="17" /> 智能问答</button>
            <button @click="generateReport"><FileText :size="17" /> 报告生成</button>
            <button @click="showShareModal = true"><Share2 :size="17" /> 分享</button>
          </div>
        </div>

        <!-- 航线地图 -->
        <section class="panel ocean-map">
          <header class="panel-header">
            <h2>航线优化地图</h2>
            <div class="tabs"><button @click="goToMapView"><Navigation :size="14" /> 综合视图</button></div>
          </header>
          <div class="map-surface route-surface">
            <span class="place p1">上海</span>
            <span class="place p2">宁波</span>
            <span class="place p3">台州</span>
            <span class="place p4">厦门</span>
            <span class="place p5">那霸</span>
            <svg viewBox="0 0 100 60" preserveAspectRatio="none">
              <defs>
                <filter id="glowCyan"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
              </defs>
              <polyline class="route-alt-2" points="28,22 30,36 44,42 60,46 78,50" />
              <polyline class="route-alt-2" points="18,12 34,18 48,22 61,25 77,31 90,40" />
              <polyline class="route-main route-optimal" points="18,12 27,20 38,24 50,34 63,40 76,48 88,52" />
              <g class="route-arrow">
                <polygon points="50,34 47,31 48,36" fill="#16d6ff" />
                <polygon points="63,40 60,37 61,42" fill="#16d6ff" />
                <polygon points="76,48 73,45 74,50" fill="#16d6ff" />
              </g>
            </svg>
            <div class="optimal-label">
              <span class="route-name">A1</span>
              <span class="route-tag-text">最优推荐</span>
            </div>
            <i class="danger-zone dz1"></i>
            <i class="danger-zone dz2"></i>
            <i class="weather-zone wz1"></i>
            <b class="port start">上海港</b>
            <b class="port end">那霸港</b>
            <div class="map-legend buoy-legend route-legend-small">
              <span class="cyan">A1 最优</span>
              <span class="blue">A2 备选</span>
              <span class="route-alt-hint">A3 备选</span>
              <span class="red">高风险</span>
              <span class="amber">中风险</span>
            </div>
          </div>
        </section>

        <!-- 关键指标 -->
        <section class="panel micro-panel">
          <header class="panel-header">
            <h2>关键航线指标</h2>
            <div class="tabs"><button>24小时</button></div>
          </header>
          <div class="micro-grid">
            <article v-for="(item, i) in routeMetrics" :key="item" :class="`tone-${['cyan','blue','teal','sky','green','indigo'][i]}`">
              <span>{{ item }}</span>
              <strong>{{ routeMetricValues[i] }} <small>{{ routeMetricUnits[i] }}</small></strong>
              <small class="trend">{{ i === 2 ? '↑ 0.2' : '↓ 0.8' }}</small>
              <svg viewBox="0 0 100 28" preserveAspectRatio="none">
                <polyline points="0,18 12,15 25,12 38,13 52,19 68,15 84,16 100,13" />
              </svg>
            </article>
          </div>
        </section>

        <!-- 方案对比 -->
        <section class="panel detail-table">
          <header class="panel-header"><h2>航线方案对比</h2></header>
          <table>
            <thead><tr><th>方案</th><th>航程</th><th>时间</th><th>燃油</th><th>节油率</th><th>风险</th><th>评分</th></tr></thead>
            <tbody>
              <tr v-for="(r, i) in plans" :key="r[0]" :class="{ 'optimal-row': i === 0 }">
                <td><span v-if="i === 0" class="optimal-tag">★ {{ r[0] }}</span><span v-else>{{ r[0] }}</span></td>
                <td>{{ r[1] }} <small class="unit">km</small></td>
                <td>{{ r[2] }} <small class="unit">h</small></td>
                <td>{{ r[3] }} <small class="unit">吨</small></td>
                <td><span v-if="i === 0" class="highlight-value">{{ r[4] }}</span><span v-else>{{ r[4] }}</span></td>
                <td><span :class="['risk-badge', 'risk-' + r[5]]">{{ r[5] }}</span></td>
                <td><span v-if="i === 0" class="star-rating best">{{ r[6] }}</span><span v-else>{{ r[6] }}</span></td>
              </tr>
            </tbody>
          </table>
        </section>

        <!-- 优化建议 -->
        <section class="panel qa-advice-panel">
          <header class="panel-header"><h2>智能优化建议</h2></header>
          <article><Navigation :size="18" /><span>推荐 A1 航线，综合能效与风险表现最佳。</span></article>
          <article><AlertTriangle :size="18" /><span>关注 S1 强风大浪区域，保持安全距离。</span></article>
          <article><Fuel :size="18" /><span>优化航速可进一步节油，预计节省 2.3 吨。</span></article>
        </section>
      </div>

      <!-- ── 侧边栏 ── -->
      <aside class="agent-search-aside route-aside min-w-0">
        <section class="panel side-feed-panel">
          <header class="panel-header"><h2>数据来源</h2><button class="more-btn" @click="showDataSourceModal = true">更多 ›</button></header>
          <ul>
            <li v-for="s in allDataSources.slice(0, 5)" :key="s.name" :class="['source-link', { clicked: isSourceClicked(s.name) }]" @click="clickDataSource(s)">{{ s.name }} <span>正常</span></li>
          </ul>
        </section>

        <section class="panel side-feed-panel">
          <header class="panel-header"><h2>模型运行状态</h2></header>
          <ul><li v-for="m in modelStatuses" :key="m">{{ m }} <span>运行中</span></li></ul>
        </section>

        <section class="panel trend-panel">
          <header class="panel-header"><h2>趋势预测</h2><div class="tabs"><button>24小时</button></div></header>
          <div class="line-chart">
            <svg viewBox="0 0 100 45" preserveAspectRatio="none" class="trend-svg">
              <polyline class="trend-line line1" points="0,26 10,23 20,17 30,18 40,22 50,16 60,20 70,14 80,19 90,16 100,21" />
              <polyline class="trend-line line2" points="0,18 10,16 20,12 30,13 40,17 50,10 60,11 70,17 80,20 90,14 100,16" />
            </svg>
          </div>
        </section>

        <section class="panel detail-table compact">
          <header class="panel-header"><h2>航段风险</h2></header>
          <table>
            <tbody>
              <tr v-for="r in segmentRisks" :key="r.segment">
                <td><span :class="`risk-segment level-${r.level}`">{{ r.segment }}</span> {{ r.risk }}</td>
                <td>{{ r.time }}</td>
              </tr>
            </tbody>
          </table>
        </section>
      </aside>
    </div>

    <!-- ── 弹窗 ── -->
    <Teleport to="body">
      <div v-if="showDataSourceModal" class="modal-overlay" @click.self="showDataSourceModal = false">
        <div class="modal-content" style="width:420px"><div class="modal-header"><h3>全部数据来源</h3><button class="modal-close" @click="showDataSourceModal = false">&times;</button></div>
          <ul class="modal-source-list"><li v-for="s in allDataSources" :key="s.name" :class="['source-link', { clicked: isSourceClicked(s.name) }]" @click="clickDataSource(s)">{{ s.name }} <span>›</span></li></ul>
        </div>
      </div>
      <div v-if="showChatModal" class="modal-overlay chat-overlay" @click.self="showChatModal = false">
        <div class="modal-content chat-modal"><div class="modal-header"><h3><Bot :size="20" /> 航线优化智能体</h3><button class="modal-close" @click="showChatModal = false">&times;</button></div>
          <div class="chat-body">
            <div class="chat-messages">
              <div v-for="(m, i) in chatMessages" :key="i" :class="['chat-message', m.role]"><div class="message-avatar"><User v-if="m.role==='user'" :size="16"/><Bot v-else :size="16"/></div><div class="message-content">{{ m.content }}</div></div>
              <div v-if="isLoading" class="chat-message assistant"><div class="message-avatar"><Bot :size="16"/></div><div class="message-content loading"><Loader2 :size="16" class="spinner"/> 思考中...</div></div>
            </div>
            <div class="chat-input-area"><input v-model="chatInput" placeholder="输入您的问题..." @keyup.enter="sendMessage" :disabled="isLoading"/><button @click="sendMessage" :disabled="isLoading||!chatInput.trim()"><Send :size="18"/></button></div>
          </div>
        </div>
      </div>
      <div v-if="showShareModal" class="modal-overlay" @click.self="showShareModal = false">
        <div class="modal-content share-modal"><div class="modal-header"><h3>分享到</h3><button class="modal-close" @click="showShareModal = false">&times;</button></div>
          <div class="share-buttons">
            <button class="share-btn wechat" @click="shareToWechat"><svg viewBox="0 0 24 24" width="32" height="32"><path fill="#07C160" d="M8.5 13.5a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm5 0a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/><path fill="#07C160" d="M12 2C6.48 2 2 6.03 2 11c0 2.76 1.36 5.22 3.5 6.83V20l2.22-1.33 1.73 1.5a1 1 0 0 0 1.55-.71l1.6-3.2 2.9 1.63a1 1 0 0 0 1.35-.19c.37.21.8.19 1.15-.05l.8-.6V20l2.22-1.33 1.73 1.5a1 1 0 0 0 1.55-.71V17.83C21.64 16.22 23 13.76 23 11c0-4.97-4.48-9-11-9z"/></svg><span>微信</span></button>
            <button class="share-btn qq" @click="shareToQQ"><svg viewBox="0 0 24 24" width="32" height="32"><path fill="#12B7F5" d="M12 2c-2.27 0-6.29 1.31-6.29 7.33 0 1.62.47 3.64 1.49 5.74L5.32 17.21c-.21.44-.29.93-.22 1.42.18 1.33 1.41 2.37 2.78 2.37 1.18 0 2.22-.73 2.74-1.82l1.91 1.35c.27.19.59.29.92.29h.02c.41-.02.8-.14 1.14-.34l2.19-1.33a1.3 1.3 0 0 0 .51-.54c.13.22.32.4.55.53l2.19 1.33c.34.2.73.32 1.14.34h.02c.33 0 .65-.1.92-.29l1.91-1.35c.52 1.09 1.56 1.82 2.74 1.82 1.37 0 2.6-1.04 2.78-2.37.07-.49-.01-.98-.22-1.42l-1.88-2.14C22.48 14.1 23 12.08 23 10.33 23 4.31 18.97 3 16.71 3c-1.14 0-2.23.22-3.22.64.05-.21.08-.43.08-.65C13.57.78 11.04-1 7.92-1S2.27.78 2.27 3c0 .22.03.44.08.65C1.36 3.22.27 3 .27 3"/></svg><span>QQ</span></button>
          </div>
        </div>
      </div>
    </Teleport>
  </section>
</template>
