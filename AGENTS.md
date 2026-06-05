# Repository Guidelines

## Project Structure & Module Organization

This repository contains an Ocean Agent demo with a Vue frontend in `client/` and a FastAPI backend in `server/`.

- `client/src/` holds Vue source: `components/`, `views/`, `services/`, `stores/`, `router/`, and shared CSS under `styles/`.
- `server/app/` holds backend code: API routes in `api/routes/`, business logic in `services/`, Pydantic models in `models/`, core helpers in `core/`, and maintenance scripts in `scripts/`.
- `server/app/data/` stores all backend state as JSON, including graph data, caches, snapshots, mock data, notifications, and prompt templates.
- `dev-doc/server-dev/README.md` is the backend development manual; update it when backend architecture, prompt storage, data layout, or development commands change.

## Build, Test, and Development Commands

Frontend:

```bash
cd client
bun run dev      # start Vite locally
bun run build    # build production assets into dist/
bun run preview  # preview the production build
```

Backend:

```bash
cd server
.Ocean/bin/python -m compileall app
.Ocean/bin/python -m app.scripts.validate_graph
.Ocean/bin/python -m app.scripts.reset_data
.Ocean/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

For a fresh backend environment:

```bash
cd server
python3 -m venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

## Coding Style & Naming Conventions

Use the existing style in each area. Vue files use PascalCase component names such as `MetricCard.vue`; JavaScript modules use camelCase exports and concise service files. Python modules use snake_case filenames and functions, with Pydantic schemas in `server/app/models/`. Keep `server/app/main.py` limited to FastAPI wiring, CORS, exception handling, router registration, and startup checks.

## Testing Guidelines

There is no dedicated test framework configured yet. Before submitting backend changes, run `compileall` and `validate_graph`. Before submitting frontend changes, run `npm run build`. Add focused tests only when introducing a test runner or extending an existing one.

## Commit & Pull Request Guidelines

Recent history uses a mix of Conventional Commit-style messages, for example `feat(graph): ...` and `refactor(QA): ...`, plus plain descriptive commits. Prefer `type(scope): summary` for new commits. Pull requests should include a short purpose statement, key changes, verification commands run, linked issues when applicable, and screenshots or screen recordings for UI changes.

## Architecture & Agent-Specific Instructions

Backend routes should call services and return `success(...)`; they should not read or write JSON directly. Keep business logic in `server/app/services/`, paths in `server/app/core/paths.py`, and prompt templates as JSON files under `server/app/data/prompts/`. Do not add SQL databases, graph databases, Redis, ORM layers, LangChain, LlamaIndex, CrewAI, AutoGen, WebSockets, Docker, or deployment scripts for v1 unless explicitly requested.
