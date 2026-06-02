"""JSON 文件读写工具。

后端不使用数据库，因此 JSON 写入必须尽量安全：
写临时文件、flush、fsync，然后 replace 原文件，降低进程中断导致文件损坏的概率。
"""

import json
import os
from pathlib import Path
from typing import Any

from .file_lock import file_lock


def read_json(path: Path, default: Any) -> Any:
    """读取 JSON 文件。

    文件不存在时返回调用方提供的默认值，便于服务启动前后的兜底。
    """
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def atomic_write_json(path: Path, data: Any) -> None:
    """原子写入 JSON 文件。

    先写入同目录临时文件，再用 replace 替换目标文件。
    同目录替换通常是原子操作，可避免半写入状态暴露给读者。
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    # 临时文件和目标文件放在同一目录，确保 replace 操作尽可能原子。
    tmp_path = path.with_suffix(f"{path.suffix}.tmp")
    with tmp_path.open("w", encoding="utf-8") as file:
        # ensure_ascii=False 保留中文，方便直接查看 JSON 文件。
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")

        # flush 将 Python 缓冲写到 OS，fsync 再要求 OS 尽量落盘。
        file.flush()
        os.fsync(file.fileno())

    # replace 会覆盖旧文件；读者要么看到旧文件，要么看到完整新文件。
    tmp_path.replace(path)


def write_json(path: Path, data: Any) -> None:
    """带文件级锁的 JSON 写入入口。

    同一进程内对同一路径串行写入，避免并发写 graph/cache 时互相覆盖。
    """
    with file_lock(path):
        atomic_write_json(path, data)


def ensure_json_file(path: Path, default: Any) -> None:
    """如果文件不存在，则用默认值创建。"""
    if not path.exists():
        write_json(path, default)
