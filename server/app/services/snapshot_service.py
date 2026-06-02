from datetime import datetime
from typing import Any

from app.core.json_store import read_json, write_json
from app.core.paths import SNAPSHOT_DIR
from app.models.graph import GraphData


class SnapshotService:
    def create_snapshot(self, graph: GraphData, reason: str) -> str:
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"graph_{stamp}_v{graph.version}.json"
        path = SNAPSHOT_DIR / filename
        payload = graph.model_dump(mode="json")
        payload["_snapshot"] = {"reason": reason, "created_at": datetime.utcnow().isoformat()}
        write_json(path, payload)
        return filename

    def list_snapshots(self) -> list[dict[str, Any]]:
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        snapshots = []
        for path in sorted(SNAPSHOT_DIR.glob("graph_*.json"), reverse=True):
            snapshots.append(
                {
                    "filename": path.name,
                    "size": path.stat().st_size,
                    "modified_at": datetime.utcfromtimestamp(path.stat().st_mtime).isoformat(),
                }
            )
        return snapshots

    def restore_snapshot(self, filename: str) -> GraphData:
        return GraphData.model_validate(read_json(SNAPSHOT_DIR / filename, {}))
