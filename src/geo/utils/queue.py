from typing import Any


class Queue:
    def __init__(self):
        self._data = []

    def enqueue(self, item: Any) -> None:
        self._data.append(item)

    def dequeue(self) -> Any | None:
        return self._data.pop(0) if self._data else None

    def is_empty(self) -> bool:
        return not bool(self._data)
