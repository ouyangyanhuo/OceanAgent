<script setup>
import { ref, onMounted } from 'vue'
import { Anchor, Bot, FileText, Fish, RadioTower, Settings, Share2, ShieldCheck, Database, Globe, Cloud } from 'lucide-vue-next'
import gsap from 'gsap'
import MetricCard from '../components/MetricCard.vue'
import AppModal from '../components/common/AppModal.vue'

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

const ranking = [
  ['西沙北部渔场', '94.0', '162.8', '金枪鱼、飞鱼、鲣鱼', '06-04 06:00 - 22:00'],
  ['文昌外海渔场', '91.0', '154.6', '金枪鱼、鲐鱼、马鲛鱼', '06-04 07:00 - 23:00'],
  ['琼州海峡渔场', '86.0', '143.2', '马鲛鱼、鲳鱼、鲷鱼', '06-04 06:30 - 21:30'],
  ['万宁近海渔场', '84.0', '136.5', '带鱼、鲷鱼、鲐鱼', '06-04 08:00 - 22:00'],
  ['儋州近海渔场', '81.0', '128.7', '鲳鱼、马鲛鱼、金线鱼', '06-04 07:30 - 20:30'],
]

const indicators = ['表层水温', '叶绿素a', '盐度', '溶解氧', '有效波高', '生物量指数']
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

const fullRankingData = [
  { rank: 1, name: '西沙北部渔场', suitability: '94.0', abundance: '162.8', fish: '金枪鱼、飞鱼、鲣鱼', window: '06-07 06:00 - 22:00' },
  { rank: 2, name: '文昌外海渔场', suitability: '91.0', abundance: '154.6', fish: '金枪鱼、鲐鱼、马鲛鱼', window: '06-07 07:00 - 23:00' },
  { rank: 3, name: '琼州海峡渔场', suitability: '86.0', abundance: '143.2', fish: '马鲛鱼、鲳鱼、鲷鱼', window: '06-07 06:30 - 21:30' },
  { rank: 4, name: '万宁近海渔场', suitability: '84.0', abundance: '136.5', fish: '带鱼、鲷鱼、鲐鱼', window: '06-07 08:00 - 22:00' },
  { rank: 5, name: '儋州近海渔场', suitability: '81.0', abundance: '128.7', fish: '鲳鱼、马鲛鱼、金线鱼', window: '06-07 07:30 - 20:30' },
  { rank: 6, name: '陵水渔场', suitability: '79.0', abundance: '119.4', fish: '石斑鱼、鲷鱼、鱿鱼', window: '06-07 08:00 - 20:00' },
  { rank: 7, name: '三亚外海渔场', suitability: '76.0', abundance: '112.6', fish: '鱿鱼、鲭鱼、鲣鱼', window: '06-07 09:00 - 20:00' },
  { rank: 8, name: '东方近海渔场', suitability: '72.0', abundance: '105.8', fish: '金线鱼、鲷鱼、马鲛鱼', window: '06-07 09:30 - 19:00' },
  { rank: 9, name: '北部湾东缘渔场', suitability: '69.5', abundance: '98.4', fish: '带鱼、鲳鱼、鱿鱼', window: '06-07 10:00 - 18:30' },
  { rank: 10, name: '南海北部近岸渔场', suitability: '66.8', abundance: '91.7', fish: '鲐鱼、鲷鱼、金线鱼', window: '06-07 10:00 - 18:00' },
]

const modelDetails = [
  { name: '渔场适宜性评估模型', status: '运行中', accuracy: '94.2%', updateTime: '2024-05-24 08:00', description: '基于多源卫星数据评估渔场适宜性' },
  { name: '资源丰度预测模型', status: '运行中', accuracy: '91.5%', updateTime: '2024-05-24 08:00', description: '结合历史渔获与海洋环境预测资源量' },
  { name: '鱼群热点识别模型', status: '运行中', accuracy: '88.7%', updateTime: '2024-05-24 08:00', description: 'AI识别鱼群聚集区域' },
  { name: '作业窗口研判模型', status: '运行中', accuracy: '93.1%', updateTime: '2024-05-24 08:00', description: '综合气象海浪评估作业窗口' },
  { name: '渔情短期预测模型', status: '运行中', accuracy: '86.9%', updateTime: '2024-05-24 08:00', description: '未来3-7天渔情趋势预测' },
  { name: '渔业资源评估模型', status: '待更新', accuracy: '79.2%', updateTime: '2024-05-23 14:00', description: '渔业资源存量评估' },
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
  { name: '历史渔情库', status: '正常', delay: '离线', type: '数据库', coverage: '2000-2024', updateFreq: '季度更新' },
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

// 地图交互
const mapScale = ref(1)
const minScale = 0.5
const maxScale = 2
const mapOffset = ref({ x: 0, y: 0 })
const isMapDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })

const zoomIn = () => { if (mapScale.value < maxScale) mapScale.value = Math.min(mapScale.value + 0.1, maxScale) }
const zoomOut = () => { if (mapScale.value > minScale) mapScale.value = Math.max(mapScale.value - 0.1, minScale) }
const resetZoom = () => { mapScale.value = 1; mapOffset.value = { x: 0, y: 0 } }

const hainanFishPoints = [
  { name: '琼州海峡渔场', x: 48, y: 23, score: 86, fish: '马鲛鱼、鲳鱼', level: '较高' },
  { name: '文昌外海渔场', x: 63, y: 33, score: 91, fish: '金枪鱼、鲐鱼', level: '极高' },
  { name: '万宁近海渔场', x: 66, y: 43, score: 84, fish: '带鱼、鲷鱼', level: '较高' },
  { name: '陵水渔场', x: 52, y: 60, score: 79, fish: '石斑鱼、鲷鱼', level: '较优' },
  { name: '三亚外海渔场', x: 58, y: 64, score: 76, fish: '鱿鱼、鲭鱼', level: '较优' },
  { name: '东方近海渔场', x: 27, y: 42, score: 72, fish: '金线鱼、鲷鱼', level: '低' },
  { name: '儋州近海渔场', x: 36, y: 34, score: 81, fish: '鲳鱼、马鲛鱼', level: '较高' },
  { name: '西沙北部渔场', x: 78, y: 72, score: 94, fish: '金枪鱼、飞鱼', level: '极高' },
]

const activeFishPoint = ref(null)
const selectFishPoint = (point) => { activeFishPoint.value = point }

const startMapDrag = (event) => {
  isMapDragging.value = true
  dragStart.value = { x: event.clientX - mapOffset.value.x, y: event.clientY - mapOffset.value.y }
}
const onMapDrag = (event) => {
  if (!isMapDragging.value) return
  mapOffset.value = { x: event.clientX - dragStart.value.x, y: event.clientY - dragStart.value.y }
}
const stopMapDrag = () => { isMapDragging.value = false }
const handleMapWheel = (event) => { if (event.deltaY < 0) zoomIn(); else zoomOut() }

const showSuitabilityMap = ref(false)
const showFishLabels = ref(true)
const openSuitabilityMap = () => { showSuitabilityMap.value = true; activeFishPoint.value = null }
const closeSuitabilityMap = () => { showSuitabilityMap.value = false; activeFishPoint.value = null }

// ── GSAP 入场动画 ──
onMounted(() => {
  animateMetrics()

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

        <!-- 主内容区：一行一个面板 -->
        <div class="fishery-main-area">
          <!-- 渔场适宜性分布 -->
          <section class="panel ocean-map fishery-map">
            <header class="panel-header"><h2>渔场适宜性分布</h2><div class="tabs"><button @click="openSuitabilityMap">适宜度综合</button></div></header>
            <div class="map-surface heatmap" @wheel.prevent="handleMapWheel" @click="activeFishPoint = null">
              <div
                class="map-zoom-layer"
                :class="{ dragging: isMapDragging }"
                :style="{ transform: `translate(${mapOffset.x}px, ${mapOffset.y}px) scale(${mapScale})` }"
                @mousedown="startMapDrag"
                @mousemove="onMapDrag"
                @mouseup="stopMapDrag"
                @mouseleave="stopMapDrag"
              >
                <div class="hainan-island">
                  <span class="city haikou">海口</span>
                  <span class="city sanya">三亚</span>
                  <span class="city wanning">万宁</span>
                  <span class="city dongfang">东方</span>
                </div>

                <span class="sea-label south-sea">南海北部</span>
                <span class="sea-label qiongzhou">琼州海峡</span>
                <span class="sea-label xisha">西沙方向</span>

                <i class="hot-zone hz1"></i>
                <i class="hot-zone hz2"></i>
                <i class="hot-zone hz3"></i>
                <i class="hot-zone hz4"></i>

                <button
                  v-for="point in hainanFishPoints"
                  :key="point.name"
                  class="fish-point"
                  :class="[point.level, { 'label-left': point.x > 70 }]"
                  :style="{ left: point.x + '%', top: point.y + '%' }"
                  @click.stop="selectFishPoint(point)"
                >
                  <b></b>
                  <span>{{ point.name }}</span>
                </button>
              </div>

              <div class="map-tools">
                <button @click="zoomIn">+</button>
                <button @click="zoomOut">-</button>
                <button @click="resetZoom">⌖</button>
              </div>

              <div
                v-if="activeFishPoint"
                class="fish-popup"
                :style="{ left: activeFishPoint.x + '%', top: activeFishPoint.y + '%' }"
                @click.stop
              >
                <button class="fish-popup-close" @click="activeFishPoint = null">×</button>
                <strong>{{ activeFishPoint.name }}</strong>
                <p>适宜度：{{ activeFishPoint.score }} / 100</p>
                <p>等级：{{ activeFishPoint.level }}</p>
                <p>主要鱼种：{{ activeFishPoint.fish }}</p>
              </div>

              <div class="map-legend">
                <strong>适宜度分级</strong>
                <span class="red">极高</span>
                <span class="amber">较高</span>
                <span class="green">较优</span>
                <span class="blue">低</span>
                <span>鱼群热点</span>
                <span>监测点</span>
              </div>
            </div>
          </section>

          <!-- 关键评估指标 -->
          <section class="panel micro-panel">
            <header class="panel-header"><h2>关键评估指标</h2><div class="tabs"></div></header>
            <div class="micro-grid">
              <article v-for="(item, index) in indicators" :key="item" :class="`tone-${['blue','teal','cyan','green','violet','amber'][index]}`">
                <span>{{ item }}</span><strong>{{ ['18.6','2.18','32.4','6.12','1.32','142.6'][index] }}</strong><small>↑ {{ ['0.3','0.24','0.1','0.18','0.12','14.8'][index] }}</small>
                <svg viewBox="0 0 100 28" preserveAspectRatio="none"><polyline points="0,22 12,18 25,20 38,12 52,16 68,13 84,19 100,10" /></svg>
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

    <!-- 适宜度综合大图 -->
    <div v-if="showSuitabilityMap" class="big-map-overlay" @click="closeSuitabilityMap">
      <div class="big-map-dialog" @click.stop>
        <div class="big-map-header">
          <h3>海南岛周边渔场适宜度综合分布</h3>
          <div class="big-map-actions">
            <button @click="showFishLabels = !showFishLabels">{{ showFishLabels ? '隐藏标注' : '显示标注' }}</button>
            <button @click="resetZoom">重置视图</button>
            <button @click="closeSuitabilityMap">关闭</button>
          </div>
        </div>
        <div class="big-map-body" @wheel.prevent="handleMapWheel" @click="activeFishPoint = null">
          <div
            class="big-map-layer"
            :class="{ dragging: isMapDragging }"
            :style="{ transform: `translate(${mapOffset.x}px, ${mapOffset.y}px) scale(${mapScale})` }"
            @mousedown="startMapDrag"
            @mousemove="onMapDrag"
            @mouseup="stopMapDrag"
            @mouseleave="stopMapDrag"
          >
            <div class="big-hainan-island">
              <span class="big-city big-haikou">海口市</span>
              <span class="big-city big-danzhou">儋州市</span>
              <span class="big-city big-dongfang">东方市</span>
              <span class="big-city big-sanya">三亚市</span>
              <span class="big-city big-wanning">万宁市</span>
              <span class="big-city big-qionghai">琼海市</span>
            </div>
            <i class="flow f1"></i>
            <i class="flow f2"></i>
            <i class="flow f3"></i>
            <i class="flow f4"></i>
            <i class="flow f5"></i>
            <button
              v-for="point in hainanFishPoints"
              :key="point.name"
              class="big-fish-point"
              :class="[point.level, { 'label-left': point.x > 70, 'hide-label': !showFishLabels }]"
              :style="{ left: point.x + '%', top: point.y + '%' }"
              @click.stop="selectFishPoint(point)"
            >
              <b></b>
              <span>{{ point.name }}</span>
            </button>
          </div>
          <div class="big-map-tools">
            <button @click.stop="zoomIn">+</button>
            <button @click.stop="zoomOut">-</button>
            <button @click.stop="resetZoom">⌖</button>
          </div>
          <div
            v-if="activeFishPoint"
            class="big-fish-popup"
            :style="{ left: activeFishPoint.x + '%', top: activeFishPoint.y + '%' }"
            @click.stop
          >
            <button class="fish-popup-close" @click="activeFishPoint = null">×</button>
            <strong>{{ activeFishPoint.name }}</strong>
            <p>适宜度：{{ activeFishPoint.score }} / 100</p>
            <p>等级：{{ activeFishPoint.level }}</p>
            <p>主要鱼种：{{ activeFishPoint.fish }}</p>
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
.fishery-main-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.fishery-aside {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ── 地图 ── */
.map-surface {
  position: relative;
  height: 282px;
  overflow: hidden;
  border-radius: 10px;
  background:
    radial-gradient(circle at 63% 45%, rgba(255, 59, 48, 0.7), transparent 10%),
    radial-gradient(circle at 58% 55%, rgba(255, 179, 49, 0.55), transparent 13%),
    radial-gradient(circle at 76% 70%, rgba(255, 59, 48, 0.55), transparent 12%),
    linear-gradient(135deg, #07365a, #03192d 70%);
  border: 1px solid rgba(45, 144, 220, 0.45);
  cursor: grab;
}
.map-surface::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: repeating-linear-gradient(145deg, rgba(0, 180, 255, 0.32) 0, rgba(0, 180, 255, 0.32) 1px, transparent 1px, transparent 16px);
  z-index: 3;
}
.map-zoom-layer {
  position: absolute;
  inset: 0;
  transform-origin: center center;
  transition: transform 0.25s ease;
  z-index: 2;
  cursor: grab;
  user-select: none;
}
.map-zoom-layer.dragging { cursor: grabbing; }

.hainan-island {
  position: absolute;
  left: 22%; top: 26%;
  width: 150px; height: 190px;
  background: linear-gradient(145deg, rgba(37, 94, 70, 0.92), rgba(24, 71, 58, 0.98));
  clip-path: polygon(42% 0, 70% 10%, 88% 32%, 78% 62%, 55% 88%, 28% 100%, 8% 78%, 0 44%, 16% 14%);
  box-shadow: inset 0 0 40px rgba(42, 245, 178, 0.16);
}
.city, .sea-label { position: absolute; color: #fff; font-size: 13px; text-shadow: 0 0 8px #00b7ff; white-space: nowrap; }
.city { z-index: 18; font-weight: 600; pointer-events: none; text-shadow: 0 0 4px #00182d, 0 0 8px #00b7ff, 1px 1px 2px #00182d; }
.haikou { left: 40%; top: 8%; }
.sanya { left: 40%; bottom: 12%; }
.wanning { right: 16%; top: 46%; }
.dongfang { left: 10%; top: 45%; }
.south-sea { left: 66%; top: 12%; }
.qiongzhou { left: 38%; top: 18%; }
.xisha { left: 80%; top: 58%; }

.hot-zone { position: absolute; width: 140px; height: 58px; border-radius: 50%; filter: blur(8px); opacity: 0.88; transform: rotate(-32deg); background: radial-gradient(circle, rgba(255, 59, 48, 0.9), rgba(255, 211, 61, 0.75), rgba(48, 224, 150, 0.35), transparent 72%); }
.hz1 { left: 54%; top: 28%; }
.hz2 { left: 48%; top: 48%; }
.hz3 { left: 70%; top: 64%; }
.hz4 { left: 34%; top: 36%; opacity: 0.45; }

.fish-point { position: absolute; z-index: 12; transform: translate(-6px, -50%); border: none; background: transparent; cursor: pointer; color: #fff; display: flex; align-items: center; gap: 6px; }
.fish-point b { flex: 0 0 auto; width: 13px; height: 13px; border-radius: 50%; background: #1e9bff; border: 2px solid #fff; box-shadow: 0 0 12px rgba(30, 155, 255, 0.95); }
.fish-point span { max-width: 96px; font-size: 12px; white-space: nowrap; text-shadow: 0 0 8px #00b7ff, 0 0 3px #00182d; pointer-events: none; transform: translateY(-14px); margin-left: 2px; padding: 1px 4px; background: rgba(3, 19, 36, 0.55); border-radius: 4px; opacity: 0; transition: opacity 0.2s; }
.fish-point:hover span { opacity: 1; }
.fish-point.label-left { transform: translate(-100%, -50%); flex-direction: row-reverse; }
.fish-point.label-left span { margin-left: 0; margin-right: 2px; }
.fish-point.极高 b { background: #ff3b30; }
.fish-point.较高 b { background: #ffb331; }
.fish-point.较优 b { background: #30e096; }
.fish-point.低 b { background: #1688ff; }

.map-tools { position: absolute; left: 12px; top: 76px; z-index: 10; display: flex; flex-direction: column; gap: 6px; }
.map-tools button { width: 32px; height: 32px; border: 1px solid rgba(86, 171, 255, 0.8); background: rgba(5, 28, 55, 0.9); color: #fff; border-radius: 6px; cursor: pointer; }

.fish-popup { position: absolute; z-index: 20; width: 168px; padding: 10px 12px; transform: translate(14px, -50%); background: rgba(5, 24, 48, 0.94); border: 1px solid rgba(48, 145, 255, 0.65); border-radius: 8px; color: #fff; font-size: 12px; box-shadow: 0 8px 22px rgba(0, 0, 0, 0.35); }
.fish-popup p { margin: 5px 0 0; color: #cde8ff; }
.fish-popup-close { position: absolute; right: 6px; top: 4px; border: none; background: transparent; color: #9ed8ff; font-size: 16px; cursor: pointer; }

.map-legend { position: absolute; right: 14px; top: 58px; z-index: 12; width: 124px; padding: 12px; background: rgba(5, 24, 48, 0.9); border: 1px solid rgba(48, 145, 255, 0.55); border-radius: 8px; color: #fff; font-size: 12px; }
.map-legend span { display: block; margin-top: 8px; }
.map-legend span::before { content: ""; display: inline-block; width: 10px; height: 10px; margin-right: 7px; border-radius: 2px; background: #6ab7ff; }
.map-legend .red::before { background: #ff3b30; }
.map-legend .amber::before { background: #ffb331; }
.map-legend .green::before { background: #30e096; }
.map-legend .blue::before { background: #1688ff; }

/* ── 趋势图 ── */
.trend-line { fill: none; stroke-width: 2.4; transition: stroke-width 0.25s ease, filter 0.25s ease, opacity 0.25s ease; cursor: pointer; pointer-events: stroke; }
.trend-line:hover { stroke-width: 4.8; filter: drop-shadow(0 0 6px currentColor); opacity: 1; }
.line-chart svg:hover .trend-line:not(:hover) { opacity: 0.35; }
.blue-trend { color: #38bdf8; stroke: currentColor; }
.green-line { color: #34d399; stroke: currentColor; }

/* ── 弹窗内容 ── */
.modal-scroll { overflow-x: auto; }
.full-table { width: 100%; min-width: 700px; border-collapse: collapse; }
.full-table th, .full-table td { padding: 12px 10px; border-bottom: 1px solid rgba(39, 151, 255, 0.12); text-align: left; color: #b9d6ee; }
.full-table th { position: sticky; top: 0; z-index: 1; font-weight: 600; color: #fff; background: rgba(7, 28, 52, 0.98); }
.confirm-btn { padding: 8px 24px; background: #10b981; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; }
.confirm-btn:hover { background: #059669; }
.status-running { color: #10b981; }
.status-warning { color: #f59e0b; }
.trend-up { color: #10b981; }

/* ── 建议卡片 ── */
.advice-grid { display: flex; flex-direction: column; gap: 12px; padding: 16px 0; }
.advice-card { background: rgba(30, 55, 91, 0.6); border-radius: 12px; padding: 14px 16px; border-left: 3px solid; }
.advice-card.priority-high { border-left-color: #ef4444; }
.advice-card.priority-mid { border-left-color: #f59e0b; }
.advice-card.priority-low { border-left-color: #10b981; }
.advice-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; color: #fff; }
.priority-tag { font-size: 11px; padding: 2px 8px; border-radius: 12px; background: rgba(255, 255, 255, 0.1); margin-left: auto; }
.advice-content { color: #cbd5e1; font-size: 14px; line-height: 1.5; margin: 0; }

/* ── 报告表单 ── */
.report-form { padding: 8px 0; }
.form-group { margin-bottom: 24px; }
.form-group label { display: block; font-size: 14px; font-weight: 500; color: #e0e0e0; margin-bottom: 12px; }
.report-type-buttons { display: flex; flex-wrap: wrap; gap: 10px; }
.type-btn { padding: 8px 16px; background: rgba(30, 55, 91, 0.6); border: 1px solid #0b162d; border-radius: 20px; font-size: 13px; color: #cbd5e1; cursor: pointer; }
.type-btn:hover { background: #1e375b; border-color: #5a7a9e; }
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
.cancel-btn { padding: 8px 20px; background: transparent; border: 1px solid #5a7a9e; border-radius: 8px; color: #cbd5e1; cursor: pointer; margin-right: 12px; }
.cancel-btn:hover { background: rgba(90, 122, 158, 0.3); border-color: #7a9abe; }
.generate-btn { padding: 8px 24px; background: #10b981; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; }
.generate-btn:hover { background: #059669; }
.generate-btn:disabled { background: #5a7a9e; cursor: not-allowed; }

/* ── 大地图弹窗 ── */
.big-map-overlay { position: fixed; inset: 0; z-index: 1200; background: rgba(0, 8, 20, 0.78); display: flex; align-items: center; justify-content: center; }
.big-map-dialog { width: 92vw; height: 86vh; background: #061f36; border: 1px solid rgba(65, 166, 255, 0.7); border-radius: 14px; overflow: hidden; display: flex; flex-direction: column; }
.big-map-header { height: 54px; padding: 0 18px; display: flex; align-items: center; justify-content: space-between; color: #fff; border-bottom: 1px solid rgba(65, 166, 255, 0.35); }
.big-map-actions { display: flex; gap: 10px; }
.big-map-actions button { padding: 6px 12px; border: 1px solid rgba(86, 171, 255, 0.8); background: rgba(5, 28, 55, 0.9); color: #fff; border-radius: 6px; cursor: pointer; }
.big-map-body { position: relative; flex: 1; overflow: auto; cursor: grab; background: radial-gradient(circle at 28% 60%, rgba(255, 236, 45, 0.75), transparent 12%), radial-gradient(circle at 48% 16%, rgba(255, 236, 45, 0.7), transparent 10%), radial-gradient(circle at 70% 58%, rgba(255, 236, 45, 0.78), transparent 14%), radial-gradient(circle at 82% 25%, rgba(130, 230, 62, 0.7), transparent 12%), radial-gradient(circle at 64% 88%, rgba(39, 82, 240, 0.9), transparent 16%), linear-gradient(135deg, #2549e8, #1a6f74 55%, #2443dd); }
.big-map-layer { position: absolute; inset: 0; transform-origin: center center; transition: transform 0.2s ease; user-select: none; }
.big-map-layer.dragging { cursor: grabbing; transition: none; }
.big-hainan-island { position: absolute; left: 28%; top: 18%; width: 38%; height: 62%; background: #f4f1e8; clip-path: polygon(46% 0, 72% 6%, 94% 28%, 88% 58%, 70% 82%, 44% 100%, 18% 88%, 0 60%, 10% 28%, 28% 8%); box-shadow: 0 0 0 12px rgba(205, 231, 255, 0.9); }
.big-city { position: absolute; color: #4c2d14; font-size: 15px; font-weight: 600; white-space: nowrap; }
.big-haikou { left: 44%; top: 8%; }
.big-danzhou { left: 24%; top: 34%; }
.big-dongfang { left: 4%; top: 54%; }
.big-sanya { left: 42%; bottom: 4%; }
.big-wanning { right: 7%; top: 58%; }
.big-qionghai { right: 12%; top: 43%; }
.flow { position: absolute; width: 3px; height: 82px; background: rgba(255, 255, 255, 0.72); border-radius: 999px; transform: rotate(16deg); opacity: 0.75; }
.f1 { left: 12%; top: 16%; }
.f2 { left: 20%; top: 44%; }
.f3 { left: 71%; top: 22%; }
.f4 { left: 82%; top: 38%; }
.f5 { left: 58%; top: 76%; }
.big-fish-point { position: absolute; z-index: 10; transform: translate(-6px, -50%); border: none; background: transparent; color: #fff; cursor: pointer; display: flex; align-items: center; gap: 6px; }
.big-fish-point b { width: 14px; height: 14px; border-radius: 50%; border: 2px solid #fff; background: #1e9bff; box-shadow: 0 0 12px rgba(30, 155, 255, 0.95); }
.big-fish-point span { padding: 2px 6px; border-radius: 5px; background: rgba(0, 20, 40, 0.62); font-size: 13px; white-space: nowrap; text-shadow: 0 0 6px #00182d; }
.big-fish-point.hide-label span { display: none; }
.big-fish-point.极高 b { background: #ff3b30; }
.big-fish-point.较高 b { background: #ffb331; }
.big-fish-point.较优 b { background: #30e096; }
.big-fish-point.低 b { background: #1688ff; }
.big-fish-popup { position: absolute; z-index: 30; width: 180px; padding: 10px 12px; transform: translate(18px, -50%); background: rgba(5, 24, 48, 0.95); border: 1px solid rgba(48, 145, 255, 0.7); border-radius: 8px; color: #fff; font-size: 12px; }
.big-map-tools { position: absolute; left: 18px; top: 18px; z-index: 40; display: flex; flex-direction: column; gap: 8px; }
.big-map-tools button { width: 34px; height: 34px; border: 1px solid rgba(86, 171, 255, 0.8); background: rgba(5, 28, 55, 0.9); color: #fff; border-radius: 6px; cursor: pointer; }

/* ── 大地图过渡 ── */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.35s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-active .big-map-dialog, .modal-fade-leave-active .big-map-dialog { transition: transform 0.35s ease, opacity 0.35s ease; }
.modal-fade-enter-from .big-map-dialog, .modal-fade-leave-to .big-map-dialog { transform: translateY(28px) scale(0.96); opacity: 0; }
.modal-fade-enter-to .big-map-dialog, .modal-fade-leave-from .big-map-dialog { transform: translateY(0) scale(1); opacity: 1; }
</style>
