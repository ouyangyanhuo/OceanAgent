<script setup>
import { AlertTriangle, Bot, FileText, Fuel, Navigation, Settings, Share2, ShipWheel } from 'lucide-vue-next'
import MetricCard from './MetricCard.vue'

const metrics = [
  { label: '当前推荐航线', value: 'A1 航线', trend: '推荐中', tone: 'blue', sparkline: [15, 18, 23, 28, 35, 42, 50, 58, 64, 71, 77, 83] },
  { label: '预计航行时间', value: '78.6 小时', trend: '6.9%', tone: 'amber', sparkline: [46, 42, 38, 36, 35, 33, 31, 30, 29, 27, 26, 24] },
  { label: '节油率', value: '12.4%', trend: '28.7吨', tone: 'teal', sparkline: [20, 24, 23, 29, 32, 31, 36, 38, 39, 42, 45, 48] },
  { label: '高风险海域', value: '2 处', trend: '1处', tone: 'amber', sparkline: [38, 34, 30, 26, 22, 20, 18, 17, 16, 15, 14, 13] },
]

const plans = [
  ['A1 (推荐)', '1,468', '78.6', '203.6', '12.4%', '低', '★★★★★'],
  ['A2 (备选)', '1,586', '84.2', '226.8', '4.6%', '中', '★★★★☆'],
  ['A3 (备选)', '1,634', '87.5', '238.9', '1.1%', '高', '★★★☆☆'],
]

const routeMetrics = ['风速', '浪高', '海流速度', '能见度', '预计燃油消耗', 'ETA 偏差']
</script>

<template>
  <section class="page agent-detail-page">
    <div class="agent-detail-head">
      <div class="agent-orb route"><ShipWheel :size="34" /></div>
      <div><h1>航线优化智能体 <span>在线</span></h1><p>面向船舶航线规划、气象海况融合分析、风险规避与能效优化的智能体</p></div>
      <div class="page-actions"><button><Bot :size="17" />智能问答</button><button><FileText :size="17" />报告生成</button><button><Settings :size="17" />优化配置</button><button><Share2 :size="17" />分享</button></div>
    </div>
    <div class="metrics-grid detail-metrics"><MetricCard v-for="metric in metrics" :key="metric.label" :metric="metric" /></div>
    <div class="detail-grid route-grid">
      <section class="panel ocean-map route-map">
        <header class="panel-header"><h2>航线优化地图</h2><div class="tabs"><button class="active">综合视图</button></div></header>
        <div class="map-surface route-surface">
          <span class="place p1">上海</span><span class="place p2">宁波</span><span class="place p3">台州</span><span class="place p4">厦门</span><span class="place p5">那霸</span>
          <svg viewBox="0 0 100 60" preserveAspectRatio="none"><polyline class="route-main" points="18,12 27,20 38,24 50,34 63,40 76,48 88,52" /><polyline class="route-alt" points="18,12 34,18 48,22 61,25 77,31 90,40" /><polyline class="route-alt purple" points="28,22 30,36 44,42 60,46 78,50" /></svg>
          <i class="danger-zone dz1"></i><i class="danger-zone dz2"></i><i class="weather-zone wz1"></i>
          <b class="port start">起点</b><b class="port end">终点</b><div class="map-tools"><button>+</button><button>-</button><button>▧</button><button>⚙</button></div>
        </div>
      </section>
      <section class="panel micro-panel"><header class="panel-header"><h2>关键航线指标</h2><div class="tabs"><button>24小时</button></div></header><div class="micro-grid"><article v-for="(item,index) in routeMetrics" :key="item" :class="`tone-${['green','blue','violet','cyan','teal','violet'][index]}`"><span>{{ item }}</span><strong>{{ ['8.6','2.1','1.2','9.6','203.6','-1.3'][index] }}</strong><small>{{ index === 2 ? '↑ 0.2' : '↓ 0.8' }}</small><svg viewBox="0 0 100 28" preserveAspectRatio="none"><polyline points="0,18 12,15 25,12 38,13 52,19 68,15 84,16 100,13" /></svg></article></div></section>
      <section class="panel side-feed-panel detail-side"><header class="panel-header"><h2>数据来源</h2><button>更多 ›</button></header><ul><li v-for="source in ['全球数值预报模式(GFS)','全球波浪模型(WW3)','全球海流模型(HYCOM)','港口AIS实时数据','船舶历史航行数据','海事通告与公告']" :key="source">{{ source }} <span>正常</span></li></ul></section>
      <section class="panel side-feed-panel detail-side"><header class="panel-header"><h2>模型运行状态</h2><button>更多 ›</button></header><ul><li v-for="model in ['航线优化模型','气候融合模型','海况风险评估模型','燃油消耗预测模型','ETA 预测模型']" :key="model">{{ model }} <span>运行中</span></li></ul></section>
      <section class="panel detail-table"><header class="panel-header"><h2>航线方案对比</h2></header><table><thead><tr><th>方案</th><th>航行距离</th><th>预计时间</th><th>燃油消耗</th><th>节油率</th><th>风险等级</th><th>综合评分</th></tr></thead><tbody><tr v-for="row in plans" :key="row[0]"><td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td><td>{{ row[4] }}</td><td>{{ row[5] }}</td><td>{{ row[6] }}</td></tr></tbody></table></section>
      <section class="panel trend-panel"><header class="panel-header"><h2>趋势预测</h2><div class="tabs"><button class="active">24小时</button></div></header><div class="line-chart"><svg viewBox="0 0 100 45" preserveAspectRatio="none"><polyline points="0,28 10,25 20,19 30,20 40,24 50,18 60,22 70,16 80,21 90,18 100,23" /><polyline class="green-line" points="0,20 10,18 20,14 30,15 40,19 50,12 60,13 70,19 80,22 90,16 100,18" /></svg></div></section>
      <section class="panel detail-table compact"><header class="panel-header"><h2>航段风险列表</h2><button>更多 ›</button></header><table><tbody><tr v-for="row in ['S1 强风大浪 高','S2 对流天气 中','S3 海流强 中','S4 能见度低 低','S5 适航风险 低']" :key="row"><td>{{ row }}</td><td>05-24 14:00 - 20:00</td></tr></tbody></table></section>
      <section class="panel qa-advice-panel"><header class="panel-header"><h2>智能优化建议</h2></header><article><Navigation :size="18" /><span>推荐当前推荐航线 A1，综合能效与风险表现最佳。</span></article><article><AlertTriangle :size="18" /><span>关注强风大浪区域，建议巡航阶段保持安全距离。</span></article><article><Fuel :size="18" /><span>优化航速可进一步节油，预计节省燃油 2.3 吨。</span></article></section>
    </div>
  </section>
</template>
