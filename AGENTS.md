# Agent Instructions

## Project Shape

This repository contains an Ocean Agent demo with a Vue frontend in `client/` and a FastAPI backend in `server/`.

The backend stores all state as JSON files under `server/app/data/`. Do not add SQL databases, graph databases, Redis, ORM layers, LangChain, LlamaIndex, CrewAI, AutoGen, WebSockets, Docker, or deployment scripts for v1 unless the user explicitly requests it.

## Backend Rules

- `server/app/main.py` is app wiring only: FastAPI setup, CORS, exception handler, router registration, startup file checks.
- Route modules in `server/app/api/routes/` should call services and return `success(...)`; they should not read or write JSON files directly.
- Business logic belongs in `server/app/services/`.
- Pydantic request/response/domain models belong in `server/app/models/`.
- Paths for JSON data belong in `server/app/core/paths.py`.
- Prompt templates must be JSON files in `server/app/data/prompts/`; do not create txt prompt files.
- LLM output is candidate data only. The backend owns validation, ID generation, deduplication, graph writes, expansion index updates, and snapshots.

## Common Commands

```bash
cd server
.Ocean/bin/python -m compileall app
.Ocean/bin/python -m app.scripts.validate_graph
.Ocean/bin/python -m app.scripts.reset_data
.Ocean/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

For dependency setup:

```bash
cd server
python3 -m venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

## Working Tree Notes

The user may have unrelated frontend edits in `client/`. Do not revert or reformat them unless the request explicitly targets frontend work.

`dev-doc/server-dev/README.md` is the backend development manual. Keep it updated when backend architecture, prompt storage, data layout, or development commands change.
