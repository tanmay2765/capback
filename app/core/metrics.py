"""Lightweight in-process metrics hooks.

Phase 1 keeps this intentionally simple so Prometheus/Grafana can be
wired later without rewriting call sites.
"""

from __future__ import annotations

from collections import defaultdict
from threading import Lock
from typing import DefaultDict


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: DefaultDict[str, int] = defaultdict(int)

    def increment(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counters[name] += value

    def snapshot(self) -> dict[str, int]:
        with self._lock:
            return dict(self._counters)

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()


metrics = MetricsRegistry()
