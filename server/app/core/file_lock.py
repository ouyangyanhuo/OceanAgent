from contextlib import contextmanager
from pathlib import Path
from threading import Lock
from typing import Iterator

_locks: dict[str, Lock] = {}
_registry_lock = Lock()


def _lock_for(path: Path) -> Lock:
    key = str(path.resolve())
    with _registry_lock:
        if key not in _locks:
            _locks[key] = Lock()
        return _locks[key]


@contextmanager
def file_lock(path: Path) -> Iterator[None]:
    lock = _lock_for(path)
    lock.acquire()
    try:
        yield
    finally:
        lock.release()
