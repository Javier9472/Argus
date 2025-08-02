from collections import deque
from multiprocessing import Queue
from typing import Any, Deque, List, Optional

class CameraBuffer:

    def __init__(self, max_frames: int) -> None:
        self._buffer: Deque[Any] = deque(maxlen=max_frames)

    # ── API pública ────────────────────────────────────────────
    def push(self, frame: Any) -> None:
        self._buffer.append(frame)

    def latest(self) -> Optional[Any]:
        return self._buffer[-1] if self._buffer else None

    def last_n(self, n: int) -> List[Any]:
        if n <= 0:
            return []
        start = max(0, len(self._buffer) - n)
        return list(self._buffer)[start:]

    def clear(self) -> None:
        self._buffer.clear()

    # ── Métodos mágicos ───────────────────────────────────────
    def __len__(self) -> int:
        return len(self._buffer)

    def __iter__(self):
        return iter(self._buffer)

    def __repr__(self):
        return f"<CameraBuffer size={len(self._buffer)} max={self._buffer.maxlen}>"



# ── Factories de colas multiproceso ────────────────────────────
def make_queue(maxsize: int | None = None) -> Queue:
    return Queue(maxsize=maxsize or 0)
