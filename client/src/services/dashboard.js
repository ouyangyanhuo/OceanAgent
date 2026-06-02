export const fallbackDashboard = {
  metrics: [
    { label: '接入智能体', value: '128', trend: '8', tone: 'blue', sparkline: [22, 26, 25, 31, 28, 35, 29, 41, 33, 37, 35, 45] },
    { label: '今日检索', value: '3,256', trend: '12.5%', tone: 'cyan', sparkline: [18, 21, 20, 27, 24, 34, 28, 31, 38, 29, 43, 34] },
    { label: '知识节点', value: '56,782', trend: '6.3%', tone: 'teal', sparkline: [26, 29, 34, 30, 37, 35, 43, 39, 46, 32, 39, 42] },
    { label: '关系边数', value: '201,856', trend: '9.8%', tone: 'violet', sparkline: [24, 27, 25, 34, 31, 45, 36, 41, 49, 35, 52, 42] },
  ],
  agents: [
    { name: '海流分析智能体', description: '基于多源数据的海流动力分析与趋势预测智能体', tags: ['海洋监测', '海流分析'], tone: 'blue', status: '在线' },
    { name: '赤潮预警智能体', description: '赤潮监测、识别与预测的专业智能体', tags: ['生态分析', '灾害预警'], tone: 'rose', status: '在线' },
    { name: '渔场评估智能体', description: '渔场环境评估与渔获量预测智能体', tags: ['渔业分析', '资源评估'], tone: 'teal', status: '在线' },
    { name: '航线优化智能体', description: '基于气象海况的航线规划与优化智能体', tags: ['航运预测', '航线优化'], tone: 'violet', status: '在线' },
    { name: '海洋生态问答智能体', description: '海洋生态知识问答与解读智能体', tags: ['生态分析', '知识问答'], tone: 'cyan', status: '在线' },
    { name: '浮标数据诊断智能体', description: '浮标异常监测与数据质量诊断智能体', tags: ['设备巡检', '数据诊断'], tone: 'amber', status: '在线' },
  ],
  tasks: [
    { time: '10:24', title: '检索海洋监测智能体', status: '成功', tone: 'green' },
    { time: '10:18', title: '构建赤潮事件关系图谱', status: '图谱构建', tone: 'violet' },
    { time: '10:05', title: '导入浮标观测数据', status: '数据导入', tone: 'blue' },
    { time: '09:52', title: '生成分析报告', status: '报告生成', tone: 'amber' },
  ],
  sources: [
    { name: '浮标', status: '在线', count: '1,245', tone: 'blue' },
    { name: 'AIS', status: '在线', count: '3,628', tone: 'cyan' },
    { name: '遥感', status: '在线', count: '892', tone: 'teal' },
    { name: '气象', status: '在线', count: '1,573', tone: 'sky' },
    { name: '声呐', status: '在线', count: '456', tone: 'indigo' },
  ],
  graph: {
    center: { id: 'event', label: '海洋\n环境事件', x: 50, y: 50, tone: 'core' },
    nodes: [
      { id: 'temp', label: '温盐', x: 31, y: 17, tone: 'cyan', type: '观测设备' },
      { id: 'buoy', label: '浮标', x: 50, y: 13, tone: 'green', type: '观测设备' },
      { id: 'satellite', label: '遥感影像', x: 68, y: 19, tone: 'cyan', type: '物理要素' },
      { id: 'redtide', label: '赤潮', x: 82, y: 39, tone: 'rose', type: '现象事件' },
      { id: 'typhoon', label: '台风', x: 77, y: 61, tone: 'violet', type: '行业领域' },
      { id: 'pollution', label: '污染源', x: 64, y: 78, tone: 'amber', type: '人类活动' },
      { id: 'fishery', label: '渔业', x: 50, y: 80, tone: 'green', type: '观测设备' },
      { id: 'shipping', label: '航运', x: 29, y: 79, tone: 'blue', type: '物理要素' },
      { id: 'farm', label: '海洋牧场', x: 20, y: 62, tone: 'blue', type: '物理要素' },
      { id: 'current', label: '海流', x: 20, y: 40, tone: 'blue', type: '物理要素' },
    ],
    edges: [
      { source: 'event', target: 'temp', kind: '因果关系' },
      { source: 'event', target: 'buoy', kind: '相关关系' },
      { source: 'event', target: 'satellite', kind: '因果关系' },
      { source: 'event', target: 'redtide', kind: '相关关系' },
      { source: 'event', target: 'typhoon', kind: '因果关系' },
      { source: 'event', target: 'pollution', kind: '相关关系' },
      { source: 'event', target: 'fishery', kind: '因果关系' },
      { source: 'event', target: 'shipping', kind: '相关关系' },
      { source: 'event', target: 'farm', kind: '因果关系' },
      { source: 'event', target: 'current', kind: '相关关系' },
      { source: 'temp', target: 'redtide', kind: '相关关系' },
      { source: 'redtide', target: 'typhoon', kind: '相关关系' },
    ],
  },
}

export async function fetchDashboard() {
  try {
    const response = await fetch('/api/dashboard')
    if (!response.ok) throw new Error(`Dashboard request failed: ${response.status}`)
    return await response.json()
  } catch {
    return fallbackDashboard
  }
}
