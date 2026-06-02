import json
import os
from pathlib import Path
from typing import Any

from .file_lock import file_lock


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(f"{path.suffix}.tmp")
    with tmp_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")
        file.flush()
        os.fsync(file.fileno())
    tmp_path.replace(path)


def write_json(path: Path, data: Any) -> None:
    with file_lock(path):
        atomic_write_json(path, data)


def ensure_json_file(path: Path, default: Any) -> None:
    if not path.exists():
        write_json(path, default)
