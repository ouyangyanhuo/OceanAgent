<script setup>
import { AlertTriangle, Battery, Bot, FileText, RadioTower, Settings, Share2, Wrench } from 'lucide-vue-next'
import MetricCard from './MetricCard.vue'

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

const faults = [
  ['B-JS-0128', '黄海北部', '故障', '溶解氧传感器异常', '2025-05-24 10:18'],
  ['B-SD-0086', '山东近岸', '预警', '电池电量偏低', '2025-05-24 09:56'],
  ['B-LYG-0053', '连云港外海', '故障', '通信中断', '2025-05-24 09:41'],
  ['B-YZ-0176', '长江口外', '预警', '水温数据异常', '2025-05-24 09:12'],
  ['B-ZS-0037', '舟山群岛', '预警', '叶绿素数据异常', '2025-05-24 08:58'],
]
</script>

<template>
  <section class="page agent-detail-page">
    <div class="agent-detail-head">
      <div class="agent-orb buoy"><RadioTower :size="34" /></div>
      <div><h1>浮标数据诊断智能体 <span>在线</span></h1><p>面向海洋浮标监测数据质控、异常诊断、设备健康评估与维护预警的智能体</p></div>
      <div class="page-actions"><button><Bot :size="17" />智能问答</button><button><FileText :size="17" />诊断报告</button><button><Settings :size="17" />诊断配置</button><button><Share2 :size="17" />分享</button></div>
    </div>
    <div class="metrics-grid detail-metrics"><MetricCard v-for="metric in metrics" :key="metric.label" :metric="metric" /></div>
    <div class="detail-grid buoy-grid">
      <section class="panel ocean-map buoy-map">
        <header class="panel-header"><h2>浮标分布与状态</h2><div class="tabs"><button>全部海域</button></div></header>
        <div class="map-surface buoy-surface">
          <span class="place p1">青岛市</span><span class="place p2">日照市</span><span class="place p3">连云港市</span><span class="place p4">舟山市</span>
          <i v-for="n in 14" :key="n" :class="`buoy-dot b${n}`"></i>
          <div class="map-tools"><button>+</button><button>-</button><button>⌖</button><button>◎</button></div>
          <div class="map-legend buoy-legend"><strong>状态图例</strong><span class="green">正常(111)</span><span class="amber">预警(6)</span><span class="red">故障(11)</span><span>离线(8)</span><strong>海流流速</strong><span class="blue">&gt;1.5</span><span>0.2-0.5</span></div>
        </div>
      </section>

      <section class="panel micro-panel">
        <header class="panel-header"><h2>浮标关键指标监测</h2><div class="tabs"><button>24小时</button></div></header>
        <div class="micro-grid">
          <article v-for="(item,index) in ['水温','盐度','溶解氧','叶绿素-a','电池电量','通信质量']" :key="item" :class="`tone-${['blue','teal','green','violet','amber','violet'][index]}`">
            <span>{{ item }}</span><strong>{{ ['17.6','32.1','6.2','1.48','78','92'][index] }}</strong><small>{{ index > 3 ? '↓ 1' : '↑ 0.2' }}</small>
            <svg viewBox="0 0 100 28" preserveAspectRatio="none"><polyline points="0,15 12,18 25,14 38,12 52,20 68,14 84,17 100,16" /></svg>
          </article>
        </div>
      </section>

      <section class="panel side-feed-panel detail-side"><header class="panel-header"><h2>数据来源</h2><button>更多 ›</button></header><ul><li v-for="source in ['浮标实时监测数据','浮标历史数据','气象数据源','海浪数据源','卫星遥感数据']" :key="source">{{ source }} <span>正常</span></li></ul></section>
      <section class="panel side-feed-panel detail-side"><header class="panel-header"><h2>模型运行状态</h2><button>更多 ›</button></header><ul><li v-for="model in ['数据质量评估模型','异常诊断模型','设备健康评估模型','剩余寿命预测模型','维护建议生成模型']" :key="model">{{ model }} <span>运行中</span></li></ul></section>

      <section class="panel detail-table">
        <header class="panel-header"><h2>诊断结果列表</h2><div class="tabs"><button class="active">全部</button><button>异常</button><button>预警</button><button>故障</button></div></header>
        <table><thead><tr><th>浮标编号</th><th>位置</th><th>诊断等级</th><th>异常类型</th><th>发生时间</th><th>操作</th></tr></thead><tbody><tr v-for="fault in faults" :key="fault[0]"><td>{{ fault[0] }}</td><td>{{ fault[1] }}</td><td>{{ fault[2] }}</td><td>{{ fault[3] }}</td><td>{{ fault[4] }}</td><td>查看</td></tr></tbody></table>
      </section>

      <section class="panel sensor-panel">
        <header class="panel-header"><h2>传感器健康度</h2></header>
        <article v-for="row in sensorRows" :key="row[0]" :class="{ warn: row[2] === '预警' }"><span>{{ row[0] }}</span><i><em :style="{ width: row[1] }"></em></i><b>{{ row[1] }}</b><small>{{ row[2] }}</small></article>
      </section>

      <section class="panel trend-panel">
        <header class="panel-header"><h2>异常波动分析</h2><div class="tabs"><button>溶解氧</button><button>近24小时</button></div></header>
        <div class="line-chart"><svg viewBox="0 0 100 45" preserveAspectRatio="none"><polyline points="0,32 10,25 20,28 30,20 40,24 50,16 60,18 70,26 80,29 90,33 100,31" /><polyline class="red-line" points="0,20 100,20" /><polyline class="green-line" points="0,35 100,35" /></svg></div>
      </section>

      <section class="panel distribution-panel fault-distribution">
        <header class="panel-header"><h2>故障类型分布</h2><button>更多 ›</button></header>
        <div class="donut">故障总数<br /><strong>11</strong></div>
        <ul><li><span>传感器异常</span><b>5</b><em>45.5%</em></li><li><span>通信异常</span><b>3</b><em>27.3%</em></li><li><span>供电异常</span><b>2</b><em>18.2%</em></li><li><span>结构异常</span><b>1</b><em>9.0%</em></li></ul>
      </section>

      <section class="panel qa-advice-panel">
        <header class="panel-header"><h2>智能运维建议</h2><button>更多 ›</button></header>
        <article><AlertTriangle :size="18" /><span>优先处理通信中断浮标，建议尽快检查天线连接情况。</span></article>
        <article><Wrench :size="18" /><span>计划维护溶解氧传感器，连续异常设备需要现场校准。</span></article>
        <article><Battery :size="18" /><span>电池更换建议：低于20%的浮标建议安排补电或更换电池。</span></article>
      </section>
    </div>
  </section>
</template>
