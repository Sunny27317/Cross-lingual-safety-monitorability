"""Downstream tests cannot run subprocesses, access networks, or open scientific paths."""

from __future__ import annotations

import builtins
import io
import socket
import subprocess
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture(autouse=True)
def synthetic_only(monkeypatch: pytest.MonkeyPatch) -> None:
    def refuse(*args: Any, **kwargs: Any) -> Any:
        raise AssertionError("downstream tests are synthetic-only: network/subprocess refused")

    original_open, original_io_open = builtins.open, io.open

    def check_path(file: Any) -> None:
        if isinstance(file, (str, Path)):
            name = str(file).replace("\\", "/").lower()
            if any(
                part in name for part in ("experiments/_runs", "pilot-output", "dataset_content_pin", ".gguf")
            ):
                raise AssertionError("scientific data path forbidden in downstream synthetic tests")

    def guarded_open(file: Any, *args: Any, **kwargs: Any) -> Any:
        check_path(file)
        return original_open(file, *args, **kwargs)

    def guarded_io_open(file: Any, *args: Any, **kwargs: Any) -> Any:
        check_path(file)
        return original_io_open(file, *args, **kwargs)

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(subprocess, "Popen", refuse)
    monkeypatch.setattr(builtins, "open", guarded_open)
    monkeypatch.setattr(io, "open", guarded_io_open)
