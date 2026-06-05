<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { AlertTriangle, Bot, FileText, Forward, Fuel, LoaderCircle, Navigation, Share, Share2, ShipWheel, Send, Trash2, X, User, Loader2 } from 'lucide-vue-next'
import { marked } from 'marked'
import gsap from 'gsap'
import MetricCard from '../components/MetricCard.vue'
import AppModal from '../components/common/AppModal.vue'
import OceanCurrent from '../components/common/OceanCurrent.vue'
import { useSatelliteMap } from '../composables/useSatelliteMap'

marked.setOptions({ gfm: true, breaks: true })

const { L, addSatelliteBaseLayer } = useSatelliteMap()

// ── 指标数据 ──
const metrics = [
  { label: '当前推荐航线', value: 'A1 航线', trend: '推荐中', tone: 'blue', sparkline: [15, 18, 23, 28, 35, 42, 50, 58, 64, 71, 77, 83] },
  { label: '预计航行时间', value: '78.6 小时', trend: '6.9%', tone: 'amber', sparkline: [46, 42, 38, 36, 35, 33, 31, 30, 29, 27, 26, 24] },
  { label: '省油率', value: '12.4%', trend: '28.7吨', tone: 'teal', sparkline: [20, 24, 23, 29, 32, 31, 36, 38, 39, 42, 45, 48] },
  { label: '高风险海域', value: '2 处', trend: '1处', tone: 'amber', sparkline: [38, 34, 30, 26, 22, 20, 18, 17, 16, 15, 14, 13] },
]

// ── 航线方案 ──
const plans = [
  ['A1 (推荐)', '1,468', '78.6', '203.6', '12.4%', '低', '★★★★★'],
  ['A2 (备选)', '1,586', '84.2', '226.8', '4.6%', '中', '★★★★☆'],
  ['A3 (备选)', '1,634', '87.5', '238.9', '1.1%', '高', '★★★☆☆'],
]

// ── 航线指标 ──
const routeMetrics = ['风速', '浪高', '海流速度', '能见度', '预计燃油消耗', 'ETA 偏差']
const routeMetricValues = ['8.6', '2.1', '1.2', '9.6', '203.6', '-1.3']
const routeMetricUnits = ['m/s', 'm', 'kn', 'km', '吨', '%']
const routeMetricDetails = [
  '当前区域平均风速 8.6m/s，建议关注',
  '当前海浪高度 2.1m，航行平稳',
  '海流速度 1.2 节，有利于航行',
  '能见度 9.6km，天气良好',
  '预计消耗燃油 203.6 吨',
  '预计到达时间偏差 -1.3 小时',
]

// ── 数据来源 ──
const allDataSources = [
  { name: '全球数值预报模式(GFS)', url: 'https://www.ncdc.noaa.gov/data-access/model-data/model-datasets/global-forcast-system-gfs' },
  { name: '全球波浪模型(WW3)', url: 'https://polar.ncep.noaa.gov/waves/wavewatch/' },
  { name: '全球海流模型(HYCOM)', url: 'https://www.hycom.org/' },
  { name: '港口AIS实时数据', url: 'https://www.marinetraffic.com/' },
  { name: '船舶历史航行数据', url: 'https://www.imo.org/en/OurWork/Safety/Pages/AIS.aspx' },
  { name: '海事通告与公告', url: 'https://www.imo.org/en/OurWork/Safety/Pages/AIS.aspx' },
  { name: '气象卫星云图', url: 'https://www.eumetsat.int/' },
  { name: '海洋遥感数据', url: 'https://sealevel.nasa.gov/' },
  { name: '航海通告服务', url: 'https://www.admiralty.co.uk/' },
]

const modelStatuses = [
  '航线优化模型', '气候融合模型', '海况风险评估模型',
  '燃油消耗预测模型', 'ETA 预测模型',
]

const segmentRisks = [
  { segment: 'S1', risk: '强风大浪', level: '高', time: '05-24 14:00 - 20:00' },
  { segment: 'S2', risk: '对流天气', level: '中', time: '05-24 20:00 - 05-25 02:00' },
  { segment: 'S3', risk: '海流强', level: '中', time: '05-25 02:00 - 08:00' },
  { segment: 'S4', risk: '能见度低', level: '低', time: '05-25 08:00 - 14:00' },
  { segment: 'S5', risk: '适航风险', level: '低', time: '05-25 14:00 - 20:00' },
]

// ── 航线坐标 ──
// A1 推荐：上海→宁波→那霸
const routeA1 = [
  [31.4, 121.5],  // 上海
  [29.9, 121.5],  // 宁波
  [28.7, 121.4],  // 台州
  [26.3, 127.8],  // 那霸
]

// A2 备选：上海→那霸（直达）
const routeA2 = [
  [31.4, 121.5],
  [26.3, 127.8],
]

// A3 备选：上海→宁波→台州→厦门→那霸
const routeA3 = [
  [31.4, 121.5],
  [29.9, 121.5],  // 宁波
  [28.7, 121.4],  // 台州
  [24.5, 118.1],  // 厦门
  [26.3, 127.8],  // 那霸
]

// ── 危险区域 ──
const dangerZones = [
  { center: [28.5, 124.5], radius: 80000, level: '高', label: '强风大浪区' },
  { center: [26.0, 122.0], radius: 60000, level: '中', label: '对流天气区' },
]

// ── 港口标注 ──
const ports = [
  { name: '上海港', lat: 31.4, lng: 121.5 },
  { name: '那霸港', lat: 26.3, lng: 127.8 },
  { name: '连云港', lat: 34.6, lng: 119.2 },
  { name: '青岛港', lat: 36.1, lng: 120.4 },
  { name: '烟台港', lat: 37.5, lng: 121.4 },
  { name: '大连港', lat: 38.9, lng: 121.6 },
  { name: '天津港', lat: 39.0, lng: 117.2 },
  { name: '日照港', lat: 35.4, lng: 119.5 },
  { name: '海口港', lat: 20.0, lng: 110.3 },
  { name: '三亚港', lat: 18.2, lng: 109.5 },
  { name: '洋浦港', lat: 19.7, lng: 109.2 },
  { name: '八所港', lat: 19.1, lng: 108.6 },
  { name: '清澜港', lat: 19.6, lng: 110.8 },
]

// ── 弹窗控制 ──
const showDataSourceModal = ref(false)
const showShareModal = ref(false)
const clickedSources = ref(new Set())

// ── Leaflet 地图 ──
let routeMap = null

const initRouteMap = () => {
  if (routeMap) {
    routeMap.remove()
    routeMap = null
  }

  routeMap = L.map('route-leaflet-map', {
    zoomControl: false,
    attributionControl: false
  }).setView([28, 124], 6)

  addSatelliteBaseLayer(routeMap)

  L.control.zoom({ position: 'topleft' }).addTo(routeMap)

  // A3 备选（粉色实线）
  L.polyline(routeA3, {
    color: '#ec4899',
    weight: 2.5,
    opacity: 0.7,
  }).addTo(routeMap).bindPopup('<b>A3 备选航线</b><br>上海→宁波→台州→厦门→那霸<br>航程：1,634 km<br>风险：高')

  // A2 备选（灰色实线）
  L.polyline(routeA2, {
    color: '#6b7280',
    weight: 2.5,
    opacity: 0.7,
  }).addTo(routeMap).bindPopup('<b>A2 备选航线</b><br>上海→那霸（直达）<br>航程：1,586 km<br>风险：中')

  // A1 推荐（绿色实线 + 发光）
  L.polyline(routeA1, {
    color: '#22c55e',
    weight: 4,
    opacity: 0.95,
    className: 'route-glow-line',
  }).addTo(routeMap).bindPopup('<b>A1 推荐航线</b><br>上海→宁波→那霸<br>航程：1,468 km<br>节油率：12.4%<br>风险：低')

  // 危险区域
  dangerZones.forEach(zone => {
    const color = zone.level === '高' ? '#ef4444' : '#f59e0b'
    L.circle(zone.center, {
      radius: zone.radius,
      color: color,
      fillColor: color,
      fillOpacity: 0.15,
      weight: 1.5,
      dashArray: '6, 4',
    }).addTo(routeMap).bindPopup(`<b>${zone.label}</b><br>风险等级：${zone.level}`)
  })

  // 港口标记
  ports.forEach(port => {
    const isMain = port.name === '上海港' || port.name === '那霸港'
    L.circleMarker([port.lat, port.lng], {
      radius: isMain ? 8 : 5,
      color: '#fff',
      weight: isMain ? 2 : 1.5,
      fillColor: '#3b82f6',
      fillOpacity: 1,
    })
      .addTo(routeMap)
      .bindTooltip(port.name, {
        permanent: isMain,
        direction: 'top',
        offset: [0, isMain ? -12 : -8],
        className: isMain ? 'port-label' : 'port-label-small',
      })
  })

  // 航路途经城市
  const routeCities = [
    { name: '宁波', lat: 29.9, lng: 121.5 },
    { name: '台州', lat: 28.7, lng: 121.4 },
    { name: '厦门', lat: 24.5, lng: 118.1 },
  ]
  routeCities.forEach(city => {
    L.circleMarker([city.lat, city.lng], {
      radius: 5,
      color: '#fff',
      weight: 1.5,
      fillColor: '#22c55e',
      fillOpacity: 0.9,
    })
      .addTo(routeMap)
      .bindTooltip(city.name, {
        permanent: true,
        direction: 'right',
        offset: [8, 0],
        className: 'city-label',
      })
  })

  // 参考城市（灰色小标注）
  const refCities = [
    { name: '温州', lat: 28.0, lng: 120.7 },
    { name: '福州', lat: 26.1, lng: 119.3 },
    { name: '泉州', lat: 24.9, lng: 118.6 },
    { name: '汕头', lat: 23.4, lng: 116.7 },
    { name: '高雄', lat: 22.6, lng: 120.3 },
    { name: '台北', lat: 25.0, lng: 121.5 },
    { name: '基隆', lat: 25.1, lng: 121.7 },
    { name: '冲绳', lat: 26.3, lng: 127.8 },
  ]
  refCities.forEach(city => {
    L.circleMarker([city.lat, city.lng], {
      radius: 3,
      color: 'rgba(255,255,255,0.5)',
      weight: 1,
      fillColor: 'rgba(255,255,255,0.3)',
      fillOpacity: 0.8,
    })
      .addTo(routeMap)
      .bindTooltip(city.name, {
        permanent: true,
        direction: 'right',
        offset: [6, 0],
        className: 'ref-city-label',
      })
  })

}

// ── 聊天相关 ──
const showChatModal = ref(false)
const chatMessages = ref([])
const chatInput = ref('')
const isLoading = ref(false)
let chatAbortController = null
const chatMessagesEl = ref(null)

function renderMarkdown(text) {
  if (!text) return ''
  try { return marked.parse(text) } catch { return text }
}

function chatScrollToBottom() {
  nextTick(() => { if (chatMessagesEl.value) chatMessagesEl.value.scrollTop = chatMessagesEl.value.scrollHeight })
}

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

const openChat = () => {
  showChatModal.value = true
  if (!chatMessages.value.length) {
    chatMessages.value = [{ role: 'bot', text: '您好！我是航线优化智能体助手。请问有什么可以帮助您的？' }]
  }
}

const sendChatMessage = async () => {
  const text = chatInput.value.trim()
  if (!text || isLoading.value) return

  chatMessages.value.push({ role: 'user', text })
  chatInput.value = ''
  isLoading.value = true
  chatAbortController = new AbortController()

  chatMessages.value.push({ role: 'bot', text: '', status: '正在提取关键词...' })
  const botIdx = chatMessages.value.length - 1
  chatScrollToBottom()

  const history = chatMessages.value
    .slice(0, -2)
    .filter(m => m.text)
    .slice(-12)
    .map(m => ({ role: m.role, text: m.text }))

  try {
    const resp = await fetch('/api/agent/qa/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text, history }),
      signal: chatAbortController.signal,
    })
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`)

    const reader = resp.body.getReader()
    const contentParts = []

    await consumeSSE(reader, {
      onStatus(data) { chatMessages.value[botIdx].status = data.message || 'AI 思考中...'; chatScrollToBottom() },
      onContent(chunk) { contentParts.push(chunk); chatMessages.value[botIdx].status = 'AI 输出中...' },
      onDone() {},
    })

    chatMessages.value[botIdx].text = contentParts.join('') || '未能获取到回答，请稍后重试。'
  } catch (err) {
    chatMessages.value[botIdx].text = err.name === 'AbortError'
      ? (chatMessages.value[botIdx].text || '已取消。')
      : '请求失败，请检查网络或后端服务是否正常运行。'
  } finally {
    chatMessages.value[botIdx].status = ''
    isLoading.value = false
    chatAbortController = null
    chatScrollToBottom()
  }
}

const clearChat = () => {
  if (chatAbortController) chatAbortController.abort()
  isLoading.value = false
  chatMessages.value = []
}

// ── 数据来源交互 ──
const clickDataSource = (source) => {
  if (source.url) {
    window.open(source.url, '_blank')
    clickedSources.value.add(source.name)
    clickedSources.value = new Set(clickedSources.value)
  }
}
const isSourceClicked = (name) => clickedSources.value.has(name)

// ── 生成报告 ──
const generateReport = async () => {
  const reportContent = `
航线优化智能体报告
==================

生成时间：${new Date().toLocaleString('zh-CN')}
报告类型：航线优化分析报告

一、航线概览
------------
• 最优航线：A1 航线
• 起点：上海港
• 终点：那霸港
• 总航程：1,468 km
• 预计航行时间：78.6 小时

二、关键指标
------------
• 风速：8.6 m/s
• 浪高：2.1 m
• 海流速度：1.2 kn
• 能见度：9.6 km
• 预计燃油消耗：203.6 吨
• ETA 偏差：-1.3 小时

三、方案对比
------------
方案    航程(km)  时间(h)  燃油(t)  节油率   风险
A1推荐   1,468    78.6    203.6   12.4%   低
A2备选   1,586    84.2    226.8   4.6%    中
A3备选   1,634    87.5    238.9   1.1%    高

四、风险区域
------------
• S1 强风大浪（高风险）- 05-24 14:00 - 20:00
• S2 对流天气（中风险）- 05-24 20:00 - 05-25 02:00
• S3 海流强（中风险）- 05-25 02:00 - 08:00

五、数据来源
------------
• 全球数值预报模式(GFS)
• 全球波浪模型(WW3)
• 全球海流模型(HYCOM)
• 港口AIS实时数据
• 船舶历史航行数据
• 海事通告与公告

六、模型状态
------------
所有模型运行正常：航线优化模型、气候融合模型、海况风险评估模型、燃油消耗预测模型、ETA预测模型

七、优化建议
------------
1. 推荐当前推荐航线 A1，综合能效与风险表现最佳
2. 关注强风大浪区域，建议巡航阶段保持安全距离
3. 优化航速可进一步节油，预计节省燃油 2.3 吨

==================
报告结束
  `.trim()

  const blob = new Blob([reportContent], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `航线优化报告_${new Date().toLocaleDateString('zh-CN').replace(/\//g, '-')}.txt`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// ── 分享功能 ──
const shareToWechat = () => {
  const shareText = `航线优化智能体报告 - 最优航线：A1\n起点：上海港 | 终点：那霸港\n航程：1,468km | 时间：78.6小时\n节油率：12.4% | 风险：低`
  navigator.clipboard.writeText(shareText).then(() => {
    alert('已复制分享内容到剪贴板，请打开微信粘贴分享')
  }).catch(() => {
    alert('分享内容：\n' + shareText)
  })
  showShareModal.value = false
}

const shareToQQ = () => {
  const shareText = encodeURIComponent(`航线优化智能体报告 - 最优航线：A1\n起点：上海港 | 终点：那霸港\n航程：1,468km | 时间：78.6小时\n节油率：12.4% | 风险：低`)
  const url = `http://connect.qq.com/widget/shareqq/index.html?url=${shareText}&title=航线优化报告&summary=航线优化智能体分析报告`
  window.open(url, '_blank')
  showShareModal.value = false
}

// ── GSAP 入场动画 ──
onMounted(() => {
  setTimeout(() => {
    initRouteMap()
  }, 100)

  const tl = gsap.timeline({ defaults: { ease: 'power2.out' } })

  tl.from('.agent-search-metrics .metric-card', {
    y: 20, opacity: 0, duration: 0.6, stagger: 0.08,
  })

  tl.from('.page-hero', {
    y: 16, opacity: 0, duration: 0.5, ease: 'power3.out',
  }, '-=0.3')

  tl.from('.route-main-area > .panel', {
    x: -30, opacity: 0, duration: 0.5, stagger: 0.1,
  }, '-=0.3')

  tl.from('.route-aside > *', {
    y: 20, opacity: 0, duration: 0.5, stagger: 0.1,
  }, '-=0.3')
})

onUnmounted(() => { if (chatAbortController) chatAbortController.abort() })
</script>

<template>
  <section class="page agent-search-page min-w-0">
    <!-- 指标卡片 -->
    <div class="metrics-grid agent-search-metrics min-w-0">
      <MetricCard v-for="metric in metrics" :key="metric.label" :metric="metric" />
    </div>

    <!-- 主体布局 -->
    <div class="agent-search-layout min-w-0">
      <div class="agent-search-main min-w-0">
        <!-- 页面头部 -->
        <div class="page-hero">
          <div class="page-hero-icon"><ShipWheel :size="28" /></div>
          <div class="page-hero-text">
            <h1>航线优化智能体</h1>
            <p>面向船舶航线规划、气象海况融合分析、风险规避与能效优化的智能体</p>
          </div>
          <div class="page-hero-meta">
            <span class="meta-badge"><Navigation :size="14" /> 航线规划</span>
          </div>
          <div class="page-actions">
            <button @click="openChat"><Bot :size="17" />智能问答</button>
            <button @click="generateReport"><FileText :size="17" />报告生成</button>
            <button @click="showShareModal = true"><Share2 :size="17" />分享</button>
          </div>
        </div>

        <!-- 航线地图 + 关键指标 -->
        <div class="route-main-area">
          <section class="panel ocean-map route-map">
            <header class="panel-header">
              <h2>航线优化地图</h2>
              <div class="tabs">
                <button class="active">航线视图</button>
              </div>
            </header>
            <div class="map-wrapper">
              <div id="route-leaflet-map" class="real-route-map leaflet-map-base"></div>
              <OceanCurrent size="small" />
            </div>
            <!-- 航线图例 -->
            <div class="route-legend">
              <span class="legend-item"><i class="legend-line legend-a1"></i> A1 最优</span>
              <span class="legend-item"><i class="legend-line legend-a2"></i> A2 备选</span>
              <span class="legend-item"><i class="legend-line legend-a3"></i> A3 备选</span>
              <span class="legend-item"><i class="legend-dot legend-danger"></i> 高风险</span>
              <span class="legend-item"><i class="legend-dot legend-warn"></i> 中风险</span>
              <span class="legend-item"><i class="legend-dot legend-port"></i> 港口</span>
            </div>
          </section>

          <section class="panel micro-panel">
            <header class="panel-header">
              <h2>关键航线指标</h2>
              <div class="tabs"><button>24小时</button></div>
            </header>
            <div class="micro-grid">
              <article
                v-for="(item, index) in routeMetrics"
                :key="item"
                :class="`tone-${['green','blue','violet','cyan','teal','violet'][index]} metric-item-hover`"
              >
                <span>{{ item }}</span>
                <strong>{{ routeMetricValues[index] }} <small>{{ routeMetricUnits[index] }}</small></strong>
                <small class="trend">{{ index === 2 ? '↑ 0.2' : '↓ 0.8' }}</small>
                <svg viewBox="0 0 100 28" preserveAspectRatio="none">
                  <polyline points="0,18 12,15 25,12 38,13 52,19 68,15 84,16 100,13" />
                </svg>
                <div class="metric-tooltip">
                  <strong>{{ item }}</strong>
                  <p>当前值: {{ routeMetricValues[index] }} {{ routeMetricUnits[index] }}</p>
                  <p>{{ routeMetricDetails[index] }}</p>
                </div>
              </article>
            </div>
          </section>

          <section class="panel detail-table compact">
            <header class="panel-header"><h2>航线方案对比</h2></header>
            <table>
              <thead>
                <tr>
                  <th>方案</th><th>航程</th><th>时间</th><th>燃油</th><th>节油率</th><th>风险</th><th>评分</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(row, index) in plans"
                  :key="row[0]"
                  :class="{ 'optimal-row': index === 0 }"
                  style="cursor:pointer"
                >
                  <td>
                    <span v-if="index === 0" class="optimal-tag">★ {{ row[0] }}</span>
                    <span v-else>{{ row[0] }}</span>
                  </td>
                  <td>{{ row[1] }} <small class="unit">km</small></td>
                  <td>{{ row[2] }} <small class="unit">h</small></td>
                  <td>{{ row[3] }} <small class="unit">吨</small></td>
                  <td>
                    <span v-if="index === 0" class="highlight-value">{{ row[4] }}</span>
                    <span v-else>{{ row[4] }}</span>
                  </td>
                  <td><span :class="['risk-badge', 'risk-' + row[5]]">{{ row[5] }}</span></td>
                  <td>
                    <span v-if="index === 0" class="star-rating best">{{ row[6] }}</span>
                    <span v-else>{{ row[6] }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </section>

          <section class="panel qa-advice-panel">
            <header class="panel-header"><h2>智能优化建议</h2></header>
            <article><Navigation :size="18" /><span>推荐当前推荐航线 A1，综合能效与风险表现最佳。</span></article>
            <article><AlertTriangle :size="18" /><span>关注强风大浪区域，建议巡航阶段保持安全距离。</span></article>
            <article><Fuel :size="18" /><span>优化航速可进一步节油，预计节省燃油 2.3 吨。</span></article>
          </section>
        </div>
      </div>

      <!-- 侧边栏 -->
      <aside class="agent-search-aside route-aside min-w-0">
        <section class="panel side-feed-panel">
          <header class="panel-header">
            <h2>数据来源</h2>
            <button class="more-btn" @click="showDataSourceModal = true">更多 ›</button>
          </header>
          <ul>
            <li
              v-for="source in allDataSources.slice(0, 5)"
              :key="source.name"
              :class="['source-link', { 'clicked': isSourceClicked(source.name) }]"
              @click="clickDataSource(source)"
            >
              {{ source.name }} <span>正常</span>
            </li>
          </ul>
        </section>

        <section class="panel side-feed-panel">
          <header class="panel-header"><h2>模型运行状态</h2></header>
          <ul>
            <li v-for="model in modelStatuses" :key="model">{{ model }} <span>运行中</span></li>
          </ul>
        </section>

        <section class="panel trend-panel">
          <header class="panel-header">
            <h2>趋势预测</h2>
            <div class="tabs"><button>24小时</button></div>
          </header>
          <div class="line-chart">
            <svg viewBox="0 0 100 45" preserveAspectRatio="none" class="trend-svg">
              <polyline class="trend-line line1" points="0,26 10,23 20,17 30,18 40,22 50,16 60,20 70,14 80,19 90,16 100,21" />
              <polyline class="trend-line line2" points="0,18 10,16 20,12 30,13 40,17 50,10 60,11 70,17 80,20 90,14 100,16" />
              <g class="trend-points" v-for="n in 11" :key="n">
                <circle :cx="(n-1) * 10" :cy="n === 1 ? 26 : n === 2 ? 23 : n === 3 ? 17 : n === 4 ? 18 : n === 5 ? 22 : n === 6 ? 16 : n === 7 ? 20 : n === 8 ? 14 : n === 9 ? 19 : n === 10 ? 16 : 21" r="2" class="trend-dot dot1" />
                <circle :cx="(n-1) * 10" :cy="n === 1 ? 18 : n === 2 ? 16 : n === 3 ? 12 : n === 4 ? 13 : n === 5 ? 17 : n === 6 ? 10 : n === 7 ? 11 : n === 8 ? 17 : n === 9 ? 20 : n === 10 ? 14 : 16" r="2" class="trend-dot dot2" />
              </g>
            </svg>
            <div class="trend-tooltip">
              <strong>燃油消耗趋势</strong>
              <p>当前: 203.6 吨</p>
              <p>预测: 198.3 吨</p>
            </div>
          </div>
        </section>

        <section class="panel detail-table compact">
          <header class="panel-header"><h2>航段风险列表</h2></header>
          <table>
            <tbody>
              <tr v-for="risk in segmentRisks" :key="risk.segment">
                <td>
                  <span :class="`risk-segment level-${risk.level}`">{{ risk.segment }}</span>
                  {{ risk.risk }}
                </td>
                <td>{{ risk.time }}</td>
              </tr>
            </tbody>
          </table>
        </section>
      </aside>
    </div>

    <!-- 数据来源弹窗 -->
    <AppModal v-model:visible="showDataSourceModal" title="全部数据来源" width="420px">
      <ul class="modal-source-list">
        <li
          v-for="source in allDataSources"
          :key="source.name"
          :class="['source-link', { 'clicked': isSourceClicked(source.name) }]"
          @click="clickDataSource(source)"
        >
          {{ source.name }} <span>›</span>
        </li>
      </ul>
    </AppModal>

    <!-- 智能问答弹窗 -->
    <Teleport to="body">
      <div v-if="showChatModal" class="modal-overlay chat-overlay" @click.self="showChatModal = false">
        <div class="modal-content chat-modal">
          <div class="modal-header">
            <h3><Bot :size="20" /> 航线优化智能体</h3>
            <div style="display:flex;gap:8px;align-items:center;">
              <button class="modal-close" @click="clearChat" title="清空对话"><Trash2 :size="14" /></button>
              <button class="modal-close" @click="showChatModal = false">&times;</button>
            </div>
          </div>
          <div class="chat-body">
            <div ref="chatMessagesEl" class="chat-messages">
              <div
                v-for="(msg, index) in chatMessages"
                :key="index"
                :class="['chat-message', msg.role]"
              >
                <div class="message-avatar">
                  <User v-if="msg.role === 'user'" :size="16" />
                  <Bot v-else :size="16" />
                </div>
                <div v-if="msg.role === 'user'" class="message-content">{{ msg.text }}</div>
                <div v-else-if="msg.text" class="message-content md-content" v-html="renderMarkdown(msg.text)"></div>
                <div v-else-if="msg.status" class="message-content loading">
                  <LoaderCircle :size="16" class="spinner" /> {{ msg.status }}
                </div>
              </div>
            </div>
            <div class="chat-input-area">
              <input
                type="text"
                v-model="chatInput"
                placeholder="输入您的问题..."
                @keyup.enter="sendChatMessage"
                :disabled="isLoading"
              />
              <button @click="sendChatMessage" :disabled="isLoading || !chatInput.trim()">
                <Send :size="18" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 分享弹窗 -->
    <AppModal v-model:visible="showShareModal" title="分享到" width="360px">
      <div class="share-buttons">
        <button class="share-btn wechat" @click="shareToWechat">
          <Share :size="20" />
          <span>微信</span>
        </button>
        <button class="share-btn qq" @click="shareToQQ">
          <Forward :size="20" />
          <span>QQ</span>
        </button>
      </div>
    </AppModal>
  </section>
</template>

<style scoped>
/* ── 航线主页特定样式 ── */
.route-main-area.route-main-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.route-aside.route-aside {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 航线发光效果 */
:deep(.route-glow-line) {
  filter: drop-shadow(0 0 6px rgba(34, 197, 94, .8)) drop-shadow(0 0 14px rgba(34, 197, 94, .4));
}

/* 港口标注 */
:deep(.port-label) {
  background: rgba(5, 24, 48, .88);
  border: 1px solid rgba(59, 130, 246, .7);
  color: #fff;
  border-radius: 6px;
  padding: 3px 8px;
  box-shadow: 0 0 12px rgba(59, 130, 246, .3);
  font-size: 12px;
  font-weight: 600;
}
:deep(.port-label-small) {
  background: rgba(5, 24, 48, .8);
  border: 1px solid rgba(59, 130, 246, .4);
  color: #b9d6ee;
  border-radius: 4px;
  padding: 1px 5px;
  font-size: 10px;
}

/* 城市标注 */
:deep(.city-label) {
  background: rgba(5, 24, 48, .85);
  border: 1px solid rgba(34, 197, 94, .6);
  color: #fff;
  border-radius: 5px;
  padding: 2px 6px;
  font-size: 11px;
  box-shadow: 0 0 8px rgba(34, 197, 94, .2);
}
:deep(.ref-city-label) {
  background: rgba(5, 24, 48, .7);
  border: 1px solid rgba(255, 255, 255, .15);
  color: rgba(255, 255, 255, .6);
  border-radius: 4px;
  padding: 1px 5px;
  font-size: 10px;
}

/* ── 航线图例 ── */
.route-legend {
  display: flex;
  gap: 16px;
  padding: 8px 12px;
  font-size: 12px;
  color: #b9d6ee;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.legend-line {
  display: inline-block;
  width: 18px;
  height: 3px;
  border-radius: 2px;
}
.legend-a1 { background: #22c55e; }
.legend-a2 { background: #6b7280; opacity: .7; }
.legend-a3 { background: #ec4899; opacity: .7; }
.legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.legend-danger { background: #ef4444; }
.legend-warn { background: #f59e0b; }
.legend-port { background: #3b82f6; }

/* ── 指标悬浮 ── */
.metric-item-hover {
  position: relative;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.metric-item-hover:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border-color: rgba(72, 151, 232, 0.5);
}
.metric-tooltip {
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%) translateY(10px);
  background: rgba(6, 28, 54, 0.95);
  color: #dff7ff;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  z-index: 100;
  pointer-events: none;
  border: 1px solid rgba(92, 171, 255, 0.4);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}
.metric-tooltip strong { display: block; margin-bottom: 6px; color: #60a5fa; font-size: 13px; }
.metric-tooltip p { margin: 3px 0; color: #b9d4ea; font-size: 11px; }
.metric-item-hover:hover .metric-tooltip { opacity: 1; visibility: visible; transform: translateX(-50%) translateY(0); }
.metric-item-hover .metric-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 8px solid transparent;
  border-top-color: rgba(6, 28, 54, 0.95);
}

/* ── 趋势图 ── */
.line-chart { position: relative; }
.trend-svg { cursor: crosshair; }
.trend-line { transition: stroke-width 0.2s ease, filter 0.2s ease; }
.trend-line.line1 { fill: none; stroke: #3b82f6; stroke-width: 2; }
.trend-line.line2 { fill: none; stroke: #22c55e; stroke-width: 2; }
.line-chart:hover .trend-line.line1 { stroke-width: 3; filter: drop-shadow(0 0 4px rgba(59, 130, 246, 0.6)); }
.line-chart:hover .trend-line.line2 { stroke-width: 3; filter: drop-shadow(0 0 4px rgba(34, 197, 94, 0.6)); }
.trend-dot { fill: #fff; stroke-width: 1.5; opacity: 0; transition: opacity 0.2s ease, r 0.2s ease; }
.trend-dot.dot1 { stroke: #3b82f6; }
.trend-dot.dot2 { stroke: #22c55e; }
.line-chart:hover .trend-dot { opacity: 1; }
.line-chart:hover .trend-dot.dot1 { fill: #3b82f6; }
.line-chart:hover .trend-dot.dot2 { fill: #22c55e; }
.trend-tooltip {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(6, 28, 54, 0.95);
  color: #dff7ff;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 12px;
  white-space: nowrap;
  opacity: 0;
  visibility: hidden;
  transition: all 0.2s ease;
  z-index: 10;
  pointer-events: none;
  border: 1px solid rgba(92, 171, 255, 0.4);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}
.line-chart:hover .trend-tooltip { opacity: 1; visibility: visible; }
.trend-tooltip strong { display: block; margin-bottom: 6px; color: #60a5fa; font-size: 13px; }
.trend-tooltip p { margin: 3px 0; color: #b9d4ea; font-size: 11px; }

/* ── 表格行样式 ── */
.optimal-row { background: rgba(34, 197, 94, 0.15) !important; border-left: 3px solid #22c55e; }
.optimal-row:hover { background: rgba(34, 197, 94, 0.25) !important; }
.optimal-tag { color: #22c55e; font-weight: bold; }
.highlight-value { color: #22c55e; font-weight: bold; }
.star-rating.best { color: #fbbf24; text-shadow: 0 0 8px rgba(251, 191, 36, 0.5); }
.risk-badge { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }
.risk-badge.risk-低 { background: rgba(34, 197, 94, 0.2); color: #4ade80; }
.risk-badge.risk-中 { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.risk-badge.risk-高 { background: rgba(239, 68, 68, 0.2); color: #ff6b6b; }
.unit { color: #6b7280; font-size: 10px; }
.risk-segment { display: inline-block; padding: 2px 8px; border-radius: 4px; font-weight: bold; margin-right: 8px; font-size: 12px; }
.risk-segment.level-高 { background: rgba(239, 68, 68, 0.3); color: #ff6b6b; }
.risk-segment.level-中 { background: rgba(245, 158, 11, 0.3); color: #fbbf24; }
.risk-segment.level-低 { background: rgba(34, 197, 94, 0.3); color: #4ade80; }
.detail-table tbody tr:hover { background: rgba(59, 130, 246, 0.1); }

/* ── 数据来源链接 ── */
.source-link { cursor: pointer; transition: color 0.2s; }
.source-link:hover { color: #60a5fa; }
.source-link.clicked { color: #6b9cc0 !important; }
.source-link.clicked span { color: #6b9cc0 !important; }
.more-btn {
  border: 0;
  color: #52b8ff;
  background: transparent;
  cursor: pointer;
  padding: 2px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}
.more-btn:hover { background: rgba(82, 184, 255, 0.1); }

/* ── 数据来源列表 ── */
.modal-source-list { list-style: none; margin: 0; padding: 12px 16px; }
.modal-source-list li {
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-source-list li:hover { background: rgba(59, 130, 246, 0.15); }
.modal-source-list li.clicked { color: #6b9cc0; }
.modal-source-list li.clicked span { color: #6b9cc0; }
.modal-source-list li span { color: #52b8ff; }

/* ── 聊天弹窗 ── */
.chat-overlay {
  align-items: flex-end;
  justify-content: flex-end;
  padding: 20px;
}
.chat-modal {
  width: 420px;
  height: 580px;
  max-width: 100%;
  max-height: 100%;
  display: flex;
  flex-direction: column;
}
.chat-body { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.chat-message { display: flex; gap: 10px; max-width: 85%; }
.chat-message.user { flex-direction: row-reverse; align-self: flex-end; }
.chat-message.assistant { align-self: flex-start; }
.message-avatar {
  width: 32px; height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.chat-message.user .message-avatar { background: #3b82f6; color: white; }
.chat-message.assistant .message-avatar { background: #22c55e; color: white; }
.message-content {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.5;
  word-break: break-word;
}
.chat-message.user .message-content { background: #3b82f6; color: white; border-bottom-right-radius: 4px; }
.chat-message.assistant .message-content { background: rgba(8, 38, 72, 0.8); color: #dff7ff; border-bottom-left-radius: 4px; }
.message-content.loading { display: flex; align-items: center; gap: 8px; }
.spinner { animation: spin 1s linear infinite; }
@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
.chat-input-area {
  display: flex;
  gap: 10px;
  padding: 16px;
  border-top: 1px solid rgba(92, 171, 255, 0.2);
  background: rgba(6, 28, 54, 0.5);
}
.chat-input-area input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid rgba(75, 143, 210, 0.42);
  border-radius: 20px;
  background: rgba(5, 28, 55, 0.8);
  color: #d9efff;
  font-size: 13px;
  outline: none;
}
.chat-input-area input:focus { border-color: rgba(75, 143, 210, 0.7); }
.chat-input-area input::placeholder { color: #6b8aa8; }
.chat-input-area button {
  width: 40px; height: 40px;
  border: none;
  border-radius: 50%;
  background: #3b82f6;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.chat-input-area button:hover:not(:disabled) { background: #2563eb; }
.chat-input-area button:disabled { background: #6b7280; cursor: not-allowed; }

/* ── 聊天 Markdown 渲染 ── */
.chat-message .md-content { overflow-wrap: break-word; word-break: break-word; }
.chat-message .md-content p { margin: 0 0 0.5em; }
.chat-message .md-content p:last-child { margin-bottom: 0; }
.chat-message .md-content ul, .chat-message .md-content ol { margin: 0.3em 0; padding-left: 1.2em; }
.chat-message .md-content li { margin: 0.15em 0; }
.chat-message .md-content code { padding: 1px 4px; border-radius: 3px; background: rgba(35, 137, 255, 0.12); color: #8ec8ff; font-size: 0.9em; }
.chat-message .md-content pre { margin: 0.4em 0; padding: 8px 10px; border-radius: 6px; background: rgba(5, 18, 38, 0.9); overflow-x: auto; }
.chat-message .md-content pre code { padding: 0; background: none; color: #c8dff5; }
.chat-message .md-content strong { color: #e8f4ff; }
.chat-message .md-content table { border-collapse: collapse; margin: 0.4em 0; width: 100%; }
.chat-message .md-content th, .chat-message .md-content td { padding: 4px 8px; border: 1px solid rgba(75, 143, 210, 0.25); text-align: left; font-size: 12px; }
.chat-message .md-content th { background: rgba(35, 137, 255, 0.1); }

/* ── 分享弹窗 ── */
.share-buttons {
  display: flex;
  justify-content: center;
  gap: 30px;
  padding: 24px 20px;
}
.share-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  background: none;
  border: none;
  cursor: pointer;
  transition: transform 0.2s;
}
.share-btn:hover { transform: scale(1.1); }
.share-btn svg,
.share-btn :deep(svg) {
  width: 20px; height: 20px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.08);
  padding: 12px;
  box-sizing: content-box;
}
.share-btn span { font-size: 13px; color: #b9d4ea; }
.share-btn.wechat:hover svg,
.share-btn.wechat:hover :deep(svg) { background: rgba(7, 193, 96, 0.2); color: #07C160; }
.share-btn.qq:hover svg,
.share-btn.qq:hover :deep(svg) { background: rgba(18, 183, 245, 0.2); color: #12B7F5; }

/* ── 响应式 ── */
@media (max-width: 768px) {
  .chat-modal { width: 100%; height: 70vh; }
}
</style>
