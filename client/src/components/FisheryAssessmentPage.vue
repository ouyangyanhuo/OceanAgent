<script setup>
import { Anchor, Bot, FileText, Fish, RadioTower, Settings, Share2, ShieldCheck } from 'lucide-vue-next'
import MetricCard from './MetricCard.vue'

const metrics = [
  { label: '综合适宜度', value: '86.3 /100', trend: '12.6%', tone: 'blue', sparkline: [18, 22, 21, 30, 26, 36, 32, 41, 37, 48, 42, 55] },
  { label: '优质渔场数量', value: '28 处', trend: '16.7%', tone: 'cyan', sparkline: [16, 21, 24, 22, 32, 29, 38, 35, 44, 40, 47, 56] },
  { label: '资源丰度指数', value: '134.7', trend: '11.5%', tone: 'teal', sparkline: [20, 25, 23, 31, 29, 37, 35, 44, 39, 51, 45, 58] },
  { label: '未来48小时作业窗口', value: '36 h', trend: '18.2%', tone: 'green', sparkline: [15, 20, 24, 29, 35, 41, 44, 43, 39, 34, 28, 22] },
]

const ranking = [
  ['舟山外海渔场', '92.4', '156.3', '带鱼、黄鱼、鲐鱼', '05-24 06:00 - 24:00'],
  ['吕泗渔场', '88.7', '141.8', '小黄鱼、带鱼、鲳鱼', '05-24 08:00 - 23:00'],
  ['长江口外渔场', '85.1', '132.6', '刀鱼、鲈鱼、黄鱼', '05-24 05:00 - 22:00'],
  ['胶州湾渔场', '82.3', '125.4', '鲅鱼、海鲫、带鱼', '05-24 07:00 - 21:00'],
  ['东海中部渔场', '79.6', '118.9', '鱿鱼、秋刀鱼、鲐鱼', '05-24 09:00 - 20:00'],
]

const indicators = ['表层水温', '叶绿素a', '盐度', '溶解氧', '有效波高', '生物量指数']
const sideSources = ['卫星遥感', '海洋浮标网', '渔船AIS', '渔获上报', '声学探测', '历史渔情库']
</script>

<template>
  <section class="page agent-detail-page">
    <div class="agent-detail-head">
      <div class="agent-orb fishery"><Fish :size="34" /></div>
      <div>
        <h1>渔场评估智能体 <span>在线</span></h1>
        <p>面向渔场环境评估、资源丰度分析、作业适宜性研判与渔情预测的智能体</p>
      </div>
      <div class="page-actions">
        <button><Bot :size="17" />智能问答</button>
        <button><FileText :size="17" />评估报告</button>
        <button><Settings :size="17" />评估配置</button>
        <button><Share2 :size="17" />分享</button>
      </div>
    </div>

    <div class="metrics-grid detail-metrics">
      <MetricCard v-for="metric in metrics" :key="metric.label" :metric="metric" />
    </div>

    <div class="detail-grid fishery-grid">
      <section class="panel ocean-map fishery-map">
        <header class="panel-header"><h2>渔场适宜性分布</h2><div class="tabs"><button class="active">表层(0-10m)</button><button>适宜度综合</button></div></header>
        <div class="map-surface heatmap">
          <span class="place p1">青岛</span><span class="place p2">日照</span><span class="place p3">连云港</span><span class="place p4">舟山</span>
          <i class="hot h1"></i><i class="hot h2"></i><i class="hot h3"></i><i class="hot h4"></i>
          <b class="station s1"></b><b class="station s2"></b><b class="station s3"></b><b class="station s4"></b><b class="station s5"></b>
          <div class="map-tools"><button>+</button><button>-</button><button>⌖</button></div>
          <div class="map-legend"><strong>适宜度分级</strong><span class="red">极高</span><span class="amber">较高</span><span class="green">较优</span><span class="blue">低</span><span>鱼群热点</span><span>监测点</span></div>
        </div>
      </section>

      <section class="panel micro-panel">
        <header class="panel-header"><h2>关键评估指标</h2><div class="tabs"><button>表层</button><button>24小时</button></div></header>
        <div class="micro-grid">
          <article v-for="(item, index) in indicators" :key="item" :class="`tone-${['blue','teal','cyan','green','violet','amber'][index]}`">
            <span>{{ item }}</span><strong>{{ ['18.6','2.18','32.4','6.12','1.32','142.6'][index] }}</strong><small>↑ {{ ['0.3','0.24','0.1','0.18','0.12','14.8'][index] }}</small>
            <svg viewBox="0 0 100 28" preserveAspectRatio="none"><polyline points="0,22 12,18 25,20 38,12 52,16 68,13 84,19 100,10" /></svg>
          </article>
        </div>
      </section>

      <section class="panel side-feed-panel detail-side">
        <header class="panel-header"><h2>数据来源</h2><button>更多 ›</button></header>
        <ul><li v-for="source in sideSources" :key="source">{{ source }} <span>正常</span></li></ul>
      </section>

      <section class="panel side-feed-panel detail-side">
        <header class="panel-header"><h2>模型运行状态</h2><button>更多 ›</button></header>
        <ul><li v-for="model in ['渔场适宜性评估模型','资源丰度预测模型','鱼群热点识别模型','作业窗口研判模型','渔情短期预测模型']" :key="model">{{ model }} <span>运行中</span></li></ul>
      </section>

      <section class="panel detail-table">
        <header class="panel-header"><h2>渔场排行</h2><button>更多 ›</button></header>
        <table><thead><tr><th>排名</th><th>渔场名称</th><th>综合适宜度</th><th>资源丰度</th><th>主要目标鱼种</th><th>最佳作业窗口</th></tr></thead>
          <tbody><tr v-for="(row, index) in ranking" :key="row[0]"><td>{{ index + 1 }}</td><td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td><td>{{ row[4] }}</td></tr></tbody></table>
      </section>

      <section class="panel trend-panel"><header class="panel-header"><h2>趋势预测</h2><div class="tabs"><button class="active">7天</button></div></header><div class="line-chart"><svg viewBox="0 0 100 45" preserveAspectRatio="none"><polyline points="0,28 10,23 20,25 30,30 40,27 50,24 60,20 70,15 80,12 90,15 100,11" /><polyline class="green-line" points="0,35 10,31 20,34 30,37 40,33 50,31 60,29 70,26 80,22 90,18 100,14" /></svg></div></section>

      <section class="panel detail-table compact">
        <header class="panel-header"><h2>目标鱼种分析</h2><button>更多 ›</button></header>
        <table><tbody><tr v-for="fish in ['带鱼','小黄鱼','鲈鱼','鲐鱼','鱿鱼']" :key="fish"><td>{{ fish }}</td><td>资源丰度 {{ Math.round(90 + fish.length * 18) }}</td><td>↑ {{ (fish.length * 2.7).toFixed(1) }}%</td><td>{{ fish.length * 5 + 8 }}%</td></tr></tbody></table>
      </section>

      <section class="panel qa-advice-panel">
        <header class="panel-header"><h2>智能作业建议</h2><button>更多 ›</button></header>
        <article><Anchor :size="18" /><span>舟山外海东北部海域综合适宜度最高，建议优先作业。</span></article>
        <article><ShieldCheck :size="18" /><span>未来48小时内，05-24 06:00 - 24:00 为最佳作业窗口。</span></article>
        <article><Fish :size="18" /><span>带鱼、小黄鱼资源丰度较高，建议以此为主要捕捞目标。</span></article>
        <article><RadioTower :size="18" /><span>东南风3-4级，浪高适中，注意局部对流天气变化。</span></article>
      </section>
    </div>
  </section>
</template>
