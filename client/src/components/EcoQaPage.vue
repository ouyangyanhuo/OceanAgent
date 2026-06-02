<script setup>
import { Bot, Brain, Cloud, Database, Flame, Leaf, MessageSquare, Send, Settings, Share2 } from 'lucide-vue-next'
import MetricCard from './MetricCard.vue'

const metrics = [
  { label: '今日问答量', value: '2,184', trend: '18.7%', tone: 'blue', sparkline: [25, 24, 31, 28, 37, 33, 44, 32, 38, 40, 36, 48] },
  { label: '知识节点命中', value: '56,782', trend: '9.6%', tone: 'cyan', sparkline: [26, 33, 30, 36, 34, 41, 38, 46, 42, 49, 47, 55] },
  { label: '问答准确率', value: '92.6%', trend: '2.1%', tone: 'teal', sparkline: [32, 34, 31, 38, 36, 40, 39, 44, 42, 47, 45, 50] },
  { label: '热点生态主题', value: '海草床、珊瑚礁、红树林', trend: '5个', tone: 'rose', sparkline: [18, 20, 26, 22, 31, 25, 34, 30, 39, 35, 44, 41] },
]

const messages = [
  ['user', '什么是海草床？它对海洋生态系统有哪些作用？'],
  ['bot', '海草床是由海草植物在浅海海底形成的重要生态系统。它具有重要的生态功能：提供栖息与繁殖场所、固定沉积物改善水质、吸收和储存碳、支撑渔业资源并促进生物多样性。'],
  ['user', '中国沿海有哪些典型的海草床分布区域？'],
  ['bot', '中国海草床主要分布在广东沿江、福建厦门、海南三亚、广西北海、浙江舟山等沿海海域。其中海南的海草床面积较大，种类丰富，以海菖蒲、卵叶喜盐草等常见。'],
  ['user', '赤潮发生的原因有哪些？如何预警？'],
  ['bot', '赤潮通常由营养盐富集、水温升高、海流静稳、光照充足等因素引发。预警应结合遥感监测、浮标温盐、水质检测与历史数据建模进行综合评估。'],
  ['user', '如果要做近岸生态修复，应该优先关注哪些指标？'],
  ['bot', '近岸生态修复应优先关注水体营养盐、溶解氧、透明度、底质类型、生境连通性、关键物种恢复情况和人为扰动强度。对海草床、红树林和珊瑚礁等不同生态系统，还需要分别跟踪覆盖度、幼苗成活率、白化率和群落结构变化。'],
]

const cards = [
  ['珊瑚礁生态系统', '生命热区', '提供栖息地、食物和护岸屏障，是高价值海洋生态服务。', '98%', '126'],
  ['海草床生态系统', '生态系统', '高生产力的浅海生态系统，具有固碳、净化水质和保护海岸功能。', '95%', '98'],
  ['红树林生态系统', '生态系统', '分布在热带与亚热带海岸，具有防波护岸和碳汇功能。', '97%', '110'],
  ['赤潮事件', '灾害风险', '由藻类异常增殖引发，可能导致缺氧、鱼类死亡和生态灾害。', '93%', '76'],
]

const records = [
  ['2025-05-24 10:21', '海草床退化的主要原因？', '海草床', '知识库+文献', '0.95'],
  ['2025-05-24 10:18', '赤潮预警的技术手段有哪些？', '赤潮', '监测+模型', '0.93'],
  ['2025-05-24 10:13', '珊瑚礁保护措施？', '珊瑚礁', '知识库+文献', '0.94'],
  ['2025-05-24 10:07', '近岸生态修复有哪些策略？', '生态修复', '知识库+案例', '0.91'],
]
</script>

<template>
  <section class="page qa-page">
    <div class="qa-hero">
      <div class="agent-orb"><MessageSquare :size="34" /></div>
      <div>
        <h1>海洋生态问答智能体 <span>在线</span></h1>
        <p>面向海洋生态知识问答、知识检索、关系推理与科普服务的智能体</p>
      </div>
      <div class="page-actions">
        <button><Bot :size="17" />智能问答</button>
        <button><Database :size="17" />知识卡片</button>
        <button><Settings :size="17" />对话配置</button>
        <button><Share2 :size="17" />分享</button>
      </div>
    </div>

    <div class="metrics-grid qa-metrics">
      <MetricCard v-for="metric in metrics" :key="metric.label" :metric="metric" />
    </div>

    <div class="qa-grid">
      <section class="panel chat-panel">
        <header class="panel-header"><h2>生态问答对话</h2><button>清空对话</button></header>
        <div class="messages">
          <article v-for="(message, index) in messages" :key="index" :class="message[0]">
            <span><component :is="message[0] === 'user' ? Leaf : Bot" :size="18" /></span>
            <p>{{ message[1] }}</p>
          </article>
        </div>
        <div class="prompt-chips">
          <button>海洋生物多样性现状如何？</button>
          <button>珊瑚礁白化的原因及影响？</button>
          <button>红树林生态价值有哪些？</button>
        </div>
        <label class="chat-input">
          <input placeholder="输入你的问题，Shift + Enter 换行，Enter 发送" />
          <button><Send :size="18" /></button>
        </label>
      </section>

      <section class="panel knowledge-card-panel">
        <header class="panel-header"><h2>生态知识卡片</h2><button>查看更多 ›</button></header>
        <article v-for="card in cards" :key="card[0]">
          <div><Flame :size="18" /></div>
          <strong>{{ card[0] }} <span>{{ card[1] }}</span></strong>
          <p>{{ card[2] }}</p>
          <small>命中 {{ card[3] }} / 关联 {{ card[4] }}</small>
        </article>
      </section>

      <section class="panel side-feed-panel">
        <header class="panel-header"><h2>数据来源</h2><button>更多 ›</button></header>
        <ul>
          <li>自然资源部海洋生态环境监测 <span>正常</span></li>
          <li>中国海洋生物多样性数据库 <span>正常</span></li>
          <li>国家海洋科学数据中心 <span>正常</span></li>
          <li>卫星遥感海洋生态专题 <span>正常</span></li>
          <li>学术文献与知识库 <span>正常</span></li>
        </ul>
      </section>

      <section class="panel side-feed-panel">
        <header class="panel-header"><h2>模型运行状态</h2><button>更多 ›</button></header>
        <ul>
          <li>生态问答模型-v2.3 <span>运行中</span></li>
          <li>知识检索模型-v2.1 <span>运行中</span></li>
          <li>关系推理模型-v1.8 <span>运行中</span></li>
          <li>生物识别模型-v1.5 <span>运行中</span></li>
        </ul>
      </section>

      <section class="panel record-panel">
        <header class="panel-header"><h2>问答记录列表</h2><button>更多 ›</button></header>
        <table>
          <thead><tr><th>时间</th><th>问题</th><th>主题</th><th>来源</th><th>置信度</th></tr></thead>
          <tbody><tr v-for="record in records" :key="record[0] + record[1]"><td>{{ record[0] }}</td><td>{{ record[1] }}</td><td>{{ record[2] }}</td><td>{{ record[3] }}</td><td>{{ record[4] }}</td></tr></tbody>
        </table>
      </section>

      <section class="panel topic-panel">
        <header class="panel-header"><h2>主题趋势分析</h2><div class="tabs"><button>7天</button><button class="active">30天</button><button>90天</button></div></header>
        <div class="line-chart tall">
          <svg viewBox="0 0 100 45" preserveAspectRatio="none">
            <polyline points="0,34 8,18 16,25 24,12 32,28 40,20 48,15 56,26 64,18 72,23 80,12 88,25 100,17" />
            <polyline class="green-line" points="0,38 8,28 16,32 24,20 32,34 40,29 48,23 56,30 64,25 72,31 80,24 88,33 100,26" />
            <polyline class="red-line" points="0,41 8,36 16,38 24,31 32,40 40,35 48,31 56,37 64,30 72,36 80,33 88,39 100,34" />
          </svg>
        </div>
      </section>

      <section class="panel distribution-panel">
        <header class="panel-header"><h2>知识命中分布</h2></header>
        <div class="donut large">命中分布<br /><strong>56,782</strong></div>
        <ul>
          <li><span>90%以上</span><b>28,764</b><em>50.7%</em></li>
          <li><span>70%-90%</span><b>16,218</b><em>28.6%</em></li>
          <li><span>50%-70%</span><b>7,842</b><em>13.8%</em></li>
          <li><span>30%-50%</span><b>2,964</b><em>5.2%</em></li>
        </ul>
      </section>

      <section class="panel qa-advice-panel">
        <header class="panel-header"><h2>智能回答建议</h2><button>更多 ›</button></header>
        <article><Cloud :size="18" /><span>海草床相关问答量上升 18.7%，建议加强海草床保护专题内容。</span></article>
        <article><Brain :size="18" /><span>赤潮相关问题热度较高，建议补充成因与防控案例。</span></article>
        <article><Leaf :size="18" /><span>生态修复类问题置信度下降，建议更新修复技术动态。</span></article>
      </section>
    </div>
  </section>
</template>
