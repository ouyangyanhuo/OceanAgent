"""图谱快照服务。

每次图谱发生结构性变化后创建快照，便于后续回溯和调试。
"""

from datetime import datetime
from typing import Any

from app.core.json_store import read_json, write_json
from app.core.paths import SNAPSHOT_DIR
from app.models.graph import GraphData


class SnapshotService:
    """封装图谱快照创建、列表和恢复。"""

    def create_snapshot(self, graph: GraphData, reason: str) -> str:
        """创建图谱快照文件并返回文件名。"""
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"graph_{stamp}_v{graph.version}.json"
        path = SNAPSHOT_DIR / filename
        payload = graph.model_dump(mode="json")

        # 在快照中附加元信息，不影响正式 graph.json 模型。
        payload["_snapshot"] = {"reason": reason, "created_at": datetime.utcnow().isoformat()}
        write_json(path, payload)
        return filename

    def list_snapshots(self) -> list[dict[str, Any]]:
        """列出已有快照，按文件名倒序返回。"""
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
        """读取指定快照并解析为 GraphData。

        当前 API 未暴露恢复操作；该方法预留给后续管理接口或脚本。
        """
        return GraphData.model_validate(read_json(SNAPSHOT_DIR / filename, {}))
