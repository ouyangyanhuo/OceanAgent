<script setup>
import { ref, onMounted } from 'vue'
import { AlertTriangle, Battery, Bot, FileText, RadioTower, Settings, Share2, Wrench } from 'lucide-vue-next'
import gsap from 'gsap'
import MetricCard from '../components/MetricCard.vue'
import AppModal from '../components/common/AppModal.vue'

const metrics = [
  { label: '在线浮标', value: '128', trend: '8', tone: 'teal', sparkline: [16, 19, 18, 24, 21, 27, 24, 34, 28, 38, 31, 44] },
  { label: '异常浮标', value: '11', trend: '2', tone: 'amber', sparkline: [12, 10, 14, 12, 18, 15, 22, 16, 24, 19, 27, 21] },
  { label: '数据完整率', value: '96.4%', trend: '1.2%', tone: 'blue', sparkline: [28, 30, 29, 34, 32, 38, 36, 40, 39, 44, 42, 47] },
  { label: '待维护设备', value: '17', trend: '3', tone: 'violet', sparkline: [10, 12, 11, 16, 15, 20, 18, 25, 22, 30, 26, 34] },
]

const sensorRows = [
  ['水温传感器', '96%', '良好'],
  ['盐度传感器', '93%', '良好'],
  ['溶解氧传感器', '72%', '预警'],
  ['叶绿素传感器', '68%', '预警'],
  ['pH传感器', '90%', '良好'],
  ['浊度传感器', '64%', '预警'],
]

const today = new Date()
const mm = String(today.getMonth() + 1).padStart(2, '0')
const dd = String(today.getDate()).padStart(2, '0')
const dateStr = `${today.getFullYear()}-${mm}-${dd}`

const faults = [
  ['B-HN-0042', '琼州海峡', '故障', '溶解氧传感器异常', `${dateStr} 01:18`],
  ['B-WC-0015', '文昌外海', '预警', '电池电量偏低', `${dateStr} 01:06`],
  ['B-SS-0089', '三亚外海', '故障', '通信中断', `${dateStr} 00:41`],
  ['B-DZ-0033', '儋州近海', '预警', '水温数据异常', `${dateStr} 00:22`],
  ['B-WN-0071', '万宁近海', '预警', '叶绿素数据异常', `${dateStr} 00:08`],
]

const indicators = ['水温', '盐度', '溶解氧', '叶绿素-a', '电池电量', '通信质量']
const indicatorValues = ['17.6', '32.1', '6.2', '1.48', '78', '92']
const indicatorTones = ['blue', 'teal', 'green', 'violet', 'amber', 'violet']

// ── 浮标点位（海南周边） ──
const buoyPoints = [
  { name: '琼州海峡浮标', x: 48, y: 22, status: '正常', type: '综合观测', battery: '86%' },
  { name: '文昌外海浮标', x: 64, y: 34, status: '预警', type: '水文气象', battery: '32%' },
  { name: '万宁近海浮标', x: 66, y: 44, status: '正常', type: '水质监测', battery: '91%' },
  { name: '陵水浮标', x: 53, y: 58, status: '正常', type: '海流观测', battery: '78%' },
  { name: '三亚外海浮标', x: 58, y: 65, status: '故障', type: '综合观测', battery: '12%' },
  { name: '东方近海浮标', x: 26, y: 43, status: '正常', type: '水质监测', battery: '94%' },
  { name: '儋州近海浮标', x: 35, y: 33, status: '预警', type: '水文气象', battery: '45%' },
  { name: '西沙北部浮标', x: 78, y: 72, status: '正常', type: '深海观测', battery: '67%' },
  { name: '海口近岸浮标', x: 44, y: 16, status: '正常', type: '水质监测', battery: '88%' },
  { name: '洋浦外海浮标', x: 30, y: 28, status: '正常', type: '海流观测', battery: '73%' },
]

const activeBuoy = ref(null)
const selectBuoy = (point) => { activeBuoy.value = point }

// ── 弹窗控制 ──
const showMoreSources = ref(false)
const showMoreModels = ref(false)
const showMoreFaults = ref(false)
const showMoreAdvice = ref(false)

// ── 更多数据 ──
const fullSources = [
  { name: '浮标实时监测数据', status: '正常', delay: '实时', type: '物联网', coverage: '海南周边', freq: '每分钟' },
  { name: '浮标历史数据', status: '正常', delay: '离线', type: '数据库', coverage: '2018-2026', freq: '每日' },
  { name: '气象数据源', status: '正常', delay: '1小时', type: '风云卫星', coverage: '南海北部', freq: '每小时' },
  { name: '海浪数据源', status: '正常', delay: '6小时', type: '数值预报', coverage: '中国近海', freq: '每日2次' },
  { name: '卫星遥感数据', status: '正常', delay: '3小时', type: 'MODIS', coverage: '全域', freq: '每日' },
  { name: '海洋站潮位数据', status: '正常', delay: '15分钟', type: '验潮站', coverage: '沿岸', freq: '实时' },
  { name: '海底光缆传感', status: '维护', delay: '--', type: 'DAS系统', coverage: '琼州海峡', freq: '连续' },
  { name: '雷达海流监测', status: '正常', delay: '20分钟', type: '地波雷达', coverage: '近岸50km', freq: '每20分钟' },
]

const fullModels = [
  { name: '数据质量评估模型', status: '运行中', accuracy: '96.1%', update: `${dateStr} 01:00`, desc: '评估浮标数据完整性与准确性' },
  { name: '异常诊断模型', status: '运行中', accuracy: '93.4%', update: `${dateStr} 01:08`, desc: '识别传感器与通信异常' },
  { name: '设备健康评估模型', status: '运行中', accuracy: '91.2%', update: `${dateStr} 01:15`, desc: '评估浮标设备整体健康状态' },
  { name: '剩余寿命预测模型', status: '运行中', accuracy: '87.6%', update: `${dateStr} 01:23`, desc: '预测关键部件剩余使用寿命' },
  { name: '维护建议生成模型', status: '运行中', accuracy: '89.3%', update: `${dateStr} 01:38`, desc: '基于诊断结果生成维护建议' },
  { name: '数据插补模型', status: '运行中', accuracy: '84.7%', update: `${dateStr} 01:45`, desc: '对缺失数据进行智能插补' },
  { name: '风暴潮预警模型', status: '待更新', accuracy: '78.9%', update: `${dateStr} 01:52`, desc: '结合浮标数据进行风暴潮预警' },
]

const fullFaults = [
  { id: 'B-HN-0042', loc: '琼州海峡', level: '故障', type: '溶解氧传感器异常', time: `${dateStr} 01:18`, action: '现场校准' },
  { id: 'B-WC-0015', loc: '文昌外海', level: '预警', type: '电池电量偏低', time: `${dateStr} 01:06`, action: '安排补电' },
  { id: 'B-SS-0089', loc: '三亚外海', level: '故障', type: '通信中断', time: `${dateStr} 00:41`, action: '检查天线' },
  { id: 'B-DZ-0033', loc: '儋州近海', level: '预警', type: '水温数据异常', time: `${dateStr} 00:22`, action: '远程重启' },
  { id: 'B-WN-0071', loc: '万宁近海', level: '预警', type: '叶绿素数据异常', time: `${dateStr} 00:08`, action: '数据复核' },
  { id: 'B-HK-0019', loc: '海口近岸', level: '故障', type: '电池膨胀', time: `${dateStr} 00:02`, action: '更换电池' },
  { id: 'B-YP-0056', loc: '洋浦外海', level: '预警', type: '盐度漂移', time: `${dateStr} 00:00`, action: '传感器校准' },
  { id: 'B-XS-0103', loc: '西沙北部', level: '故障', type: '锚链松动', time: `${dateStr} 00:35`, action: '现场检修' },
  { id: 'B-LS-0028', loc: '陵水近海', level: '预警', type: '浊度超标', time: `${dateStr} 00:15`, action: '数据标记' },
  { id: 'B-DZ-0041', loc: '东方近海', level: '正常', type: '例行巡检通过', time: `${dateStr} 01:50`, action: '无需处理' },
]

const fullAdvice = [
  { icon: 'AlertTriangle', title: '通信中断处理', content: '三亚外海浮标(B-SS-0089)通信中断超过1小时，建议尽快派遣检修船检查天线连接与通信模块。', priority: '高' },
  { icon: 'Battery', title: '电池更换计划', content: '文昌外海浮标(B-WC-0015)电池电量降至32%，洋浦外海浮标(B-YP-0056)盐度传感器需校准，建议本周内安排补给船。', priority: '高' },
  { icon: 'Wrench', title: '传感器校准', content: '溶解氧传感器连续异常的浮标需现场校准，建议结合下一次补给任务同步完成。', priority: '中' },
  { icon: 'RadioTower', title: '数据质量提醒', content: '近24小时内有3个浮标出现数据异常波动，建议启用数据插补模型填补缺失值。', priority: '中' },
  { icon: 'Settings', title: '预防性维护', content: '琼州海峡浮标锚链已运行14个月，建议在下一次台风季前进行预防性检查。', priority: '低' },
  { icon: 'Bot', title: '模型更新', content: '风暴潮预警模型准确率降至78.9%，建议更新训练数据集并重新训练。', priority: '中' },
]

const sideSources = ['浮标实时监测数据', '浮标历史数据', '气象数据源', '海浪数据源', '卫星遥感数据']
const modelNames = ['数据质量评估模型', '异常诊断模型', '设备健康评估模型', '剩余寿命预测模型', '维护建议生成模型']

onMounted(() => {
  const tl = gsap.timeline({ defaults: { ease: 'power2.out' } })
  tl.from('.page-hero', { y: 16, opacity: 0, duration: 0.5, ease: 'power3.out' })
  tl.from('.buoy-main-area > .panel', { x: -30, opacity: 0, duration: 0.5, stagger: 0.1 }, '-=0.3')
  tl.from('.buoy-aside > *', { y: 20, opacity: 0, duration: 0.5, stagger: 0.1 }, '-=0.3')
})
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
          <div class="page-hero-icon"><RadioTower :size="28" /></div>
          <div class="page-hero-text">
            <h1>浮标数据诊断智能体</h1>
            <p>面向海洋浮标监测数据质控、异常诊断、设备健康评估与维护预警的智能体</p>
          </div>
          <div class="page-hero-meta">
            <span class="meta-badge"><RadioTower :size="14" /> 浮标监测</span>
          </div>
        </div>

        <!-- 主内容区 -->
        <div class="buoy-main-area">
          <!-- 浮标分布与状态 -->
          <section class="panel ocean-map buoy-map">
            <header class="panel-header"><h2>浮标分布与状态</h2><div class="tabs"></div></header>
            <div class="map-surface buoy-surface" @click="activeBuoy = null">
              <div class="hainan-island-sm">
                <span class="city-sm c-hk">海口</span>
                <span class="city-sm c-sy">三亚</span>
                <span class="city-sm c-wn">万宁</span>
                <span class="city-sm c-df">东方</span>
              </div>
              <span class="sea-label-sm s-south">南海北部</span>
              <span class="sea-label-sm s-qz">琼州海峡</span>
              <span class="sea-label-sm s-xs">西沙方向</span>

              <button
                v-for="point in buoyPoints"
                :key="point.name"
                class="buoy-btn"
                :class="point.status === '故障' ? 'fault' : point.status === '预警' ? 'warn' : 'ok'"
                :style="{ left: point.x + '%', top: point.y + '%' }"
                @click.stop="activeBuoy = point"
              >
                <b></b>
                <span>{{ point.name }}</span>
              </button>

              <div v-if="activeBuoy" class="buoy-popup" :style="{ left: activeBuoy.x + '%', top: activeBuoy.y + '%' }" @click.stop>
                <button class="popup-close" @click="activeBuoy = null">×</button>
                <strong>{{ activeBuoy.name }}</strong>
                <p>状态：{{ activeBuoy.status }}</p>
                <p>类型：{{ activeBuoy.type }}</p>
                <p>电量：{{ activeBuoy.battery }}</p>
              </div>

              <div class="map-legend buoy-legend">
                <strong>状态图例</strong>
                <span class="green">正常</span>
                <span class="amber">预警</span>
                <span class="red">故障</span>
              </div>
            </div>
          </section>

          <!-- 浮标关键指标监测 -->
          <section class="panel micro-panel">
            <header class="panel-header"><h2>浮标关键指标监测</h2><div class="tabs"><button>24小时</button></div></header>
            <div class="micro-grid">
              <article v-for="(item, index) in indicators" :key="item" :class="`tone-${indicatorTones[index]}`">
                <span>{{ item }}</span>
                <strong>{{ indicatorValues[index] }}</strong>
                <small>{{ index > 3 ? '↓ 1' : '↑ 0.2' }}</small>
                <svg viewBox="0 0 100 28" preserveAspectRatio="none"><polyline points="0,15 12,18 25,14 38,12 52,20 68,14 84,17 100,16" /></svg>
              </article>
            </div>
          </section>

          <!-- 诊断结果列表 -->
          <section class="panel detail-table">
            <header class="panel-header">
              <h2>诊断结果列表</h2>
              <div class="tabs"><button class="active">全部</button><button>异常</button><button>预警</button><button>故障</button></div>
            </header>
            <table>
              <thead><tr><th>浮标编号</th><th>位置</th><th>诊断等级</th><th>异常类型</th><th>发生时间</th><th>操作</th></tr></thead>
              <tbody>
                <tr v-for="fault in faults" :key="fault[0]">
                  <td>{{ fault[0] }}</td><td>{{ fault[1] }}</td><td>{{ fault[2] }}</td><td>{{ fault[3] }}</td><td>{{ fault[4] }}</td><td>查看</td>
                </tr>
              </tbody>
            </table>
          </section>

          <!-- 智能运维建议 -->
          <section class="panel qa-advice-panel">
            <header class="panel-header"><h2>智能运维建议</h2><button @click="showMoreAdvice = true">更多 ›</button></header>
            <article><AlertTriangle :size="18" /><span>优先处理通信中断浮标，建议尽快检查天线连接情况。</span></article>
            <article><Wrench :size="18" /><span>计划维护溶解氧传感器，连续异常设备需要现场校准。</span></article>
            <article><Battery :size="18" /><span>电池更换建议：低于20%的浮标建议安排补电或更换电池。</span></article>
          </section>
        </div>
      </div>

      <!-- 侧边栏 -->
      <aside class="agent-search-aside buoy-aside min-w-0">
        <section class="panel side-feed-panel">
          <header class="panel-header"><h2>数据来源</h2><button @click="showMoreSources = true">更多 ›</button></header>
          <ul><li v-for="source in sideSources" :key="source">{{ source }} <span>正常</span></li></ul>
        </section>

        <section class="panel side-feed-panel">
          <header class="panel-header"><h2>模型运行状态</h2><button @click="showMoreModels = true">更多 ›</button></header>
          <ul><li v-for="model in modelNames" :key="model">{{ model }} <span>运行中</span></li></ul>
        </section>

        <section class="panel sensor-panel">
          <header class="panel-header"><h2>传感器健康度</h2></header>
          <article v-for="row in sensorRows" :key="row[0]" :class="{ warn: row[2] === '预警' }">
            <span>{{ row[0] }}</span>
            <i><em :style="{ width: row[1] }"></em></i>
            <b>{{ row[1] }}</b>
            <small>{{ row[2] }}</small>
          </article>
        </section>

        <section class="panel trend-panel">
          <header class="panel-header"><h2>异常波动分析</h2><div class="tabs"><button>溶解氧</button><button>近24小时</button></div></header>
          <div class="line-chart">
            <svg viewBox="0 0 100 45" preserveAspectRatio="none">
              <polyline points="0,32 10,25 20,28 30,20 40,24 50,16 60,18 70,26 80,29 90,33 100,31" />
              <polyline class="red-line" points="0,20 100,20" />
              <polyline class="green-line" points="0,35 100,35" />
            </svg>
          </div>
        </section>

        <section class="panel distribution-panel fault-distribution">
          <header class="panel-header"><h2>故障类型分布</h2><button @click="showMoreFaults = true">更多 ›</button></header>
          <div class="donut">故障总数<br /><strong>11</strong></div>
          <ul>
            <li><span>传感器异常</span><b>5</b><em>45.5%</em></li>
            <li><span>通信异常</span><b>3</b><em>27.3%</em></li>
            <li><span>供电异常</span><b>2</b><em>18.2%</em></li>
            <li><span>结构异常</span><b>1</b><em>9.0%</em></li>
          </ul>
        </section>
      </aside>
    </div>

    <!-- 数据来源弹窗 -->
    <AppModal v-model:visible="showMoreSources" :title="`数据来源详情（共 ${fullSources.length} 个）`" width="900px">
      <div class="modal-scroll">
        <table class="full-table">
          <thead><tr><th>数据源</th><th>状态</th><th>延迟</th><th>类型</th><th>覆盖范围</th><th>更新频率</th></tr></thead>
          <tbody>
            <tr v-for="s in fullSources" :key="s.name">
              <td>{{ s.name }}</td>
              <td><span :class="s.status === '正常' ? 'status-ok' : 'status-warn'">{{ s.status }}</span></td>
              <td>{{ s.delay }}</td><td>{{ s.type }}</td><td>{{ s.coverage }}</td><td>{{ s.freq }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #footer><button class="confirm-btn" @click="showMoreSources = false">关闭</button></template>
    </AppModal>

    <!-- 模型运行状态弹窗 -->
    <AppModal v-model:visible="showMoreModels" :title="`模型运行状态（共 ${fullModels.length} 个）`" width="1000px">
      <div class="modal-scroll">
        <table class="full-table">
          <thead><tr><th>模型名称</th><th>状态</th><th>准确率</th><th>更新时间</th><th>描述</th></tr></thead>
          <tbody>
            <tr v-for="m in fullModels" :key="m.name">
              <td>{{ m.name }}</td>
              <td><span :class="m.status === '运行中' ? 'status-ok' : 'status-warn'">{{ m.status }}</span></td>
              <td>{{ m.accuracy }}</td><td>{{ m.update }}</td><td>{{ m.desc }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #footer><button class="confirm-btn" @click="showMoreModels = false">关闭</button></template>
    </AppModal>

    <!-- 故障类型分布弹窗 -->
    <AppModal v-model:visible="showMoreFaults" :title="`故障详情（共 ${fullFaults.length} 条）`" width="1000px">
      <div class="modal-scroll">
        <table class="full-table">
          <thead><tr><th>浮标编号</th><th>位置</th><th>等级</th><th>异常类型</th><th>发生时间</th><th>建议操作</th></tr></thead>
          <tbody>
            <tr v-for="f in fullFaults" :key="f.id">
              <td>{{ f.id }}</td><td>{{ f.loc }}</td>
              <td><span :class="f.level === '故障' ? 'status-fault' : f.level === '预警' ? 'status-warn' : 'status-ok'">{{ f.level }}</span></td>
              <td>{{ f.type }}</td><td>{{ f.time }}</td><td>{{ f.action }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #footer><button class="confirm-btn" @click="showMoreFaults = false">关闭</button></template>
    </AppModal>

    <!-- 智能运维建议弹窗 -->
    <AppModal v-model:visible="showMoreAdvice" :title="`智能运维建议（共 ${fullAdvice.length} 条）`" width="800px">
      <div class="advice-grid">
        <div v-for="(item, idx) in fullAdvice" :key="idx" class="advice-card" :class="`priority-${item.priority === '高' ? 'high' : item.priority === '中' ? 'mid' : 'low'}`">
          <div class="advice-header">
            <component :is="item.icon === 'AlertTriangle' ? AlertTriangle : item.icon === 'Battery' ? Battery : item.icon === 'Wrench' ? Wrench : item.icon === 'RadioTower' ? RadioTower : item.icon === 'Settings' ? Settings : Bot" :size="20" />
            <strong>{{ item.title }}</strong>
            <span class="priority-tag">{{ item.priority }}优先级</span>
          </div>
          <p class="advice-content">{{ item.content }}</p>
        </div>
      </div>
      <template #footer><button class="confirm-btn" @click="showMoreAdvice = false">关闭</button></template>
    </AppModal>
  </section>
</template>

<style scoped>
.buoy-main-area { display: flex; flex-direction: column; gap: 16px; }
.buoy-aside { display: flex; flex-direction: column; gap: 16px; }

/* ── 地图 ── */
.buoy-surface {
  position: relative;
  height: 280px;
  overflow: hidden;
  border-radius: 10px;
  background: linear-gradient(160deg, #05263f, #0a3a5c 60%, #0e4a70);
  border: 1px solid rgba(56, 160, 220, 0.4);
}

.hainan-island-sm {
  position: absolute;
  left: 22%; top: 24%;
  width: 140px; height: 180px;
  background: linear-gradient(145deg, rgba(37, 94, 70, 0.92), rgba(24, 71, 58, 0.98));
  clip-path: polygon(42% 0, 70% 10%, 88% 32%, 78% 62%, 55% 88%, 28% 100%, 8% 78%, 0 44%, 16% 14%);
  box-shadow: inset 0 0 40px rgba(42, 245, 178, 0.16);
}
.city-sm { position: absolute; color: #fff; font-size: 12px; font-weight: 600; pointer-events: none; text-shadow: 0 0 4px #00182d, 0 0 8px #00b7ff; }
.c-hk { left: 42%; top: 8%; }
.c-sy { left: 40%; bottom: 10%; }
.c-wn { right: 8%; top: 48%; }
.c-df { left: 6%; top: 46%; }
.sea-label-sm { position: absolute; color: rgba(255,255,255,0.5); font-size: 11px; pointer-events: none; }
.s-south { left: 66%; top: 14%; }
.s-qz { left: 36%; top: 16%; }
.s-xs { left: 80%; top: 60%; }

.buoy-btn {
  position: absolute;
  z-index: 12;
  transform: translate(-6px, -50%);
  border: none; background: transparent;
  cursor: pointer; color: #fff;
  display: flex; align-items: center; gap: 6px;
}
.buoy-btn b { flex-shrink: 0; width: 12px; height: 12px; border-radius: 50%; border: 2px solid #fff; }
.buoy-btn span { font-size: 11px; white-space: nowrap; pointer-events: none; opacity: 0; transition: opacity 0.2s; text-shadow: 0 0 6px #00182d; background: rgba(3,19,36,0.55); padding: 1px 4px; border-radius: 3px; }
.buoy-btn:hover span { opacity: 1; }
.buoy-btn.ok b { background: #22c55e; box-shadow: 0 0 8px rgba(34,197,94,0.8); }
.buoy-btn.warn b { background: #f59e0b; box-shadow: 0 0 8px rgba(245,158,11,0.8); }
.buoy-btn.fault b { background: #ef4444; box-shadow: 0 0 8px rgba(239,68,68,0.8); }

.buoy-popup {
  position: absolute; z-index: 20; width: 160px;
  padding: 10px 12px; transform: translate(14px, -50%);
  background: rgba(5,24,48,0.94); border: 1px solid rgba(48,145,255,0.65);
  border-radius: 8px; color: #fff; font-size: 12px;
  box-shadow: 0 8px 22px rgba(0,0,0,0.35);
}
.buoy-popup p { margin: 4px 0 0; color: #cde8ff; }
.popup-close { position: absolute; right: 6px; top: 4px; border: none; background: transparent; color: #9ed8ff; font-size: 16px; cursor: pointer; }

.buoy-legend {
  position: absolute; right: 12px; top: 12px; z-index: 10;
  width: 110px; padding: 10px;
  background: rgba(5,24,48,0.9); border: 1px solid rgba(48,145,255,0.55);
  border-radius: 8px; color: #fff; font-size: 11px;
}
.buoy-legend strong { display: block; margin-bottom: 4px; font-size: 12px; }
.buoy-legend span { display: block; margin-top: 5px; }
.buoy-legend span::before { content: ''; display: inline-block; width: 8px; height: 8px; margin-right: 6px; border-radius: 2px; background: #6ab7ff; }
.buoy-legend .green::before { background: #22c55e; }
.buoy-legend .amber::before { background: #f59e0b; }
.buoy-legend .red::before { background: #ef4444; }

/* ── 传感器 ── */
.sensor-panel article { display: grid; grid-template-columns: 1fr 100px 42px 36px; align-items: center; gap: 8px; padding: 8px 0; font-size: 13px; color: #b9d6ee; }
.sensor-panel article span { color: #dff7ff; }
.sensor-panel article i { height: 6px; background: rgba(59,130,246,0.15); border-radius: 3px; overflow: hidden; }
.sensor-panel article em { display: block; height: 100%; background: #22c55e; border-radius: 3px; transition: width 0.6s ease; }
.sensor-panel article.warn em { background: #f59e0b; }
.sensor-panel article b { text-align: right; color: #8fb9df; font-size: 12px; }
.sensor-panel article small { font-size: 11px; }
.sensor-panel article.warn small { color: #f59e0b; }

/* ── 趋势图 ── */
.line-chart svg { width: 100%; height: 100px; }
.line-chart polyline { fill: none; stroke: #3b82f6; stroke-width: 2; }
.line-chart .red-line { stroke: #ef4444; stroke-width: 1; stroke-dasharray: 4 3; }
.line-chart .green-line { stroke: #22c55e; stroke-width: 1; stroke-dasharray: 4 3; }

/* ── 故障分布 ── */
.fault-distribution .donut { text-align: center; padding: 16px; color: #8fb9df; font-size: 13px; }
.fault-distribution .donut strong { display: block; font-size: 28px; color: #fff; margin-top: 4px; }
.fault-distribution ul { list-style: none; padding: 0 12px 12px; }
.fault-distribution li { display: flex; align-items: center; gap: 8px; padding: 6px 0; font-size: 12px; color: #b9d6ee; }
.fault-distribution li span { flex: 1; }
.fault-distribution li b { color: #dff7ff; }
.fault-distribution li em { color: #8fb9df; font-style: normal; font-size: 11px; }

/* ── 弹窗内容 ── */
.modal-scroll { overflow-x: auto; }
.full-table { width: 100%; min-width: 700px; border-collapse: collapse; }
.full-table th, .full-table td { padding: 12px 10px; border-bottom: 1px solid rgba(39,151,255,0.12); text-align: left; color: #b9d6ee; }
.full-table th { position: sticky; top: 0; z-index: 1; font-weight: 600; color: #fff; background: rgba(7,28,52,0.98); }
.confirm-btn { padding: 8px 24px; background: #10b981; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; }
.confirm-btn:hover { background: #059669; }
.status-ok { color: #10b981; }
.status-warn { color: #f59e0b; }
.status-fault { color: #ef4444; }

/* ── 建议卡片 ── */
.advice-grid { display: flex; flex-direction: column; gap: 12px; padding: 16px 0; }
.advice-card { background: rgba(30,55,91,0.6); border-radius: 12px; padding: 14px 16px; border-left: 3px solid; }
.advice-card.priority-high { border-left-color: #ef4444; }
.advice-card.priority-mid { border-left-color: #f59e0b; }
.advice-card.priority-low { border-left-color: #10b981; }
.advice-header { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; color: #fff; }
.priority-tag { font-size: 11px; padding: 2px 8px; border-radius: 12px; background: rgba(255,255,255,0.1); margin-left: auto; }
.advice-content { color: #cbd5e1; font-size: 14px; line-height: 1.5; margin: 0; }
</style>
