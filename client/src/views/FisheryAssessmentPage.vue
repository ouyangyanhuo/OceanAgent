<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { Anchor, Bot, FileText, Fish, RadioTower, Settings, Share2, ShieldCheck, Database, Globe, Cloud } from 'lucide-vue-next'
import gsap from 'gsap'
import MetricCard from '../components/MetricCard.vue'
import AppModal from '../components/common/AppModal.vue'
import OceanCurrent from '../components/common/OceanCurrent.vue'
import { useSatelliteMap } from '../composables/useSatelliteMap'

const { L, addSatelliteBaseLayer } = useSatelliteMap()

const resetZoom = () => {
  if (!fullMap) return
  fullMap.setView([20, 30], 2)
}

const metrics = [
  { label: '综合适宜度', value: '86.3 /100', trend: '12.6%', tone: 'blue', sparkline: [18, 22, 21, 30, 26, 36, 32, 41, 37, 48, 42, 55] },
  { label: '优质渔场数量', value: '28 处', trend: '16.7%', tone: 'cyan', sparkline: [16, 21, 24, 22, 32, 29, 38, 35, 44, 40, 47, 56] },
  { label: '资源丰度指数', value: '134.7', trend: '11.5%', tone: 'teal', sparkline: [20, 25, 23, 31, 29, 37, 35, 44, 39, 51, 45, 58] },
  { label: '未来48小时作业窗口', value: '36 h', trend: '18.2%', tone: 'green', sparkline: [15, 20, 24, 29, 35, 41, 44, 43, 39, 34, 28, 22] },
]

const animatedMetrics = ref([
  { label: '综合适宜度', value: 0, suffix: ' /100', trend: '12.6%', tone: 'blue', target: 86.3, sparkline: [18, 22, 21, 30, 26, 36, 32, 41, 37, 48, 42, 55] },
  { label: '优质渔场数量', value: 0, suffix: ' 处', trend: '16.7%', tone: 'cyan', target: 28, sparkline: [16, 21, 24, 22, 32, 29, 38, 35, 44, 40, 47, 56] },
  { label: '资源丰度指数', value: 0, suffix: '', trend: '11.5%', tone: 'teal', target: 134.7, sparkline: [20, 25, 23, 31, 29, 37, 35, 44, 39, 51, 45, 58] },
  { label: '未来48小时作业窗口', value: 0, suffix: ' h', trend: '18.2%', tone: 'green', target: 36, sparkline: [15, 20, 24, 29, 35, 41, 44, 43, 39, 34, 28, 22] },
])

const animateMetrics = () => {
  animatedMetrics.value.forEach((item) => {
    const start = 0
    const end = item.target
    const duration = 1400
    const startTime = performance.now()

    const run = (now) => {
      const progress = Math.min((now - startTime) / duration, 1)
      const ease = 1 - Math.pow(1 - progress, 3)
      item.value = Number((start + (end - start) * ease).toFixed(end % 1 === 0 ? 0 : 1))

      if (progress < 1) requestAnimationFrame(run)
    }

    requestAnimationFrame(run)
  })
}

const today = new Date()
const mm = String(today.getMonth() + 1).padStart(2, '0')
const dd = String(today.getDate()).padStart(2, '0')
const dateTag = `${mm}-${dd}`

const ranking = [
  ['西沙北部渔场', '94.0', '162.8', '金枪鱼、飞鱼、鲣鱼', `${dateTag} 06:00 - 22:00`],
  ['文昌外海渔场', '91.0', '154.6', '金枪鱼、鲐鱼、马鲛鱼', `${dateTag} 07:00 - 23:00`],
  ['琼州海峡渔场', '86.0', '143.2', '马鲛鱼、鲳鱼、鲷鱼', `${dateTag} 06:30 - 21:30`],
  ['万宁近海渔场', '84.0', '136.5', '带鱼、鲷鱼、鲐鱼', `${dateTag} 08:00 - 22:00`],
  ['儋州近海渔场', '81.0', '128.7', '鲳鱼、马鲛鱼、金线鱼', `${dateTag} 07:30 - 20:30`],
]

const indicators = [
  {
    label: '表层水温',
    value: '28.4',
    unit: '℃',
    change: '+0.6℃',
    status: '偏暖',
    tone: 'blue',
    sparkline: '0,19 12,17 25,15 38,13 52,11 68,10 84,8 100,7'
  },
  {
    label: '叶绿素a',
    value: '1.72',
    unit: 'mg/m³',
    change: '+0.18',
    status: '浮游生物活跃',
    tone: 'teal',
    sparkline: '0,22 12,20 25,16 38,18 52,13 68,15 84,11 100,9'
  },
  {
    label: '盐度',
    value: '33.1',
    unit: '‰',
    change: '-0.2‰',
    status: '稳定',
    tone: 'cyan',
    sparkline: '0,12 12,13 25,12 38,14 52,13 68,12 84,13 100,12'
  },
  {
    label: '溶解氧',
    value: '6.48',
    unit: 'mg/L',
    change: '+0.31',
    status: '适宜',
    tone: 'green',
    sparkline: '0,21 12,19 25,17 38,14 52,16 68,12 84,10 100,8'
  },
  {
    label: '有效波高',
    value: '0.86',
    unit: 'm',
    change: '-0.14m',
    status: '作业友好',
    tone: 'violet',
    sparkline: '0,9 12,12 25,10 38,15 52,13 68,18 84,20 100,22'
  },
  {
    label: '生物量指数',
    value: '147.9',
    unit: '',
    change: '+12.7',
    status: '资源集聚',
    tone: 'amber',
    sparkline: '0,24 12,21 25,19 38,16 52,13 68,11 84,9 100,6'
  }
]
const sideSources = ['卫星遥感', '海洋浮标网', '渔船AIS', '渔获上报', '声学探测', '历史渔情库']

// 弹窗控制
const showMoreRanking = ref(false)
const showMoreModels = ref(false)
const showMoreFishTarget = ref(false)
const showMoreSources = ref(false)
const showMoreAdvice = ref(false)
const showReportDialog = ref(false)

// 报告配置
const reportConfig = ref({
  type: '渔场综合评估报告',
  timeRange: '近7天',
  format: 'PDF',
  includeCharts: true,
  includeData: true,
})

const isGenerating = ref(false)

const reportTypes = [
  '渔场综合评估报告', '资源丰度分析报告', '作业适宜性报告',
  '渔情预测周报', '渔场排行统计报告', '鱼种资源分析报告',
]

const timeRanges = ['近24小时', '近3天', '近7天', '近30天', '自定义']

const dateStr = `${today.getFullYear()}-${mm}-${dd}`

const fullRankingData = [
  { rank: 1, name: '西沙北部渔场', suitability: '94.0', abundance: '162.8', fish: '金枪鱼、飞鱼、鲣鱼', window: `${dateTag} 06:00 - 22:00` },
  { rank: 2, name: '文昌外海渔场', suitability: '91.0', abundance: '154.6', fish: '金枪鱼、鲐鱼、马鲛鱼', window: `${dateTag} 07:00 - 23:00` },
  { rank: 3, name: '琼州海峡渔场', suitability: '86.0', abundance: '143.2', fish: '马鲛鱼、鲳鱼、鲷鱼', window: `${dateTag} 06:30 - 21:30` },
  { rank: 4, name: '万宁近海渔场', suitability: '84.0', abundance: '136.5', fish: '带鱼、鲷鱼、鲐鱼', window: `${dateTag} 08:00 - 22:00` },
  { rank: 5, name: '儋州近海渔场', suitability: '81.0', abundance: '128.7', fish: '鲳鱼、马鲛鱼、金线鱼', window: `${dateTag} 07:30 - 20:30` },
  { rank: 6, name: '陵水渔场', suitability: '79.0', abundance: '119.4', fish: '石斑鱼、鲷鱼、鱿鱼', window: `${dateTag} 08:00 - 20:00` },
  { rank: 7, name: '三亚外海渔场', suitability: '76.0', abundance: '112.6', fish: '鱿鱼、鲭鱼、鲣鱼', window: `${dateTag} 09:00 - 20:00` },
  { rank: 8, name: '东方近海渔场', suitability: '72.0', abundance: '105.8', fish: '金线鱼、鲷鱼、马鲛鱼', window: `${dateTag} 09:30 - 19:00` },
  { rank: 9, name: '北部湾东缘渔场', suitability: '69.5', abundance: '98.4', fish: '带鱼、鲳鱼、鱿鱼', window: `${dateTag} 10:00 - 18:30` },
  { rank: 10, name: '南海北部近岸渔场', suitability: '66.8', abundance: '91.7', fish: '鲐鱼、鲷鱼、金线鱼', window: `${dateTag} 10:00 - 18:00` },
]

const modelDetails = [
  { name: '渔场适宜性评估模型', status: '运行中', accuracy: '94.2%', updateTime: `${dateStr} 01:00`, description: '基于多源卫星数据评估渔场适宜性' },
  { name: '资源丰度预测模型', status: '运行中', accuracy: '91.5%', updateTime: `${dateStr} 01:08`, description: '结合历史渔获与海洋环境预测资源量' },
  { name: '鱼群热点识别模型', status: '运行中', accuracy: '88.7%', updateTime: `${dateStr} 01:15`, description: 'AI识别鱼群聚集区域' },
  { name: '作业窗口研判模型', status: '运行中', accuracy: '93.1%', updateTime: `${dateStr} 01:23`, description: '综合气象海浪评估作业窗口' },
  { name: '渔情短期预测模型', status: '运行中', accuracy: '86.9%', updateTime: `${dateStr} 01:38`, description: '未来3-7天渔情趋势预测' },
  { name: '渔业资源评估模型', status: '待更新', accuracy: '79.2%', updateTime: `${dateStr} 01:52`, description: '渔业资源存量评估' },
]

const fishTargetDetails = [
  { name: '马鲛鱼', abundance: '168.4', trend: '+7.8%', proportion: '21%', habitat: '琼州海峡、文昌外海', bestSeason: '春夏季' },
  { name: '金枪鱼', abundance: '156.9', trend: '+6.5%', proportion: '19%', habitat: '文昌外海、西沙北部', bestSeason: '夏秋季' },
  { name: '鲳鱼', abundance: '142.3', trend: '+5.9%', proportion: '17%', habitat: '儋州近海、琼州海峡', bestSeason: '春秋季' },
  { name: '石斑鱼', abundance: '128.6', trend: '+4.7%', proportion: '14%', habitat: '陵水、三亚近岸礁区', bestSeason: '夏季' },
  { name: '鲷鱼', abundance: '119.8', trend: '+3.8%', proportion: '12%', habitat: '万宁、东方近海', bestSeason: '春夏季' },
  { name: '鱿鱼', abundance: '104.5', trend: '+2.9%', proportion: '9%', habitat: '三亚外海、西沙方向', bestSeason: '秋冬季' },
  { name: '金线鱼', abundance: '96.2', trend: '+2.1%', proportion: '6%', habitat: '东方近海、北部湾东缘', bestSeason: '夏秋季' },
  { name: '飞鱼', abundance: '82.7', trend: '+1.6%', proportion: '2%', habitat: '西沙北部外海', bestSeason: '夏季' },
]

const sourceDetails = [
  { name: '卫星遥感', status: '正常', delay: '实时', type: 'MODIS/Sentinel', coverage: '全域', updateFreq: '3小时' },
  { name: '海洋浮标网', status: '正常', delay: '15分钟', type: '物联网监测', coverage: '重点海域', updateFreq: '实时' },
  { name: '渔船AIS', status: '正常', delay: '5分钟', type: '船舶定位', coverage: '近海区域', updateFreq: '实时' },
  { name: '渔获上报', status: '正常', delay: '2小时', type: '智能终端', coverage: '渔港', updateFreq: '每日' },
  { name: '声学探测', status: '正常', delay: '4小时', type: '科学调查', coverage: '调查航次', updateFreq: '每周' },
  { name: '历史渔情库', status: '正常', delay: '3小时', type: '数据库', coverage: '2000-2025', updateFreq: '季度更新' },
  { name: '气象卫星', status: '正常', delay: '1小时', type: '风云卫星', coverage: '全海域', updateFreq: '每小时' },
  { name: '海浪预报', status: '正常', delay: '6小时', type: '数值预报', coverage: '中国近海', updateFreq: '每日2次' },
]

const adviceDetails = [
  { icon: 'Anchor', title: '最佳作业区域', content: '文昌外海与西沙北部渔场综合适宜度最高，水温、叶绿素a与资源丰度条件较优，建议作为优先作业海域。', priority: '高' },
  { icon: 'ShieldCheck', title: '作业时间窗口', content: '未来48小时内，海南东部海域以清晨至夜间前段为较优作业窗口，建议重点关注 06:00 - 22:00 时段。', priority: '高' },
  { icon: 'Fish', title: '目标鱼种选择', content: '马鲛鱼、金枪鱼、鲳鱼资源丰度较高，其中马鲛鱼主要集中在琼州海峡与文昌外海，金枪鱼更适合在西沙北部外海作业。', priority: '高' },
  { icon: 'RadioTower', title: '气象海况', content: '海南岛东部与南部近海整体海况较稳定，但三亚外海和西沙方向需持续关注风浪变化，避免强对流天气影响作业安全。', priority: '中' },
  { icon: 'Settings', title: '作业方式建议', content: '琼州海峡和儋州近海适合中小型渔船近海作业，文昌外海、西沙北部更适合具备远海作业能力的船只开展围网或钓捕作业。', priority: '中' },
  { icon: 'Database', title: '渔具选择', content: '针对马鲛鱼、鲳鱼可采用流刺网或围网作业；针对金枪鱼、飞鱼等外海鱼种，建议采用延绳钓、灯光诱捕等方式。', priority: '中' },
  { icon: 'Globe', title: '避风锚地', content: '海南周边可优先选择海口、洋浦、三亚、文昌清澜等港区作为补给与避风点，外海作业船只需提前规划返港路线。', priority: '低' },
  { icon: 'Cloud', title: '未来天气', content: '建议结合海南东部近岸、南部近海和西沙方向的分区预报动态调整作业计划，优先选择风力较小、浪高较低的时段出海。', priority: '中' },
]

const generateReport = () => {
  isGenerating.value = true
  setTimeout(() => {
    isGenerating.value = false
    showReportDialog.value = false
    alert(`报告已生成！\n类型：${reportConfig.value.type}\n时间范围：${reportConfig.value.timeRange}\n格式：${reportConfig.value.format}`)
  }, 1500)
}

// ── Leaflet 地图逻辑 ──

const hainanFishPoints = [
  { name: '琼州海峡渔场', lat: 20.15, lng: 110.25, score: 86, fish: '马鲛鱼、鲳鱼', level: '较高' },
  { name: '文昌外海渔场', lat: 19.75, lng: 111.25, score: 91, fish: '金枪鱼、鲐鱼', level: '极高' },
  { name: '万宁近海渔场', lat: 18.75, lng: 110.55, score: 84, fish: '带鱼、鲷鱼', level: '较高' },
  { name: '陵水渔场', lat: 18.45, lng: 109.95, score: 79, fish: '石斑鱼、鲷鱼', level: '较优' },
  { name: '三亚外海渔场', lat: 18.15, lng: 109.55, score: 76, fish: '鱿鱼、鲭鱼', level: '较优' },
  { name: '东方近海渔场', lat: 19.05, lng: 108.65, score: 72, fish: '金线鱼、鲷鱼', level: '低' },
  { name: '儋州近海渔场', lat: 19.75, lng: 109.15, score: 81, fish: '鲳鱼、马鲛鱼', level: '较高' },
  { name: '西沙北部渔场', lat: 16.85, lng: 112.35, score: 94, fish: '金枪鱼、飞鱼', level: '极高' },
]

const worldFishPoints = [
  { name: '纽芬兰渔场', lat: 47.5, lng: -52.8, type: '世界四大渔场' },
  { name: '北海道渔场', lat: 43.4, lng: 145.3, type: '世界四大渔场' },
  { name: '北海渔场', lat: 57.1, lng: 2.5, type: '世界四大渔场' },
  { name: '秘鲁渔场', lat: -12, lng: -77, type: '世界四大渔场' },
  { name: '舟山渔场', lat: 30.1, lng: 122.5, type: '中国近海重要渔场' },
  { name: '阿拉斯加渔场', lat: 58, lng: -160, type: '世界著名渔场' },
  { name: '白令海渔场', lat: 56, lng: -175, type: '世界著名渔场' },
  { name: '几内亚湾渔场', lat: 4, lng: 5, type: '世界著名渔场' },
  { name: '阿根廷外海渔场', lat: -45, lng: -60, type: '世界著名渔场' },
  { name: '澳大利亚西部渔场', lat: -28, lng: 114, type: '世界著名渔场' },
]

const activeFishPoint = ref(null)
const selectFishPoint = (point) => { activeFishPoint.value = point }

const showSuitabilityMap = ref(false)
const showFishLabels = ref(true)

let hainanMap = null
let fullMap = null
let hainanBigMarkers = []
let worldBigMarkers = []

const getLevelColor = (level) => {
  if (level === '极高') return '#ff3b30'
  if (level === '较高') return '#ffb331'
  if (level === '较优') return '#30e096'
  return '#1688ff'
}

const initHainanMap = () => {
  if (hainanMap) {
    hainanMap.remove()
    hainanMap = null
  }

  hainanMap = L.map('hainan-map', {
    zoomControl: false,
    attributionControl: false
  }).setView([19.2, 110.3], 7)

  addSatelliteBaseLayer(hainanMap)

  L.control.zoom({
    position: 'topleft'
  }).addTo(hainanMap)

  hainanFishPoints.forEach(point => {
    let color = '#1e9bff'
    if (point.level === '极高') color = '#ff3b30'
    else if (point.level === '较高') color = '#ffb331'
    else if (point.level === '较优') color = '#30e096'

    L.circleMarker(
      [point.lat, point.lng],
      {
        radius: 8,
        color: '#fff',
        weight: 2,
        fillColor: color,
        fillOpacity: 1
      }
    )
      .addTo(hainanMap)
      .bindPopup(`
        <b>${point.name}</b><br>
        适宜度：${point.score}/100<br>
        等级：${point.level}<br>
        鱼种：${point.fish}
      `)
  })
}

const openSuitabilityMap = () => {
  showSuitabilityMap.value = true
  nextTick(() => {
    initBigMap()
  })
}

const closeSuitabilityMap = () => {
  if (fullMap) {
    fullMap.remove()
    fullMap = null
  }
  hainanBigMarkers = []
  worldBigMarkers = []
  showSuitabilityMap.value = false
}

const toggleLabels = () => {
  showFishLabels.value = !showFishLabels.value
  const markers = [...hainanBigMarkers, ...worldBigMarkers]
  markers.forEach(marker => {
    if (showFishLabels.value) {
      marker.openTooltip()
    } else {
      marker.closeTooltip()
    }
  })
}

const initBigMap = () => {
  if (fullMap) {
    fullMap.remove()
    fullMap = null
  }

  hainanBigMarkers = []
  worldBigMarkers = []

  fullMap = L.map('big-world-map', {
    zoomControl: true,
    attributionControl: false,
    minZoom: 2,
    maxZoom: 10
  }).setView([20, 30], 2)

  addSatelliteBaseLayer(fullMap)

  hainanFishPoints.forEach(point => {
    const marker = L.circleMarker(
      [point.lat, point.lng],
      {
        radius: 10,
        fillColor: getLevelColor(point.level),
        color: '#fff',
        weight: 2,
        fillOpacity: 1,
        className: 'hainan-fish-marker'
      }
    )
      .addTo(fullMap)
      .bindPopup(`
        <b>${point.name}</b><br>
        适宜度：${point.score}/100<br>
        等级：${point.level}<br>
        鱼种：${point.fish}
      `)
      .bindTooltip(point.name, {
        permanent: true,
        direction: 'top',
        offset: [0, -10],
        className: 'fish-map-label hainan-label'
      })

    hainanBigMarkers.push(marker)
  })

  worldFishPoints.forEach(point => {
    const marker = L.circleMarker(
      [point.lat, point.lng],
      {
        radius: 8,
        fillColor: '#ff6b6b',
        color: '#fff',
        weight: 2,
        fillOpacity: 1,
        className: 'world-fish-marker'
      }
    )
      .addTo(fullMap)
      .bindPopup(`
        <b>${point.name}</b><br>
        ${point.type}
      `)
      .bindTooltip(point.name, {
        permanent: true,
        direction: 'top',
        offset: [0, -10],
        className: 'fish-map-label world-label'
      })

    worldBigMarkers.push(marker)
  })

  if (!showFishLabels.value) {
    ;[...hainanBigMarkers, ...worldBigMarkers].forEach(marker => marker.closeTooltip())
  }

  nextTick(() => {
    if (fullMap) fullMap.invalidateSize()
  })
}

// ── GSAP 入场动画 ──
onMounted(() => {
  animateMetrics()

  setTimeout(() => {
    initHainanMap()
  }, 100)

  const tl = gsap.timeline({ defaults: { ease: 'power2.out' } })

  tl.from('.page-hero', {
    y: 16, opacity: 0, duration: 0.5, ease: 'power3.out',
  })

  tl.from('.fishery-main-area > .panel', {
    x: -30, opacity: 0, duration: 0.5, stagger: 0.1,
  }, '-=0.3')

  tl.from('.fishery-aside > *', {
    y: 20, opacity: 0, duration: 0.5, stagger: 0.1,
  }, '-=0.3')
})
</script>

<template>
  <section class="page agent-search-page min-w-0">
    <!-- 指标卡片 -->
    <div class="metrics-grid agent-search-metrics min-w-0">
      <MetricCard
        v-for="metric in animatedMetrics"
        :key="metric.label"
        :metric="{ ...metric, value: metric.value + metric.suffix }"
      />
    </div>

    <!-- 主体布局 -->
    <div class="agent-search-layout min-w-0">
      <div class="agent-search-main min-w-0">
        <!-- 页面头部 -->
        <div class="page-hero">
          <div class="page-hero-icon"><Fish :size="28" /></div>
          <div class="page-hero-text">
            <h1>渔场评估智能体</h1>
            <p>面向渔场环境评估、资源丰度分析、作业适宜性研判与渔情预测的智能体</p>
          </div>
          <div class="page-hero-meta">
            <span class="meta-badge"><Anchor :size="14" /> 渔场评估</span>
          </div>
          <div class="page-actions">
            <button @click="showReportDialog = true"><FileText :size="17" />评估报告</button>
          </div>
        </div>

        <!-- 主内容区 -->
        <div class="fishery-main-area">
          <!-- 渔场适宜性分布（Leaflet 地图） -->
          <section class="panel ocean-map fishery-map">
            <header class="panel-header"><h2>渔场适宜性分布</h2><div class="tabs"><button @click="openSuitabilityMap">适宜度综合</button></div></header>
            <div class="map-wrapper">
              <div id="hainan-map" class="real-hainan-map leaflet-map-base"></div>
              <OceanCurrent size="small" />
            </div>
          </section>

          <!-- 关键评估指标 -->
          <section class="panel micro-panel">
            <header class="panel-header"><h2>关键评估指标</h2><div class="tabs"><button> 24小时 </button></div></header>
            <div class="micro-grid">
              <article
                v-for="item in indicators"
                :key="item.label"
                :class="`tone-${item.tone}`"
              >
                <span>{{ item.label }}</span>
                <strong>
                  {{ item.value }}
                  <em class="indicator-unit">{{ item.unit }}</em>
                </strong>
                <small>
                  {{ item.change }}
                  <b>{{ item.status }}</b>
                </small>
                <svg viewBox="0 0 100 28" preserveAspectRatio="none">
                  <polyline :points="item.sparkline" />
                </svg>
              </article>
            </div>
          </section>

          <!-- 渔场排行 -->
          <section class="panel detail-table">
            <header class="panel-header">
              <h2>渔场排行</h2>
              <button @click="showMoreRanking = true">更多 ›</button>
            </header>
            <table>
              <thead>
                <tr>
                  <th>排名</th><th>渔场名称</th><th>综合适宜度</th><th>资源丰度</th><th>主要目标鱼种</th><th>最佳作业窗口</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in ranking" :key="row[0]">
                  <td>{{ index + 1 }}</td>
                  <td>{{ row[0] }}</td>
                  <td>{{ row[1] }}</td>
                  <td>{{ row[2] }}</td>
                  <td>{{ row[3] }}</td>
                  <td>{{ row[4] }}</td>
                </tr>
              </tbody>
            </table>
          </section>

          <!-- 智能作业建议 -->
          <section class="panel qa-advice-panel">
            <header class="panel-header"><h2>智能作业建议</h2><button @click="showMoreAdvice = true">更多 ›</button></header>
            <article v-for="item in adviceDetails.slice(0, 4)" :key="item.title">
              <component
                :is="item.icon === 'Anchor' ? Anchor : item.icon === 'ShieldCheck' ? ShieldCheck : item.icon === 'Fish' ? Fish : RadioTower"
                :size="18"
              />
              <span>{{ item.content }}</span>
            </article>
          </section>
        </div>
      </div>

      <!-- 侧边栏 -->
      <aside class="agent-search-aside fishery-aside min-w-0">
        <section class="panel side-feed-panel">
          <header class="panel-header"><h2>数据来源</h2><button @click="showMoreSources = true">更多 ›</button></header>
          <ul><li v-for="source in sideSources" :key="source">{{ source }} <span>正常</span></li></ul>
        </section>

        <section class="panel side-feed-panel">
          <header class="panel-header"><h2>模型运行状态</h2><button @click="showMoreModels = true">更多 ›</button></header>
          <ul><li v-for="model in ['渔场适宜性评估模型','资源丰度预测模型','鱼群热点识别模型','作业窗口研判模型','渔情短期预测模型']" :key="model">{{ model }} <span>运行中</span></li></ul>
        </section>

        <section class="panel trend-panel">
          <header class="panel-header"><h2>趋势预测</h2></header>
          <div class="line-chart">
            <svg viewBox="0 0 100 45" preserveAspectRatio="none">
              <polyline class="trend-line blue-trend" points="0,28 10,23 20,25 30,30 40,27 50,24 60,20 70,15 80,12 90,15 100,11" />
              <polyline class="trend-line green-line" points="0,35 10,31 20,34 30,37 40,33 50,31 60,29 70,26 80,22 90,18 100,14" />
            </svg>
          </div>
        </section>

        <section class="panel detail-table compact">
          <header class="panel-header">
            <h2>目标鱼种分析</h2>
            <button @click="showMoreFishTarget = true">更多 ›</button>
          </header>
          <table>
            <tbody>
              <tr v-for="fish in fishTargetDetails.slice(0, 5)" :key="fish.name">
                <td>{{ fish.name }}</td>
                <td>资源丰度 {{ fish.abundance }}</td>
                <td class="trend-up">{{ fish.trend }}</td>
                <td>{{ fish.proportion }}</td>
              </tr>
            </tbody>
          </table>
        </section>
      </aside>
    </div>

    <!-- 适宜度综合大图（Leaflet 全球地图 + 洋流动画） -->
    <div v-if="showSuitabilityMap" class="big-map-overlay" @click="closeSuitabilityMap">
      <div class="big-map-dialog" @click.stop>
        <div class="big-map-header">
          <h3>海南岛周边渔场适宜度综合分布</h3>
          <div class="big-map-actions">
            <button @click="toggleLabels">{{ showFishLabels ? '隐藏标注' : '显示标注' }}</button>
            <button @click="resetZoom">重置视图</button>
            <button @click="closeSuitabilityMap">关闭</button>
          </div>
        </div>
        <div class="big-map-body">
          <div class="big-map-container">
            <div id="big-world-map"></div>
            <OceanCurrent size="big" />
          </div>
        </div>
      </div>
    </div>

    <!-- 渔场排行弹窗 -->
    <AppModal v-model:visible="showMoreRanking" :title="`渔场排行详情（共 ${fullRankingData.length} 个渔场）`" width="1000px">
      <div class="modal-scroll">
        <table class="full-table">
          <thead><tr><th>排名</th><th>渔场名称</th><th>综合适宜度</th><th>资源丰度</th><th>主要目标鱼种</th><th>最佳作业窗口</th></tr></thead>
          <tbody>
            <tr v-for="item in fullRankingData" :key="item.rank">
              <td>{{ item.rank }}</td><td>{{ item.name }}</td><td>{{ item.suitability }}</td><td>{{ item.abundance }}</td><td>{{ item.fish }}</td><td>{{ item.window }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #footer>
        <button class="confirm-btn" @click="showMoreRanking = false">关闭</button>
      </template>
    </AppModal>

    <!-- 模型运行状态弹窗 -->
    <AppModal v-model:visible="showMoreModels" :title="`模型运行状态（共 ${modelDetails.length} 个模型）`" width="1000px">
      <div class="modal-scroll">
        <table class="full-table">
          <thead><tr><th>模型名称</th><th>状态</th><th>准确率</th><th>更新时间</th><th>描述</th></tr></thead>
          <tbody>
            <tr v-for="(item, idx) in modelDetails" :key="idx">
              <td>{{ item.name }}</td>
              <td><span :class="item.status === '运行中' ? 'status-running' : 'status-warning'">{{ item.status }}</span></td>
              <td>{{ item.accuracy }}</td><td>{{ item.updateTime }}</td><td>{{ item.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #footer>
        <button class="confirm-btn" @click="showMoreModels = false">关闭</button>
      </template>
    </AppModal>

    <!-- 目标鱼种分析弹窗 -->
    <AppModal v-model:visible="showMoreFishTarget" :title="`目标鱼种分析（共 ${fishTargetDetails.length} 种）`" width="900px">
      <div class="modal-scroll">
        <table class="full-table">
          <thead><tr><th>鱼种</th><th>资源丰度</th><th>趋势</th><th>占比</th><th>栖息地</th><th>最佳季节</th></tr></thead>
          <tbody>
            <tr v-for="(item, idx) in fishTargetDetails" :key="idx">
              <td>{{ item.name }}</td><td>{{ item.abundance }}</td><td class="trend-up">{{ item.trend }}</td><td>{{ item.proportion }}</td><td>{{ item.habitat }}</td><td>{{ item.bestSeason }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #footer>
        <button class="confirm-btn" @click="showMoreFishTarget = false">关闭</button>
      </template>
    </AppModal>

    <!-- 数据来源弹窗 -->
    <AppModal v-model:visible="showMoreSources" :title="`数据来源详情（共 ${sourceDetails.length} 个数据源）`" width="900px">
      <div class="modal-scroll">
        <table class="full-table">
          <thead><tr><th>数据源</th><th>状态</th><th>延迟</th><th>类型</th><th>覆盖范围</th><th>更新频率</th></tr></thead>
          <tbody>
            <tr v-for="(item, idx) in sourceDetails" :key="idx">
              <td>{{ item.name }}</td><td><span class="status-running">{{ item.status }}</span></td><td>{{ item.delay }}</td><td>{{ item.type }}</td><td>{{ item.coverage }}</td><td>{{ item.updateFreq }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #footer>
        <button class="confirm-btn" @click="showMoreSources = false">关闭</button>
      </template>
    </AppModal>

    <!-- 智能作业建议弹窗 -->
    <AppModal v-model:visible="showMoreAdvice" :title="`智能作业建议（共 ${adviceDetails.length} 条）`" width="800px">
      <div class="advice-grid">
        <div v-for="(item, idx) in adviceDetails" :key="idx" class="advice-card" :class="`priority-${item.priority === '高' ? 'high' : item.priority === '中' ? 'mid' : 'low'}`">
          <div class="advice-header">
            <component :is="item.icon === 'Anchor' ? Anchor : item.icon === 'ShieldCheck' ? ShieldCheck : item.icon === 'Fish' ? Fish : item.icon === 'RadioTower' ? RadioTower : item.icon === 'Settings' ? Settings : item.icon === 'Database' ? Database : item.icon === 'Globe' ? Globe : Cloud" :size="20" />
            <strong>{{ item.title }}</strong>
            <span class="priority-tag">{{ item.priority }}优先级</span>
          </div>
          <p class="advice-content">{{ item.content }}</p>
        </div>
      </div>
      <template #footer>
        <button class="confirm-btn" @click="showMoreAdvice = false">关闭</button>
      </template>
    </AppModal>

    <!-- 生成报告弹窗 -->
    <AppModal v-model:visible="showReportDialog" title="生成评估报告" width="600px">
      <div class="report-form">
        <div class="form-group">
          <label>报告类型</label>
          <div class="report-type-buttons">
            <button v-for="type in reportTypes" :key="type" :class="['type-btn', { active: reportConfig.type === type }]" @click="reportConfig.type = type">{{ type }}</button>
          </div>
        </div>
        <div class="form-group">
          <label>时间范围</label>
          <select v-model="reportConfig.timeRange" class="time-select">
            <option v-for="range in timeRanges" :key="range" :value="range">{{ range }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>输出格式</label>
          <div class="format-options">
            <label class="format-option"><input type="radio" value="PDF" v-model="reportConfig.format"> PDF文档</label>
            <label class="format-option"><input type="radio" value="Excel" v-model="reportConfig.format"> Excel表格</label>
            <label class="format-option"><input type="radio" value="Word" v-model="reportConfig.format"> Word文档</label>
            <label class="format-option"><input type="radio" value="HTML" v-model="reportConfig.format"> 在线预览</label>
          </div>
        </div>
        <div class="form-group">
          <label>包含内容</label>
          <div class="content-options">
            <label class="content-option"><input type="checkbox" v-model="reportConfig.includeCharts"> 包含图表分析</label>
            <label class="content-option"><input type="checkbox" v-model="reportConfig.includeData"> 包含原始数据</label>
          </div>
        </div>
        <div class="report-preview">
          <h4>报告预览</h4>
          <div class="preview-stats">
            <div class="stat-item"><span class="stat-label">预计页数</span><span class="stat-value">{{ reportConfig.includeCharts && reportConfig.includeData ? '8-10' : '4-6' }}页</span></div>
            <div class="stat-item"><span class="stat-label">数据量</span><span class="stat-value">约 {{ reportConfig.includeData ? '156' : '42' }}条数据</span></div>
            <div class="stat-item"><span class="stat-label">图表数量</span><span class="stat-value">{{ reportConfig.includeCharts ? '12' : '0' }}个</span></div>
          </div>
        </div>
      </div>
      <template #footer>
        <button class="cancel-btn" @click="showReportDialog = false">取消</button>
        <button class="generate-btn" @click="generateReport" :disabled="isGenerating">{{ isGenerating ? '生成中...' : '生成报告' }}</button>
      </template>
    </AppModal>
  </section>
</template>

<style scoped>
/* ── 布局 ── */
.fishery-main-area { display: flex; flex-direction: column; gap: 16px; }
.fishery-aside { display: flex; flex-direction: column; gap: 16px; }

/* ── 地图覆盖层（页面特有蓝色滤镜） ── */
.real-hainan-map::after,
.big-map-body::after {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 450;
  pointer-events: none;
  background:
    radial-gradient(circle at 65% 35%, rgba(0, 255, 220, .12), transparent 28%),
    linear-gradient(135deg, rgba(0, 120, 255, .28), rgba(0, 255, 180, .08));
  mix-blend-mode: screen;
}
.real-hainan-map :deep(.leaflet-interactive) {
  animation: pulseGlow 2s infinite;
}
#big-world-map :deep(.hainan-fish-marker) {
  animation: pulseGlow 2s infinite;
}
#big-world-map :deep(.world-fish-marker) {
  animation: pulseGlow 2s infinite;
  filter: drop-shadow(0 0 5px rgba(255, 92, 92, .75));
}

/* ── 大地图弹窗 ── */
.big-map-overlay {
  position: fixed;
  inset: 0;
  z-index: 1200;
  background: rgba(0, 8, 20, .78);
  display: flex;
  align-items: center;
  justify-content: center;
}
.big-map-dialog {
  width: 92vw;
  height: 86vh;
  background: #061f36;
  border: 1px solid rgba(65, 166, 255, .7);
  border-radius: 14px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.big-map-header {
  height: 54px;
  padding: 0 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #fff;
  border-bottom: 1px solid rgba(65, 166, 255, .35);
}
.big-map-actions {
  display: flex;
  gap: 10px;
}
.big-map-actions button {
  padding: 6px 12px;
  border: 1px solid rgba(86, 171, 255, .8);
  background: rgba(5, 28, 55, .9);
  color: #fff;
  border-radius: 6px;
  cursor: pointer;
  transition: transform .25s ease, box-shadow .25s ease;
}
.big-map-actions button:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 16px rgba(14, 165, 233, .45);
}
.big-map-body {
  position: relative;
  flex: 1;
  overflow: hidden;
}
.big-map-container {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
}
#big-world-map {
  width: 100%;
  height: 100%;
}
#big-world-map :deep(.fish-map-label) {
  background: rgba(5, 24, 48, .88);
  border: 1px solid rgba(56, 189, 248, .55);
  color: #fff;
  border-radius: 6px;
  padding: 3px 7px;
  box-shadow: 0 0 12px rgba(56, 189, 248, .25);
  font-size: 12px;
}
#big-world-map :deep(.hainan-label) { border-color: rgba(45, 212, 191, .8); }
#big-world-map :deep(.world-label) { border-color: rgba(255, 107, 107, .75); }

/* ── 趋势图 ── */
.trend-line { fill: none; stroke-width: 2.4; transition: stroke-width 0.25s ease, filter 0.25s ease, opacity 0.25s ease; cursor: pointer; pointer-events: stroke; }
.trend-line:hover { stroke-width: 4.8; filter: drop-shadow(0 0 6px currentColor); opacity: 1; }
.line-chart svg:hover .trend-line:not(:hover) { opacity: 0.35; }
.blue-trend { color: #38bdf8; stroke: currentColor; }
.green-line { color: #34d399; stroke: currentColor; }

/* ── 报告表单 ── */
.report-form { padding: 8px 0; }
.form-group { margin-bottom: 24px; }
.form-group label { display: block; font-size: 14px; font-weight: 500; color: #e0e0e0; margin-bottom: 12px; }
.report-type-buttons { display: flex; flex-wrap: wrap; gap: 10px; }
.type-btn { padding: 8px 16px; background: rgba(30, 55, 91, 0.6); border: 1px solid #0b162d; border-radius: 20px; font-size: 13px; color: #cbd5e1; cursor: pointer; transition: transform .25s ease, box-shadow .25s ease, background .25s ease; }
.type-btn:hover { transform: translateY(-2px); box-shadow: 0 0 16px rgba(14, 165, 233, .45); }
.type-btn.active { background: #10b981; color: white; border-color: #10b981; }
.time-select { width: 100%; padding: 10px 12px; background: rgba(30, 55, 91, 0.6); border: 1px solid #0b162d; border-radius: 8px; color: #e0e0e0; font-size: 14px; cursor: pointer; }
.format-options { display: flex; gap: 20px; flex-wrap: wrap; }
.format-option { display: flex; align-items: center; gap: 6px; color: #cbd5e1; font-size: 14px; cursor: pointer; }
.content-options { display: flex; gap: 20px; }
.content-option { display: flex; align-items: center; gap: 6px; color: #cbd5e1; font-size: 14px; cursor: pointer; }
.report-preview { background: rgba(30, 55, 91, 0.4); border-radius: 12px; padding: 16px; margin-top: 16px; }
.report-preview h4 { color: #e0e0e0; font-size: 14px; margin-bottom: 12px; }
.preview-stats { display: flex; gap: 24px; flex-wrap: wrap; }
.stat-item { display: flex; flex-direction: column; gap: 4px; }
.stat-label { font-size: 12px; color: #8aa4c4; }
.stat-value { font-size: 16px; font-weight: 600; color: #10b981; }

/* ── 指标单位 ── */
.indicator-unit { font-size: 12px; font-style: normal; font-weight: 500; color: rgba(226, 245, 255, .78); margin-left: 3px; }
.micro-grid article small { display: flex; align-items: center; gap: 6px; }
.micro-grid article small b { font-weight: 500; color: rgba(226, 245, 255, .72); }
</style>
