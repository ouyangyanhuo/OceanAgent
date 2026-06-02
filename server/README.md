# Ocean Agent Backend

FastAPI mock API for the first Ocean Agent dashboard.

Backend data, cache files, graph files, mock records, snapshots, and prompt JSON
files live under `app/data/`.

```bash
python3 -m venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/uvicorn app.main:app --reload
```

If port `8000` is occupied locally, run the API on another port and start the
frontend with `VITE_API_TARGET=http://127.0.0.1:<port>`.

Endpoints:

- `GET /health`
- `GET /api/dashboard`
- `GET /api/graph`
- `GET /api/graph/nodes/{node_id}`
- `GET /api/graph/nodes/{node_id}/neighbors`
- `GET /api/graph/nodes/{node_id}/expand-options`
- `POST /api/graph/expand`
- `GET /api/agent/list`
- `POST /api/agent/run`
- `POST /api/report/generate`
- `GET /api/mock/ocean-observations`
- `GET /api/mock/buoy-status`
- `GET /api/mock/current-fields`
- `GET /api/mock/fishery-areas`
- `GET /api/mock/routes`
- `GET /api/cache/status`
- `POST /api/cache/clear`
