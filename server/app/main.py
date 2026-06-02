from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router, root_router
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.json_store import ensure_json_file
from app.core.paths import (
    AGENT_CACHE_FILE,
    AI_CACHE_FILE,
    EXPANSION_INDEX_FILE,
    GRAPH_FILE,
    REPORT_CACHE_FILE,
    SCHEMA_RULES_FILE,
    ensure_data_dirs,
)
from app.core.response import app_error_handler

settings = get_settings()

app = FastAPI(title="Ocean Agent Intelligence Platform", version=settings.version)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.include_router(root_router)
app.include_router(api_router)


@app.on_event("startup")
def ensure_runtime_files() -> None:
    ensure_data_dirs()
    ensure_json_file(GRAPH_FILE, {"graph_id": "ocean_kg_demo_v1", "version": 1, "nodes": [], "edges": []})
    ensure_json_file(EXPANSION_INDEX_FILE, {})
    ensure_json_file(SCHEMA_RULES_FILE, {"allowed_node_types": [], "allowed_relations": [], "expand_types": {}})
    ensure_json_file(AI_CACHE_FILE, {})
    ensure_json_file(REPORT_CACHE_FILE, {})
    ensure_json_file(AGENT_CACHE_FILE, {})
