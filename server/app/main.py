from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .mock_data import DASHBOARD_DATA

app = FastAPI(title="Ocean Agent Intelligence Platform", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ocean-agent-api"}


@app.get("/api/dashboard")
def dashboard() -> dict:
    return DASHBOARD_DATA
