<script setup>
import { ref, onMounted } from 'vue'
import { AlertTriangle, Bot, FileText, Fuel, Navigation, Share2, ShipWheel, Send, X, User, Loader2 } from 'lucide-vue-next'
import MetricCard from '../components/MetricCard.vue'

// 扣子 API 配置

const metrics = [
  { label: '当前推荐航线', value: 'A1 航线', trend: '推荐中', tone: 'blue', sparkline: [15, 18, 23, 28, 35, 42, 50, 58, 64, 71, 77, 83] },
  { label: '预计航行时间', value: '78.6 小时', trend: '6.9%', tone: 'amber', sparkline: [46, 42, 38, 36, 35, 33, 31, 30, 29, 27, 26, 24] },
  { label: '省油率', value: '12.4%', trend: '28.7吨', tone: 'teal', sparkline: [20, 24, 23, 29, 32, 31, 36, 38, 39, 42, 45, 48] },
  { label: '高风险海域', value: '2 处', trend: '1处', tone: 'amber', sparkline: [38, 34, 30, 26, 22, 20, 18, 17, 16, 15, 14, 13] },
]

const plans = [
  ['A1 (推荐)', '1,468', '78.6', '203.6', '12.4%', '低', '★★★★★'],
  ['A2 (备选)', '1,586', '84.2', '226.8', '4.6%', '中', '★★★★☆'],
  ['A3 (备选)', '1,634', '87.5', '238.9', '1.1%', '高', '★★★☆☆'],
]

const routeMetrics = ['风速', '浪高', '海流速度', '能见度', '预计燃油消耗', 'ETA 偏差']
const routeMetricValues = ['8.6', '2.1', '1.2', '9.6', '203.6', '-1.3']
const routeMetricUnits = ['m/s', 'm', 'kn', 'km', '吨', '%']
const routeMetricDetails = [
  '当前区域平均风速 8.6m/s，建议关注',
  '当前海浪高度 2.1m，航行平稳',
  '海流速度 1.2 节，有利于航行',
  '能见度 9.6km，天气良好',
  '预计消耗燃油 203.6 吨',
  '预计到达时间偏差 -1.3 小时'
]

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
  '航线优化模型',
  '气候融合模型',
  '海况风险评估模型',
  '燃油消耗预测模型',
  'ETA 预测模型'
]

const segmentRisks = [
  { segment: 'S1', risk: '强风大浪', level: '高', time: '05-24 14:00 - 20:00' },
  { segment: 'S2', risk: '对流天气', level: '中', time: '05-24 20:00 - 05-25 02:00' },
  { segment: 'S3', risk: '海流强', level: '中', time: '05-25 02:00 - 08:00' },
  { segment: 'S4', risk: '能见度低', level: '低', time: '05-25 08:00 - 14:00' },
  { segment: 'S5', risk: '适航风险', level: '低', time: '05-25 14:00 - 20:00' },
]

// 弹窗控制
const showDataSourceModal = ref(false)
const showChatModal = ref(false)
const showShareModal = ref(false)
const clickedSources = ref(new Set())

// 聊天相关
const chatMessages = ref([])
const chatInput = ref('')
const isLoading = ref(false)
const conversationId = ref('')

// 初始化聊天
const initChat = () => {
  chatMessages.value = [
    { role: 'assistant', content: '您好！我是航线优化智能体助手。请问有什么可以帮助您的？' }
  ]
  conversationId.value = ''
}

// 打开智能问答弹窗
const openChat = () => {
  showChatModal.value = true
  initChat()
}

// 发送消息到扣子
const sendToCoze = async (message) => {
  isLoading.value = true
  
  try {
    // 使用后端代理调用扣子API
    const response = await fetch('/api/coze/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: message,
        conversation_id: conversationId.value || null
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      if (data.conversation_id) {
        conversationId.value = data.conversation_id
      }
      chatMessages.value.push({
        role: 'assistant',
        content: data.message
      })
    } else {
      chatMessages.value.push({
        role: 'assistant',
        content: data.message || '抱歉，智能体暂时无法回复，请稍后再试。'
      })
    }
  } catch (error) {
    console.error('Coze API error:', error)
    chatMessages.value.push({
      role: 'assistant',
      content: '抱歉，连接智能体时出现问题，请检查网络后重试。'
    })
  } finally {
    isLoading.value = false
  }
}

// 发送消息
const sendMessage = async () => {
  if (!chatInput.value.trim() || isLoading.value) return
  
  const userMessage = chatInput.value.trim()
  chatMessages.value.push({ role: 'user', content: userMessage })
  chatInput.value = ''
  
  await sendToCoze(userMessage)
}

// 点击数据来源
const clickDataSource = (source) => {
  if (source.url) {
    window.open(source.url, '_blank')
    clickedSources.value.add(source.name)
    clickedSources.value = new Set(clickedSources.value)
  }
}

const isSourceClicked = (name) => {
  return clickedSources.value.has(name)
}

// 综合视图跳转
const goToMapView = () => {
  window.open('https://www.openstreetmap.org/export/embed.html?bbox=115,20,130,35&layer=mapnik', '_blank')
}

// 生成报告
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
  `
  
  // 创建 Blob 并生成下载
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

// 分享功能
const shareToWechat = () => {
  // 复制分享内容到剪贴板
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
</script>

<template>
  <section class="page agent-detail-page">
    <div class="page-content">
      <div class="agent-detail-head">
        <div class="agent-orb route"><ShipWheel :size="34" /></div>
        <div><h1>航线优化智能体 <span>在线</span></h1><p>面向船舶航线规划、气象海况融合分析、风险规避与能效优化的智能体</p></div>
        <div class="page-actions">
          <button @click="openChat"><Bot :size="17" />智能问答</button>
          <button @click="generateReport"><FileText :size="17" />报告生成</button>
          <button @click="showShareModal = true"><Share2 :size="17" />分享</button>
        </div>
      </div>
      
      <!-- 顶部四个指标卡片 -->
      <div class="metrics-grid detail-metrics">
        <MetricCard 
          v-for="metric in metrics" 
          :key="metric.label" 
          :metric="metric"
          class="metric-card-hover"
        />
      </div>
      
      <div class="detail-grid route-grid">
        <!-- 航线优化地图 -->
        <section class="panel ocean-map route-map">
          <header class="panel-header">
            <h2>航线优化地图</h2>
            <div class="tabs">
              <button @click="goToMapView">
                <Navigation :size="14" /> 综合视图
              </button>
            </div>
          </header>
          <div class="map-surface route-surface">
            <!-- 城市标签 -->
            <span class="place p1">上海</span>
            <span class="place p2">宁波</span>
            <span class="place p3">台州</span>
            <span class="place p4">厦门</span>
            <span class="place p5">那霸</span>
            
            <!-- 航线 SVG -->
            <svg viewBox="0 0 100 60" preserveAspectRatio="none">
              <defs>
                <linearGradient id="routeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" style="stop-color:#22c55e;stop-opacity:1" />
                  <stop offset="50%" style="stop-color:#3b82f6;stop-opacity:1" />
                  <stop offset="100%" style="stop-color:#06b6d4;stop-opacity:1" />
                </linearGradient>
                <filter id="glowGreen">
                  <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>
              <polyline class="route-alt-2" points="28,22 30,36 44,42 60,46 78,50" />
              <polyline class="route-alt-2" points="18,12 34,18 48,22 61,25 77,31 90,40" />
              <polyline class="route-main route-optimal" points="18,12 27,20 38,24 50,34 63,40 76,48 88,52" />
              <g class="route-arrow">
                <polygon points="50,34 47,31 48,36" fill="#22c55e" />
                <polygon points="63,40 60,37 61,42" fill="#22c55e" />
                <polygon points="76,48 73,45 74,50" fill="#22c55e" />
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
              <span class="green">A1 最优</span>
              <span class="blue">A2 备选</span>
              <span class="route-alt-hint">A3 备选</span>
              <span class="red">高风险</span>
              <span class="amber">中风险</span>
            </div>
          </div>
        </section>
        
        <!-- 关键航线指标 -->
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
        
        <!-- 数据来源 -->
        <section class="panel side-feed-panel detail-side">
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
        
        <!-- 模型运行状态 -->
        <section class="panel side-feed-panel detail-side">
          <header class="panel-header">
            <h2>模型运行状态</h2>
          </header>
          <ul>
            <li v-for="model in modelStatuses" :key="model">{{ model }} <span>运行中</span></li>
          </ul>
        </section>
        
        <!-- 航线方案对比 -->
        <section class="panel detail-table">
          <header class="panel-header">
            <h2>航线方案对比</h2>
          </header>
          <table>
            <thead>
              <tr>
                <th>方案</th>
                <th>航行距离</th>
                <th>预计时间</th>
                <th>燃油消耗</th>
                <th>节油率</th>
                <th>风险等级</th>
                <th>综合评分</th>
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
                <td>
                  <span :class="['risk-badge', 'risk-' + row[5]]">{{ row[5] }}</span>
                </td>
                <td>
                  <span v-if="index === 0" class="star-rating best">{{ row[6] }}</span>
                  <span v-else>{{ row[6] }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </section>
        
        <!-- 趋势预测 -->
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
        
        <!-- 航段风险列表 -->
        <section class="panel detail-table compact">
          <header class="panel-header">
            <h2>航段风险列表</h2>
          </header>
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
        
        <!-- 智能优化建议 -->
        <section class="panel qa-advice-panel">
          <header class="panel-header"><h2>智能优化建议</h2></header>
          <article><Navigation :size="18" /><span>推荐当前推荐航线 A1，综合能效与风险表现最佳。</span></article>
          <article><AlertTriangle :size="18" /><span>关注强风大浪区域，建议巡航阶段保持安全距离。</span></article>
          <article><Fuel :size="18" /><span>优化航速可进一步节油，预计节省燃油 2.3 吨。</span></article>
        </section>
      </div>
    </div>
    
    <!-- 数据来源弹窗 -->
    <Teleport to="body">
      <div v-if="showDataSourceModal" class="modal-overlay" @click.self="showDataSourceModal = false">
        <div class="modal-content" style="width:420px;">
          <div class="modal-header">
            <h3>全部数据来源</h3>
            <button class="modal-close" @click="showDataSourceModal = false">×</button>
          </div>
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
        </div>
      </div>
    </Teleport>
    
    <!-- 智能问答弹窗 -->
    <Teleport to="body">
      <div v-if="showChatModal" class="modal-overlay chat-overlay" @click.self="showChatModal = false">
        <div class="modal-content chat-modal">
          <div class="modal-header">
            <h3><Bot :size="20" /> 航线优化智能体</h3>
            <button class="modal-close" @click="showChatModal = false">×</button>
          </div>
          <div class="chat-body">
            <div class="chat-messages">
              <div 
                v-for="(msg, index) in chatMessages" 
                :key="index"
                :class="['chat-message', msg.role]"
              >
                <div class="message-avatar">
                  <User v-if="msg.role === 'user'" :size="16" />
                  <Bot v-else :size="16" />
                </div>
                <div class="message-content">{{ msg.content }}</div>
              </div>
              <div v-if="isLoading" class="chat-message assistant">
                <div class="message-avatar"><Bot :size="16" /></div>
                <div class="message-content loading">
                  <Loader2 :size="16" class="spinner" /> 思考中...
                </div>
              </div>
            </div>
            <div class="chat-input-area">
              <input 
                type="text" 
                v-model="chatInput" 
                placeholder="输入您的问题..."
                @keyup.enter="sendMessage"
                :disabled="isLoading"
              />
              <button @click="sendMessage" :disabled="isLoading || !chatInput.trim()">
                <Send :size="18" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
    
    <!-- 分享弹窗 -->
    <Teleport to="body">
      <div v-if="showShareModal" class="modal-overlay" @click.self="showShareModal = false">
        <div class="modal-content share-modal">
          <div class="modal-header">
            <h3>分享到</h3>
            <button class="modal-close" @click="showShareModal = false">×</button>
          </div>
          <div class="share-buttons">
            <button class="share-btn wechat" @click="shareToWechat">
              <svg viewBox="0 0 24 24" width="32" height="32">
                <path fill="#07C160" d="M8.5 13.5a1 1 0 1 0 0-2 1 1 0 0 0 0 2zm5 0a1 1 0 1 0 0-2 1 1 0 0 0 0 2z"/>
                <path fill="#07C160" d="M12 2C6.48 2 2 6.03 2 11c0 2.76 1.36 5.22 3.5 6.83V20a1 1 0 0 0 1.55.83l2.22-1.33 1.73 1.5a1 1 0 0 0 1.55-.71l1.6-3.2 2.9 1.63a1 1 0 0 0 1.35-.19c.37.21.8.19 1.15-.05l.8-.6V20a1 1 0 0 0 1.55.83l2.22-1.33 1.73 1.5a1 1 0 0 0 1.55-.71V17.83C21.64 16.22 23 13.76 23 11c0-4.97-4.48-9-11-9z"/>
              </svg>
              <span>微信</span>
            </button>
            <button class="share-btn qq" @click="shareToQQ">
              <svg viewBox="0 0 24 24" width="32" height="32">
                <path fill="#12B7F5" d="M12.003 2c-2.265 0-6.29 1.307-6.29 7.325 0 1.62.465 3.645 1.488 5.74L5.32 17.21c-.21.44-.29.93-.22 1.42.18 1.33 1.41 2.37 2.78 2.37 1.18 0 2.22-.73 2.74-1.82l1.91 1.35c.27.19.59.29.92.29h.02c.41-.02.8-.14 1.14-.34l2.19-1.33c.21-.13.38-.32.51-.54.13.22.32.4.55.53l2.19 1.33c.34.2.73.32 1.14.34h.02c.33 0 .65-.1.92-.29l1.91-1.35c.52 1.09 1.56 1.82 2.74 1.82 1.37 0 2.6-1.04 2.78-2.37.07-.49-.01-.98-.22-1.42l-1.88-2.14c1.02-2.095 1.49-4.12 1.49-5.74 0-6.018-4.026-7.325-6.29-7.325-1.14 0-2.23.22-3.22.64.05-.21.08-.43.08-.65 0-2.21-2.53-4-5.65-4S.003 4.79.003 7c0 .22.03.44.08.65-.99-.42-2.08-.64-3.22-.64C2.52 7 0 8.79 0 11c0 3.03 2.52 5 5.65 5 .87 0 1.68-.17 2.42-.46-.15-.92-.14-2.07.04-3.33.08-.63.76-1.02 1.36-1.02.57 0 1.04.34 1.18.85.29 1.03.78 1.97 1.43 2.76.5.6 1.14 1.06 1.87 1.36-.29 1.37-.79 2.5-1.51 3.43-.56.72-1.23 1.25-2.01 1.61-.18.08-.36.15-.54.21-.17.06-.36.1-.56.13-.18.03-.39.05-.62.06-.24.02-.5.03-.79.03-.23 0-.47-.01-.7-.03-.23-.02-.44-.06-.65-.12-.21-.06-.41-.13-.6-.21-.19-.08-.38-.18-.55-.29-.17-.11-.34-.23-.5-.37-.16-.14-.31-.29-.45-.45-.14-.16-.27-.34-.39-.53-.12-.19-.22-.4-.31-.62-.09-.22-.16-.45-.21-.7-.05-.24-.08-.5-.08-.78 0-.26.02-.53.06-.8.04-.27.1-.54.18-.8.08-.26.18-.51.3-.75.12-.24.26-.47.42-.69.16-.22.34-.42.54-.61.2-.19.42-.36.66-.51.24-.15.5-.28.78-.39.28-.11.58-.2.9-.27.32-.07.66-.12 1.02-.15.36-.03.75-.05 1.16-.05s.8.02 1.16.05c.36.03.7.08 1.02.15.32.07.62.16.9.27.28.11.54.24.78.39.24.15.46.32.66.51.2.19.38.39.54.61.16.22.3.45.42.69.12.24.22.49.3.75.08.27.14.54.18.8.04.27.06.54.06.8 0 .28-.03.54-.08.78-.05.24-.12.48-.21.7-.09.22-.19.43-.31.62-.12.19-.25.37-.39.53-.14.16-.29.31-.45.45-.16.14-.33.26-.5.37-.17.11-.36.21-.55.29-.19.08-.39.15-.6.21-.21.06-.42.1-.65.12-.23.02-.47.03-.7.03-.3 0-.55-.01-.79-.03-.22-.01-.44-.03-.62-.06-.2-.03-.39-.07-.56-.13-.18-.06-.36-.13-.54-.21-.78-.36-1.45-.89-2.01-1.61-.72-.93-1.22-2.06-1.51-3.43.73-.3 1.37-.76 1.87-1.36.65-.79 1.14-1.73 1.43-2.76.14-.51.61-.85 1.18-.85.6 0 1.28.39 1.36 1.02.18 1.26.19 2.41.04 3.33.74.29 1.55.46 2.42.46 3.13 0 5.65-1.97 5.65-5 0-2.21-2.52-4-5.65-4z"/>
              </svg>
              <span>QQ</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </section>
</template>

<style scoped>
.agent-detail-page {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
}

.page-content {
  padding: 16px;
  min-height: 100%;
}

.metric-card-hover {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.metric-card-hover:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
}

.route-alt-hint {
  display: inline-flex;
  align-items: center;
}
.route-alt-hint::before {
  content: '';
  display: inline-block;
  width: 8px;
  height: 2px;
  margin-right: 6px;
  background: #ec4899;
  border-radius: 1px;
}

.route-legend-small {
  padding: 6px 8px !important;
  font-size: 10px !important;
  width: 90px !important;
  gap: 4px !important;
}
.route-legend-small strong {
  display: none;
}
.route-legend-small span {
  margin: 1px 0;
}

.optimal-label {
  position: absolute;
  left: 40%;
  top: 32%;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.4);
}
.optimal-label .route-name {
  font-size: 14px;
  font-weight: bold;
}
.optimal-label .route-tag-text {
  font-size: 9px;
  opacity: 0.9;
}

.route-optimal {
  stroke: #22c55e !important;
  stroke-width: 0.8 !important;
  filter: url(#glowGreen) !important;
}

.route-alt-2 {
  stroke: #6b7280;
  stroke-width: 0.3;
  fill: none;
  stroke-dasharray: 2,1;
  opacity: 0.5;
}

.map-legend .green {
  color: #22c55e !important;
  font-weight: bold;
}
.map-legend .green::before {
  background: #22c55e !important;
}

.optimal-row {
  background: rgba(34, 197, 94, 0.15) !important;
  border-left: 3px solid #22c55e;
}
.optimal-row:hover {
  background: rgba(34, 197, 94, 0.25) !important;
}
.optimal-tag {
  color: #22c55e;
  font-weight: bold;
}
.highlight-value {
  color: #22c55e;
  font-weight: bold;
}
.star-rating.best {
  color: #fbbf24;
  text-shadow: 0 0 8px rgba(251, 191, 36, 0.5);
}
.risk-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
}
.risk-badge.risk-低 {
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
}
.risk-badge.risk-中 {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
}
.risk-badge.risk-高 {
  background: rgba(239, 68, 68, 0.2);
  color: #ff6b6b;
}
.unit {
  color: #6b7280;
  font-size: 10px;
}

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
.metric-tooltip strong {
  display: block;
  margin-bottom: 6px;
  color: #60a5fa;
  font-size: 13px;
}
.metric-tooltip p {
  margin: 3px 0;
  color: #b9d4ea;
  font-size: 11px;
}
.metric-item-hover:hover .metric-tooltip {
  opacity: 1;
  visibility: visible;
  transform: translateX(-50%) translateY(0);
}
.metric-item-hover .metric-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 8px solid transparent;
  border-top-color: rgba(6, 28, 54, 0.95);
}

.source-link {
  cursor: pointer;
  transition: color 0.2s;
}
.source-link:hover {
  color: #60a5fa;
}
.source-link.clicked {
  color: #3b82f6 !important;
}
.source-link.clicked span {
  color: #3b82f6 !important;
}

.more-btn {
  border: 0;
  color: #52b8ff;
  background: transparent;
  cursor: pointer;
  padding: 2px 8px;
  border-radius: 4px;
  transition: all 0.2s;
}
.more-btn:hover {
  background: rgba(82, 184, 255, 0.1);
}

.risk-segment {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: bold;
  margin-right: 8px;
  font-size: 12px;
}
.risk-segment.level-高 {
  background: rgba(239, 68, 68, 0.3);
  color: #ff6b6b;
}
.risk-segment.level-中 {
  background: rgba(245, 158, 11, 0.3);
  color: #fbbf24;
}
.risk-segment.level-低 {
  background: rgba(34, 197, 94, 0.3);
  color: #4ade80;
}

.ocean-map .tabs button {
  min-height: 34px;
  border: 1px solid rgba(75, 143, 210, 0.42);
  border-radius: 7px;
  color: #d9efff;
  background: rgba(5, 28, 55, 0.8);
  padding: 0 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.ocean-map .tabs button:hover {
  background: rgba(20, 60, 100, 0.8);
  border-color: rgba(75, 143, 210, 0.6);
}

.micro-panel .tabs button,
.trend-panel .tabs button {
  min-height: 34px;
  border: 1px solid rgba(75, 143, 210, 0.42);
  border-radius: 7px;
  color: #d9efff;
  background: rgba(5, 28, 55, 0.8);
  padding: 0 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}
.micro-panel .tabs button:hover,
.trend-panel .tabs button:hover {
  background: rgba(20, 60, 100, 0.8);
  border-color: rgba(75, 143, 210, 0.6);
}

.line-chart {
  position: relative;
}
.trend-svg {
  cursor: crosshair;
}
.trend-line {
  transition: stroke-width 0.2s ease, filter 0.2s ease;
}
.trend-line.line1 {
  fill: none;
  stroke: #3b82f6;
  stroke-width: 2;
}
.trend-line.line2 {
  fill: none;
  stroke: #22c55e;
  stroke-width: 2;
}
.line-chart:hover .trend-line.line1 {
  stroke-width: 3;
  filter: drop-shadow(0 0 4px rgba(59, 130, 246, 0.6));
}
.line-chart:hover .trend-line.line2 {
  stroke-width: 3;
  filter: drop-shadow(0 0 4px rgba(34, 197, 94, 0.6));
}
.trend-dot {
  fill: #fff;
  stroke-width: 1.5;
  opacity: 0;
  transition: opacity 0.2s ease, r 0.2s ease;
}
.trend-dot.dot1 {
  stroke: #3b82f6;
}
.trend-dot.dot2 {
  stroke: #22c55e;
}
.line-chart:hover .trend-dot {
  opacity: 1;
}
.line-chart:hover .trend-dot.dot1 {
  fill: #3b82f6;
}
.line-chart:hover .trend-dot.dot2 {
  fill: #22c55e;
}
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
.line-chart:hover .trend-tooltip {
  opacity: 1;
  visibility: visible;
}
.trend-tooltip strong {
  display: block;
  margin-bottom: 6px;
  color: #60a5fa;
  font-size: 13px;
}
.trend-tooltip p {
  margin: 3px 0;
  color: #b9d4ea;
  font-size: 11px;
}

.detail-table tbody tr:hover {
  background: rgba(59, 130, 246, 0.1);
}

.agent-detail-page::-webkit-scrollbar {
  width: 8px;
}
.agent-detail-page::-webkit-scrollbar-track {
  background: rgba(6, 28, 54, 0.5);
  border-radius: 4px;
}
.agent-detail-page::-webkit-scrollbar-thumb {
  background: rgba(60, 154, 255, 0.4);
  border-radius: 4px;
}
.agent-detail-page::-webkit-scrollbar-thumb:hover {
  background: rgba(60, 154, 255, 0.6);
}

/* 弹窗通用样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
.modal-content {
  max-width: 90%;
  max-height: 80vh;
  background: linear-gradient(145deg, rgba(18, 73, 130, 0.95), rgba(5, 26, 51, 0.98));
  border: 1px solid rgba(60, 154, 255, 0.35);
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  animation: slideUp 0.3s ease;
}
@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(92, 171, 255, 0.25);
}
.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #dff7ff;
  display: flex;
  align-items: center;
  gap: 8px;
}
.modal-close {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 1px solid rgba(92, 171, 255, 0.4);
  background: rgba(6, 28, 54, 0.8);
  color: #b9d4ea;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.modal-close:hover {
  background: rgba(60, 154, 255, 0.3);
  color: #fff;
}
.modal-body {
  padding: 12px;
  max-height: 400px;
  overflow-y: auto;
}
.modal-source-list {
  list-style: none;
  margin: 0;
  padding: 12px 16px;
}
.modal-source-list li {
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-source-list li:hover {
  background: rgba(59, 130, 246, 0.15);
}
.modal-source-list li.clicked {
  color: #60a5fa;
}
.modal-source-list li.clicked span {
  color: #60a5fa;
}
.modal-source-list li span {
  color: #52b8ff;
}

.modal-footer {
  padding: 12px 20px;
  border-top: 1px solid rgba(92, 171, 255, 0.2);
  background: rgba(6, 28, 54, 0.5);
}
.modal-footer p {
  margin: 0;
  font-size: 12px;
  color: #9bbfe1;
}

/* 聊天弹窗样式 */
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
.chat-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.chat-message {
  display: flex;
  gap: 10px;
  max-width: 85%;
}
.chat-message.user {
  flex-direction: row-reverse;
  align-self: flex-end;
}
.chat-message.assistant {
  align-self: flex-start;
}
.message-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.chat-message.user .message-avatar {
  background: #3b82f6;
  color: white;
}
.chat-message.assistant .message-avatar {
  background: #22c55e;
  color: white;
}
.message-content {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.5;
  word-break: break-word;
}
.chat-message.user .message-content {
  background: #3b82f6;
  color: white;
  border-bottom-right-radius: 4px;
}
.chat-message.assistant .message-content {
  background: rgba(8, 38, 72, 0.8);
  color: #dff7ff;
  border-bottom-left-radius: 4px;
}
.message-content.loading {
  display: flex;
  align-items: center;
  gap: 8px;
}
.spinner {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
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
.chat-input-area input:focus {
  border-color: rgba(75, 143, 210, 0.7);
}
.chat-input-area input::placeholder {
  color: #6b8aa8;
}
.chat-input-area button {
  width: 40px;
  height: 40px;
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
.chat-input-area button:hover:not(:disabled) {
  background: #2563eb;
}
.chat-input-area button:disabled {
  background: #6b7280;
  cursor: not-allowed;
}

/* 分享弹窗样式 */
.share-modal {
  width: 320px;
}
.share-buttons {
  display: flex;
  justify-content: center;
  gap: 30px;
  padding: 30px 20px;
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
.share-btn:hover {
  transform: scale(1.1);
}
.share-btn svg {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.1);
  padding: 12px;
}
.share-btn span {
  font-size: 13px;
  color: #b9d4ea;
}
.share-btn.wechat:hover svg {
  background: rgba(7, 193, 96, 0.2);
}
.share-btn.qq:hover svg {
  background: rgba(18, 183, 245, 0.2);
}

@media (max-width: 1200px) {
  .detail-grid {
    grid-template-columns: 1fr 1fr;
  }
}
@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
  .metric-card-hover:hover {
    transform: none;
  }
  .chat-modal {
    width: 100%;
    height: 70vh;
  }
}
</style>
