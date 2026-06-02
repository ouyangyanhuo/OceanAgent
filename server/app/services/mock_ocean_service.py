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
    def get_observations(self, sea_area_id: str | None = None) -> list[dict[str, Any]]:
        return self._filter_by_sea_area(read_json(OCEAN_OBSERVATIONS_FILE, []), sea_area_id)

    def get_buoy_status(self, buoy_id: str | None = None) -> list[dict[str, Any]]:
        records = read_json(BUOY_STATUS_FILE, [])
        if buoy_id:
            return [record for record in records if record.get("id") == buoy_id]
        return records

    def get_current_fields(self, sea_area_id: str | None = None) -> list[dict[str, Any]]:
        return self._filter_by_sea_area(read_json(CURRENT_FIELDS_FILE, []), sea_area_id)

    def get_fishery_areas(self) -> list[dict[str, Any]]:
        return read_json(FISHERY_AREAS_FILE, [])

    def get_routes(self) -> list[dict[str, Any]]:
        return read_json(ROUTES_FILE, [])

    def perturb_observation(self, observation: dict[str, Any]) -> dict[str, Any]:
        copy = dict(observation)
        value = copy.get("value")
        if isinstance(value, int | float):
            copy["value"] = round(value * 1.01, 2)
        return copy

    def _filter_by_sea_area(
        self,
        records: list[dict[str, Any]],
        sea_area_id: str | None,
    ) -> list[dict[str, Any]]:
        if not sea_area_id:
            return records
        return [record for record in records if record.get("sea_area_id") == sea_area_id]
