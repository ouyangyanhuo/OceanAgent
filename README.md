# Ocean Agent Intelligence Platform

海洋智能体决策平台 — Vue 3 前端 + FastAPI 后端，基于知识图谱的海洋生态监测与智能分析系统。

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | Vue 3 · Vite 6 · Tailwind CSS v4 · Pinia · Vue Router 4 · Cytoscape · Leaflet |
| 后端 | FastAPI · Pydantic · Uvicorn · httpx |
| 包管理 | 前端 Bun / 后端 uv + pip |
| 数据存储 | JSON 文件（无数据库） |

## 项目结构

```
OceanAgent/
├── client/                 # Vue 3 前端
│   ├── src/
│   │   ├── views/          # 页面组件（6 个 Agent 页 + 搜索 + 图谱）
│   │   ├── components/     # 通用组件
│   │   ├── stores/         # Pinia 状态管理
│   │   ├── composables/    # 组合式函数
│   │   └── router/         # 路由配置
│   └── vite.config.js      # Vite 配置（代理 /api → 后端）
│
├── server/                 # FastAPI 后端
│   ├── app/
│   │   ├── api/routes/     # 路由层（请求转换 → 调用服务）
│   │   ├── services/       # 业务逻辑层
│   │   ├── models/         # Pydantic 模型
│   │   ├── core/           # 基础设施（配置、路径、JSON I/O、锁、错误）
│   │   ├── data/           # 持久化数据（图谱、提示词、缓存、Mock）
│   │   └── scripts/        # 维护脚本（校验图谱、重置数据）
│   └── requirements.txt
│
├── client/Dockerfile       # 前端容器化
├── server/Dockerfile       # 后端容器化
└── .dockerignore
```

## 本地开发

### 后端

```bash
cd server

# 创建虚拟环境 & 安装依赖
python3 -m venv .venv
uv pip install --python .venv/bin/python -r requirements.txt

# 启动开发服务器（默认 :8000）
.venv/bin/uvicorn app.main:app --reload

# 编译检查
.venv/bin/python -m compileall app

# 校验图谱完整性
.venv/bin/python -m app.scripts.validate_graph

# 重置数据到默认状态
.venv/bin/python -m app.scripts.reset_data
```

### 前端

```bash
cd client

bun install       # 安装依赖
bun run dev       # 启动开发服务器（默认 :5173，代理 /api → :8000）
bun run build     # 生产构建
bun run preview   # 预览生产构建
```

如果端口 8000 被占用，可在其他端口启动后端，然后：

```bash
VITE_API_TARGET=http://127.0.0.1:<port> bun run dev
```

### 环境变量

后端通过 `server/.env` 配置，参考 `server/.env.example`：

| 变量 | 说明 | 默认值 |
|---|---|---|
| `CORS_ORIGINS` | 允许的跨域来源 | `http://localhost:5173,http://127.0.0.1:5173` |
| `LLM_PROVIDER` | LLM 提供商 | `mock` |
| `LLM_API_KEY` | API Key | - |
| `LLM_BASE_URL` | API 地址 | - |
| `LLM_MODEL` | 模型名称 | - |
| `CACHE_ENABLED` | 是否启用缓存 | `true` |

## Docker 部署

### 构建镜像

```bash
# 后端
docker build -t ocean-agent-server -f server/Dockerfile .

# 前端
docker build -t ocean-agent-client -f client/Dockerfile .
```

### 运行

```bash
# 启动后端（:8000）
docker run -d -p 8000:8000 --name ocean-server \
  -e LLM_PROVIDER=mock \
  ocean-agent-server

# 启动前端（:80）
docker run -d -p 80:80 --name ocean-client \
  -e API_TARGET=http://host.docker.internal:8000 \
  ocean-agent-client
```

> 前端 Nginx 默认将 `/api` 和 `/health` 反向代理到 `API_TARGET`（默认 `http://localhost:8000`）。

### docker-compose（参考）

```yaml
version: "3.9"
services:
  server:
    build:
      context: .
      dockerfile: server/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - LLM_PROVIDER=mock
    volumes:
      - server-data:/app/app/data

  client:
    build:
      context: .
      dockerfile: client/Dockerfile
    ports:
      - "80:80"
    environment:
      - API_TARGET=http://server:8000
    depends_on:
      - server

volumes:
  server-data:
```

## API 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/health` | 健康检查 |
| GET | `/api/dashboard` | 仪表盘数据 |
| GET | `/api/graph` | 完整知识图谱 |
| GET | `/api/graph/nodes/{id}` | 节点详情 |
| GET | `/api/graph/nodes/{id}/neighbors` | 节点邻居 |
| GET | `/api/graph/nodes/{id}/expand-options` | 可选扩展类型 |
| POST | `/api/graph/expand` | 扩展图谱 |
| GET | `/api/agent/list` | Agent 列表 |
| POST | `/api/agent/run` | 运行 Agent |
| POST | `/api/report/generate` | 生成报告 |
| GET | `/api/mock/ocean-observations` | 海洋观测数据 |
| GET | `/api/mock/buoy-status` | 浮标状态 |
| GET | `/api/mock/current-fields` | 洋流场数据 |
| GET | `/api/mock/fishery-areas` | 渔场区域 |
| GET | `/api/mock/routes` | 航线路由 |
| GET | `/api/cache/status` | 缓存状态 |
| POST | `/api/cache/clear` | 清除缓存 |

所有接口统一返回格式：

```json
{ "success": true, "data": {}, "message": "ok", "error": null }
```

## 设计约束

1. **LLM 仅作建议** — LLM 输出候选节点/边，后端负责校验、ID 生成、去重和写入
2. **图谱结构扩展幂等** — 相同节点 + 相同扩展类型 = 缓存结果，不重复调用 LLM
3. **结构层与表达层分离** — 图谱结构持久稳定；报告/问答等表达层可动态再生成
4. **提示词即 JSON 文件** — 存放在 `server/app/data/prompts/`，模板变量用 `{{var}}`
5. **所有 JSON 路径集中管理** — 在 `core/paths.py` 中定义，服务层从不硬编码路径

## License

MIT
