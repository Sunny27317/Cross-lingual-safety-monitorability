"""Structured logging + append-only JSONL writing.

- :class:`JsonlWriter` — one validated record per line, flushed, append-only.
- :func:`get_logger` — a plain stdlib logger with a consistent format.

No logging backend beyond local files (readiness §15: "No W&B for the pilot").
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from types import TracebackType
from typing import IO, Any

from pydantic import BaseModel

_LOG_FORMAT = "%(asctime)s %(levelname)-7s %(name)s | %(message)s"


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


class JsonlWriter:
    """Append-only JSONL writer. Each ``write`` takes a pydantic model or a plain dict.

    Opens in append mode so a re-run never truncates a prior run's data by accident.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh: IO[str] | None = None
        self.count = 0

    def __enter__(self) -> JsonlWriter:
        self._fh = self.path.open("a", encoding="utf-8")
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if self._fh is not None:
            self._fh.flush()
            self._fh.close()
            self._fh = None

    def write(self, record: BaseModel | dict[str, Any]) -> None:
        if self._fh is None:
            raise RuntimeError("JsonlWriter used outside of a `with` block")
        payload = record.model_dump(mode="json") if isinstance(record, BaseModel) else record
        self._fh.write(json.dumps(payload, sort_keys=True, ensure_ascii=False) + "\n")
        self._fh.flush()
        self.count += 1


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


__all__ = ["JsonlWriter", "get_logger", "read_jsonl"]
