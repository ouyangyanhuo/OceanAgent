"""模拟海洋数据服务。

读取 app/data/mock 下的 JSON 文件，为前端展示、智能体分析和报告生成提供上下文。
"""

from typing import Any

from app.core.json_store import read_json
from app.core.paths import (
    BUOY_STATUS_FILE,
    CURRENT_FIELDS_FILE,
    FISHERY_AREAS_FILE,
    OCEAN_OBSERVATIONS_FILE,
    ROUTES_FILE,
)


class MockOceanService:
    """封装 mock 海洋数据读取和简单过滤。"""

    def get_observations(self, sea_area_id: str | None = None) -> list[dict[str, Any]]:
        """返回海洋观测记录，可按海域过滤。"""
        # 观测数据通常与海域绑定，因此复用按 sea_area_id 过滤的辅助函数。
        return self._filter_by_sea_area(read_json(OCEAN_OBSERVATIONS_FILE, []), sea_area_id)

    def get_buoy_status(self, buoy_id: str | None = None) -> list[dict[str, Any]]:
        """返回浮标状态，可按浮标 ID 过滤。"""
        records = read_json(BUOY_STATUS_FILE, [])
        if buoy_id:
            # 浮标接口按 buoy_id 过滤，而不是 sea_area_id。
            return [record for record in records if record.get("id") == buoy_id]
        return records

    def get_current_fields(self, sea_area_id: str | None = None) -> list[dict[str, Any]]:
        """返回海流场记录，可按海域过滤。"""
        return self._filter_by_sea_area(read_json(CURRENT_FIELDS_FILE, []), sea_area_id)

    def get_fishery_areas(self) -> list[dict[str, Any]]:
        """返回渔场区域数据。"""
        return read_json(FISHERY_AREAS_FILE, [])

    def get_routes(self) -> list[dict[str, Any]]:
        """返回航线数据。"""
        return read_json(ROUTES_FILE, [])

    def perturb_observation(self, observation: dict[str, Any]) -> dict[str, Any]:
        """生成轻微扰动后的观测值。

        仅用于展示模拟变化，不会回写基础 mock 数据文件。
        """
        copy = dict(observation)
        value = copy.get("value")
        if isinstance(value, int | float):
            # 只扰动数值字段；非数值观测保持原样。
            copy["value"] = round(value * 1.01, 2)
        return copy

    def _filter_by_sea_area(
        self,
        records: list[dict[str, Any]],
        sea_area_id: str | None,
    ) -> list[dict[str, Any]]:
        """按 sea_area_id 过滤记录。"""
        if not sea_area_id:
            # 没有过滤条件时返回完整列表，供总览页面使用。
            return records

        # mock 文件约定每条记录用 sea_area_id 字段关联海域。
        return [record for record in records if record.get("sea_area_id") == sea_area_id]
