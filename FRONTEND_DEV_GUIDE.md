# Ocean Agent 前端开发指南

> 本指南面向新加入项目的开发者，涵盖环境搭建、启动开发、目录结构、模块说明和编码规范。

---

## 目录
0. [项目克隆](#0-项目克隆)
1. [技术栈概览](#1-技术栈概览)
2. [环境准备](#2-环境准备)
3. [安装与启动](#3-安装与启动)
4. [目录结构与文件说明](#4-目录结构与文件说明)
5. [核心架构说明](#5-核心架构说明)
6. [如何新增页面](#6-如何新增页面)
7. [如何新增组件](#7-如何新增组件)
8. [样式开发指南](#8-样式开发指南)
9. [API 调用约定](#9-api-调用约定)
10. [常见问题 FAQ](#10-常见问题-faq)

---
## 0. 项目克隆
### 安装 Git
[安装教程](https://www.runoob.com/git/git-install-setup.html)

不用 Git 也可以直接下载 zip 包

###
### Clone 教程

打开命令行运行
```
git clone https://gitee.com/magneto110/OceanAgent
```

## 1. 技术栈概览

| 类别       | 技术                          | 说明                          |
| ---------- | ----------------------------- | ----------------------------- |
| 框架       | Vue 3.5+ (Composition API)   | 使用 `<script setup>` 语法糖  |
| 构建工具   | Vite 6                        | 快速热更新、ESM 原生支持      |
| CSS 方案   | Tailwind CSS v4 + 自定义 CSS  | Tailwind 通过 Vite 插件集成   |
| 图标库     | lucide-vue-next               | 全量 Lucide 图标的 Vue 版本   |
| UI 样式库  | @heroui/styles                | 提供基础组件样式              |
| 包管理器   | Bun (推荐) / npm              | 项目 lockfile 为 bun.lock     |
| 路由       | 无 Vue Router                 | 通过 ref + v-if 手动切换页面  |
| 状态管理   | 无 Pinia/Vuex                 | 各组件本地 ref 管理状态       |

---

## 2. 环境准备

### 2.1 安装 Node.js
[安装指引](https://www.runoob.com/nodejs/nodejs-install-setup.html)

### 2.2 安装 Bun（推荐）

[安装指引](https://www.bunjs.cn/docs/installation)

如果不想用 Bun，也可以用 npm，后续命令将 `bun` 替换为 `npm` 即可。

### 2.3 编辑器推荐

- **VS Code** + 以下扩展：
  - [Vue - Official](https://marketplace.visualstudio.com/items?itemName=Vue.volar) — Vue 3 语法支持（原 Volar）
  - [Tailwind CSS IntelliSense](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss) — Tailwind 类名提示
  - [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) — 代码规范检查（可选，项目暂未配置）

---

## 3. 安装与启动

### 3.1 首次安装

```bash
# 进入前端目录
cd client

# 安装依赖
bun install
```

### 3.2 启动开发服务器

```bash
bun run dev
```

启动后终端会显示类似：

```
  VITE v6.x.x  ready in 300 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

在浏览器打开 `http://localhost:5173` 即可看到页面。

### 3.3 连接后端 API

开发服务器会自动将 `/api` 和 `/health` 请求代理到后端。默认代理目标为 `http://127.0.0.1:8000`。

如果你的后端运行在其他端口：

```bash
# 例如后端运行在 9000 端口
VITE_API_TARGET=http://127.0.0.1:9000 bun run dev
```

> **注意：** 即使不启动后端，前端也能正常运行——所有数据都有前端内置的 fallback 静态数据。

### 3.4 生产构建

```bash
# 构建产物输出到 dist/
bun run build

# 预览构建结果
bun run preview
```

### 3.5 全部可用命令

| 命令              | 作用                   |
| ----------------- | ---------------------- |
| `bun install`     | 安装依赖               |
| `bun run dev`     | 启动开发服务器（热更新）|
| `bun run build`   | 生产构建               |
| `bun run preview` | 预览生产构建           |

---

## 4. 目录结构与文件说明

```
client/
├── index.html                  # HTML 入口，挂载 #app，加载 /src/main.js
├── package.json                # 项目配置、依赖、脚本
├── bun.lock                    # Bun lockfile（不要手动修改）
├── vite.config.js              # Vite 配置：Vue 插件 + Tailwind 插件 + API 代理
│
└── src/
    ├── main.js                 # 应用入口：创建 Vue 实例，导入全局样式，挂载到 #app
    ├── App.vue                 # 根组件：顶部栏 + 侧边栏 + 页面切换 + 状态栏
    ├── styles.css              # 全局样式入口，按顺序导入所有 CSS 文件
    │
    ├── components/             # 所有 Vue 组件（页面 + 可复用组件）
    │   ├── SidebarNav.vue          # 侧边栏导航（6 个页面入口，支持折叠/展开）
    │   ├── AgentSearchPage.vue     # 智能体搜索页（默认首页）
    │   ├── GraphPage.vue           # 关系图谱页
    │   ├── EcoQaPage.vue           # 海洋生态问答页
    │   ├── FisheryAssessmentPage.vue  # 渔业评估页
    │   ├── RouteOptimizationPage.vue  # 航线优化页
    │   ├── BuoyDiagnosticsPage.vue    # 浮标诊断页
    │   ├── DashboardPage.vue       # 仪表盘页（当前未使用，备用）
    │   ├── AgentCard.vue           # 可复用：智能体卡片
    │   ├── MetricCard.vue          # 可复用：指标卡片（含迷你折线图）
    │   ├── TaskFeed.vue            # 可复用：任务时间线面板
    │   ├── DataSources.vue         # 可复用：数据源列表面板
    │   └── KnowledgeGraph.vue      # 可复用：SVG 知识图谱可视化
    │
    ├── services/               # API 调用层
    │   └── dashboard.js            # 唯一的服务文件：fetchDashboard() + fallback 数据
    │
    └── styles/                 # 样式文件（按职责分层）
        ├── base.css                # 基础样式：CSS 变量、重置、布局骨架、顶栏、侧栏
        ├── components.css          # 组件样式：面板、卡片、指标网格、时间线、图谱、状态栏
        ├── responsive.css          # 响应式断点：1560px / 1320px / 1100px / 900px
        ├── shared/
        │   ├── topbar.css          # 顶栏响应式适配
        │   ├── page-head.css       # 页面头部（标题 + 操作按钮）样式
        │   └── layout-hardening.css # 布局加固：溢出控制、滚动条、网格修正
        └── pages/
            ├── dashboard.css       # 仪表盘页面布局
            ├── agent-search.css    # 智能体搜索页布局
            ├── graph.css           # 关系图谱页布局
            ├── qa.css              # 问答页样式（聊天、知识卡片、图表）
            ├── qa-layout.css       # 问答页 CSS Grid 区域定义
            ├── detail.css          # 详情页通用样式（地图、微型指标、传感器面板）
            └── task.css            # 任务页样式（流程、图表、表格、建议面板）
```

### 文件职责速查

| 文件                  | 一句话说明                            |
| --------------------- | ------------------------------------- |
| `index.html`          | HTML 外壳，只有一行 `<div id="app">`  |
| `main.js`             | 创建 Vue app，导入样式，挂载          |
| `App.vue`             | 全局布局 + 页面路由（v-if 切换）      |
| `styles.css`          | CSS 入口，@import 所有样式文件        |
| `vite.config.js`      | 构建配置 + API 代理                   |
| `dashboard.js`        | 唯一的 API 调用 + 全局 fallback 数据  |
| `SidebarNav.vue`      | 左侧导航栏                           |
| `*Page.vue`           | 各页面组件（6 个页面）                |
| `AgentCard.vue`       | 智能体展示卡片                       |
| `MetricCard.vue`      | 带迷你图的指标卡片                    |
| `TaskFeed.vue`        | 任务列表时间线                        |
| `DataSources.vue`     | 数据源面板                            |
| `KnowledgeGraph.vue`  | SVG 知识图谱                          |
| `styles/base.css`     | CSS 变量、布局骨架                    |
| `styles/components.css` | 组件通用样式                        |
| `styles/pages/*.css`  | 各页面专属样式                        |
| `styles/responsive.css` | 响应式断点                          |

---

## 5. 核心架构说明

### 5.1 页面切换机制

本项目 **没有使用 Vue Router**，页面切换通过 `App.vue` 中的 `activePage` ref 实现：

```js
// App.vue
const activePage = ref('agents')  // 默认页面
```

```html
<!-- 模板中用 v-if 切换 -->
<AgentSearchPage      v-if="activePage === 'agents'"   :dashboard="dashboard" />
<GraphPage        v-else-if="activePage === 'graph'"   :dashboard="dashboard" />
<EcoQaPage        v-else-if="activePage === 'qa'"      />
<FisheryAssessmentPage v-else-if="activePage === 'fishery'" />
<RouteOptimizationPage v-else-if="activePage === 'route'"  />
<BuoyDiagnosticsPage   v-else-if="activePage === 'buoy'"   />
```

`SidebarNav` 通过 `emit('change-page', pageName)` 通知 `App.vue` 切换页面。

### 5.2 数据流

```
dashboard.js::fetchDashboard()
       │
       ▼  (成功则用 API 数据，失败则用 fallback 静态数据)
       │
   App.vue::dashboard ref
       │
       ├──► AgentSearchPage (props: dashboard)
       │       ├──► MetricCard × 4  (dashboard.metrics)
       │       ├──► AgentCard × 6   (dashboard.agents)
       │       ├──► TaskFeed        (dashboard.tasks)
       │       └──► DataSources     (dashboard.sources)
       │
       └──► GraphPage (props: dashboard)
               └──► KnowledgeGraph  (dashboard.graph)
```

其他页面（Q&A、渔业、航线、浮标）目前 **完全使用组件内部硬编码数据**，不依赖 `dashboard` props。

### 5.3 组件通信模式

- **父子通信**：Props 向下传，Events（emit）向上传
- **无全局状态**：没有 Pinia/Vuex，每个组件自己管理状态
- **兄弟通信**：通过父组件中转（如 SidebarNav → App.vue → Page）

---

## 6. 如何新增页面

假设要新增一个名为 "Marine Pollution" 的页面：

### 步骤 1：创建页面组件

在 `src/components/` 下新建 `MarinePollutionPage.vue`：

```vue
<script setup>
// 从 lucide-vue-next 导入需要的图标
import { Waves } from 'lucide-vue-next'
// 导入可复用组件
import MetricCard from './MetricCard.vue'
</script>

<template>
  <div class="page-head">
    <div>
      <h2>海洋污染监测</h2>
      <p class="subtitle">实时追踪海洋污染物扩散与治理</p>
    </div>
    <div class="actions">
      <button class="btn-outline">导出报告</button>
      <button class="btn-primary">新建任务</button>
    </div>
  </div>
  <!-- 页面内容 -->
</template>
```

### 步骤 2：注册页面到 App.vue

```js
// App.vue <script setup> 中导入
import MarinePollutionPage from './components/MarinePollutionPage.vue'
```

```html
<!-- App.vue template 中添加 v-else-if 分支 -->
<BuoyDiagnosticsPage   v-else-if="activePage === 'buoy'" />
<MarinePollutionPage   v-else-if="activePage === 'pollution'" />
```

### 步骤 3：添加导航入口

在 `SidebarNav.vue` 的 `navItems` 数组中追加一项：

```js
{ key: 'pollution', icon: Waves, label: '污染监测' }
```

### 步骤 4（可选）：添加页面专属样式

在 `src/styles/pages/` 下新建 `pollution.css`，然后在 `src/styles.css` 中导入：

```css
@import "./styles/pages/pollution.css";
```

---

## 7. 如何新增组件

### 可复用组件 vs 页面组件

| 类型       | 存放位置             | 是否被多个页面使用 | 示例               |
| ---------- | -------------------- | ------------------ | ------------------ |
| 页面组件   | `src/components/`    | 否，只在一个页面用 | `EcoQaPage.vue`    |
| 可复用组件 | `src/components/`    | 是，被多个页面引用 | `MetricCard.vue`   |

> 目前两种组件都放在同一目录下，通过命名约定区分：页面组件以 `Page.vue` 结尾。

### 组件模板

```vue
<script setup>
/**
 * MyComponent - 组件简要说明
 */
import { ref, computed } from 'vue'

// Props 定义
const props = defineProps({
  data: { type: Object, required: true }
})

// Events 定义
const emit = defineEmits(['update'])

// 本地状态
const isOpen = ref(false)

// 计算属性
const displayValue = computed(() => props.data.value ?? 'N/A')

// 方法
function handleClick() {
  emit('update', displayValue.value)
}
</script>

<template>
  <div class="my-component" @click="handleClick">
    <span>{{ displayValue }}</span>
  </div>
</template>
```

### 图标使用

从 `lucide-vue-next` 按需导入：

```js
import { Search, Anchor, Fish, AlertTriangle } from 'lucide-vue-next'
```

在模板中使用：

```html
<Search :size="18" />
<Anchor :size="16" stroke-width="2" />
```

---

## 8. 样式开发指南

### 8.1 CSS 变量（主题色）

所有主题色通过 CSS 变量定义在 `styles/base.css` 的 `:root` 中：

```css
:root {
  --panel: #0c1929;           /* 面板背景 */
  --panel-strong: #112240;    /* 强调面板背景 */
  --line: rgba(255,255,255,.08); /* 边框/分割线 */
  --text-soft: rgba(255,255,255,.55); /* 次要文字 */

  /* 强调色 */
  --blue: #3b82f6;
  --cyan: #22d3ee;
  --teal: #2dd4bf;
  --green: #34d399;
  --violet: #a78bfa;
  --rose: #fb7185;
  --amber: #fbbf24;
}
```

使用方式：

```css
.my-panel {
  background: var(--panel);
  border: 1px solid var(--line);
  color: var(--text-soft);
}
```

### 8.2 Tone（色调）系统

组件通过 `.tone-*` 类名设置强调色，最终映射到 `--tone-color` CSS 变量：

```html
<div class="tone-blue">   <!-- --tone-color: var(--blue) -->
<div class="tone-rose">   <!-- --tone-color: var(--rose) -->
<div class="tone-teal">   <!-- --tone-color: var(--teal) -->
```

可用的 tone：`blue`、`cyan`、`teal`、`green`、`violet`、`rose`、`amber`。

### 8.3 新增样式文件

1. 在 `src/styles/pages/` 下创建 `.css` 文件
2. 在 `src/styles.css` 末尾按顺序导入：

```css
/* styles.css */
@import "./styles/pages/pollution.css";
```

> **导入顺序很重要**——后面的文件可以覆盖前面的样式。

### 8.4 响应式断点

项目定义了 4 个断点（见 `responsive.css`）：

| 断点范围          | 布局行为                           |
| ----------------- | ---------------------------------- |
| `> 1560px`        | 密集桌面布局，多列网格             |
| `1321px ~ 1560px` | 标准桌面布局                       |
| `901px ~ 1320px`  | 平板布局：侧栏折叠，网格变单列     |
| `<= 900px`        | 移动布局：侧栏变顶部横导航，全部堆叠 |

编写新样式时，请在 `responsive.css` 中添加对应的媒体查询。

---

## 9. API 调用约定

### 当前状态

项目目前只有一个 API 调用：`fetchDashboard()`（在 `services/dashboard.js` 中）。其他所有页面使用硬编码的静态数据。

### API 调用模式

```js
// services/example.js
const API_BASE = '/api'  // Vite 会代理到后端

export async function fetchSomething() {
  try {
    const res = await fetch(`${API_BASE}/something`)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const json = await res.json()
    return json.data ?? json  // 后端统一返回 {success, data, message, error}
  } catch (err) {
    console.warn('API 调用失败，使用 fallback 数据:', err)
    return fallbackSomething  // 返回内置的静态数据
  }
}
```

### 关键约定

1. **所有 API 路径以 `/api` 开头**——Vite 开发服务器会代理到后端
2. **后端返回格式统一**为 `{success: true, data: {...}, message: "ok", error: null}`
3. **必须提供 fallback 数据**——后端离线时前端仍可正常展示
4. **不使用 axios 等第三方 HTTP 库**——直接用原生 `fetch`

---

## 10. 常见问题 FAQ

### Q: `bun install` 报错怎么办？

确认 Bun 已正确安装：
```bash
bun --version  # 应显示 1.x.x
```
如果不想用 Bun，可以用 npm：
```bash
npm install
```

### Q: 启动后页面空白？

1. 检查终端是否有编译错误
2. 确认浏览器打开的是 `http://localhost:5173`（不是其他端口）
3. 清除浏览器缓存后刷新

### Q: API 请求 404？

- 确认后端已启动在 8000 端口
- 或者确认 `VITE_API_TARGET` 环境变量指向正确的后端地址
- 但即使后端没启动，页面也能正常显示（使用 fallback 数据）

### Q: 热更新不生效？

- Vue 模板和 `<script setup>` 的修改会自动热更新
- `styles.css` 的 @import 结构变更可能需要手动刷新
- `vite.config.js` 修改后需要重启开发服务器

### Q: 如何查看构建产物大小？

```bash
bun run build
# 构建完成后终端会显示各文件大小
# 产物在 dist/ 目录下
```

### Q: 为什么没有 Vue Router？

当前项目规模较小（6 个页面），使用 `v-if` 切换已经足够，引入 Vue Router 会增加不必要的复杂度。如果后续页面数量增长到 10+，可以考虑迁移。

### Q: 如何添加新的 Lucide 图标？

```js
// 在组件的 <script setup> 中按需导入
import { NewIconName } from 'lucide-vue-next'
```

所有可用图标见 [Lucide 官网](https://lucide.dev/icons/)。图标名称使用 PascalCase。

---

## 附录：页面与组件对应关系

```
App.vue
├── Topbar (header)
├── SidebarNav.vue
│   └── navItems → emit('change-page')
│
├── [agents]   AgentSearchPage.vue
│   ├── MetricCard.vue × 4
│   ├── AgentCard.vue × 6
│   ├── TaskFeed.vue
│   └── DataSources.vue
│
├── [graph]    GraphPage.vue
│   ├── MetricCard.vue × 4
│   ├── KnowledgeGraph.vue
│   ├── TaskFeed.vue
│   └── DataSources.vue
│
├── [qa]       EcoQaPage.vue (内部硬编码数据)
│
├── [fishery]  FisheryAssessmentPage.vue (内部硬编码数据)
│
├── [route]    RouteOptimizationPage.vue (内部硬编码数据)
│
└── [buoy]     BuoyDiagnosticsPage.vue (内部硬编码数据)
```
