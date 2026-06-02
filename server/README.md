# Ocean Agent Backend

FastAPI mock API for the first Ocean Agent dashboard.

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
