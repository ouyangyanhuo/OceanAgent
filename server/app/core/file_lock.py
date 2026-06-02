"""进程内文件写锁。

第一版只需要防止同一 Uvicorn 进程内的并发写冲突，因此使用 threading.Lock。
如果未来多进程部署，需要替换为跨进程文件锁。
"""

from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from typing import Iterator

_locks: dict[str, Lock] = {}
_registry_lock = Lock()


def _lock_for(path: Path) -> Lock:
    """为每个绝对路径返回一个稳定的 Lock 实例。"""
    key = str(path.resolve())
    with _registry_lock:
        if key not in _locks:
            _locks[key] = Lock()
        return _locks[key]


@contextmanager
def file_lock(path: Path) -> Iterator[None]:
    """上下文管理器形式的文件锁。"""
    lock = _lock_for(path)
    lock.acquire()
    try:
        yield
    finally:
        lock.release()
