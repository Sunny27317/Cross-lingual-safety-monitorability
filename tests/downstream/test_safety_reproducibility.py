from __future__ import annotations

import ast
import json
import socket
import subprocess
from pathlib import Path

import pytest
from pydantic import ValidationError

from clsm.downstream.__main__ import main
from clsm.downstream.fixtures import fixture_report, synthetic_bundle, synthetic_provenance
from clsm.downstream.reporting import measurement_envelope


def test_synthetic_cli_has_no_scientific_input_option(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("sys.argv", ["downstream", "fixture-check"])
    main()
    output = json.loads(capsys.readouterr().out)
    assert output["report"]["provenance"]["data_kind"] == "synthetic"
    monkeypatch.setattr("sys.argv", ["downstream", "fixture-check", "--input", "pilot-output/traces.json"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code != 0


def test_network_and_subprocess_guard_is_active() -> None:
    with pytest.raises(AssertionError, match="synthetic-only"):
        socket.create_connection(("example.invalid", 80))
    with pytest.raises(AssertionError, match="synthetic-only"):
        subprocess.run(["not-a-real-command"], check=True)


def test_no_downstream_execution_or_authorization_imports() -> None:
    forbidden = {
        "subprocess",
        "requests",
        "httpx",
        "datasets",
        "transformers",
        "torch",
        "vllm",
        "socket",
        "clsm.track_a_backend",
        "clsm.track_a_run",
        "clsm.track_a_execute",
        "clsm.generation",
    }
    for path in Path("src/clsm/downstream").glob("*.py"):
        tree = ast.parse(path.read_text())
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
        assert not imports & forbidden, path


def test_versions_and_report_bindings_are_complete() -> None:
    report = fixture_report()
    assert {v.package for v in report.provenance.software_versions} >= {"python", "numpy", "pydantic"}
    roles = {b.role for b in report.bindings}
    assert roles >= {
        "trace_set",
        "judge_spec",
        "label_policy",
        "human_reference",
        "annotations",
        "direct",
        "translated",
        "translations",
        "analysis_bundle",
        "annotation_packet",
        "private_assignment",
    }
    assert report.provenance.git_sha == "0" * 40  # explicit synthetic placeholder, never a real run identity
    with pytest.raises(ValidationError):
        type(report.provenance).model_validate_json(
            report.provenance.model_dump_json().replace('"synthetic"', '"scientific"')
        )
    p = synthetic_provenance()
    with pytest.raises(ValidationError, match="versions required"):
        type(p).model_validate({**p.model_dump(), "software_versions": ()})


def test_unchecked_model_mutation_does_not_evade_bundle_validation() -> None:
    b = synthetic_bundle()
    bad = b.direct[0].model_copy(update={"label": "made up"})
    with pytest.warns(UserWarning, match="serializer"), pytest.raises(ValueError):
        measurement_envelope(b.model_copy(update={"direct": (bad, *b.direct[1:])}), synthetic_provenance())
