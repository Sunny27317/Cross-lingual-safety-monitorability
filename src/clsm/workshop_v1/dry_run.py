"""Offline synthetic transport exercise. No arbitrary inputs, clients, or scientific metrics."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any

from clsm.downstream.contracts import DataKind, canonical, content_hash, object_hash
from clsm.downstream.fixtures import synthetic_provenance
from clsm.downstream.translation import TranslationControl, TranslationRecord, TranslationRequest
from clsm.track_a_artifacts import artifact_hashes, write_new
from clsm.workshop_v1.fixtures import synthetic_design, synthetic_translator
from clsm.workshop_v1.monitoring import (
    MonitoringBinding,
    MonitorPath,
    VisibleTrace,
    validate_hdt_bindings,
    validate_monitoring_binding,
)
from clsm.workshop_v1.population import Population, select_population, validate_population
from clsm.workshop_v1.preflight import safe_unused_output
from clsm.workshop_v1.records import (
    SYNTHETIC_LABEL,
    Confounds,
    GenerationRecord,
    Identity,
    full_design,
    validate_generations,
)


class SyntheticBackend:
    """Fixed transport marker, never plausible model reasoning or answers."""

    def generate(self, identity: Identity) -> str:
        if not identity.generation_id.startswith("synthetic-generation-"):
            raise ValueError("synthetic backend requires fixture identity")
        return f"{SYNTHETIC_LABEL}\nTRANSPORT MARKER ONLY: {identity.generation_id}\nNO ANSWER OR COT"


def synthetic_records(
    *,
    code_commit: str,
    working_tree_hash: str,
    environment_hash: str,
    created_utc: str,
) -> tuple[Population, tuple[GenerationRecord, ...]]:
    study, snapshot = synthetic_design()
    population = select_population(study, snapshot)
    validate_population(study, snapshot, population)
    backend = SyntheticBackend()
    records = []
    assert study.dataset is not None and study.designation is not None
    for identity in full_design(study, population):
        item = next(i for i in population.items if i.source_item_id == identity.source_item_id)
        model = next(m.spec for m in study.models if m.spec and m.spec.model_id == identity.model_id)
        cue = next(c.spec for c in study.conditions if c.condition == identity.condition)
        assert model is not None and cue is not None
        item_text = next(r.text for r in item.renderings if r.language == identity.language)
        cue_rendering = next(r for r in cue.renderings if r.language == identity.language)
        template = next(p for p in study.prompts if p.language == identity.language)
        prompt = template.template.format(item=item_text, cue=cue_rendering.text)
        output = backend.generate(identity)
        records.append(
            GenerationRecord(
                data_kind=DataKind.SYNTHETIC,
                label=SYNTHETIC_LABEL,
                study_id=study.study_id,
                study_hash=study.artifact_hash,
                designation=study.designation,
                code_commit=code_commit,
                working_tree_hash=working_tree_hash,
                environment_hash=environment_hash,
                population_hash=population.artifact_hash,
                identity=identity,
                dataset=study.dataset,
                source_item_hash=item.artifact_hash,
                category=item.category,
                difficulty_metadata=item.difficulty_metadata,
                model=model,
                cue=cue,
                cue_text_hash=cue_rendering.text_hash,
                prompt_template_hash=template.template_hash,
                prompt=prompt,
                prompt_hash=content_hash(prompt),
                created_utc=created_utc,
                output_path=f"outputs/{identity.generation_id}.txt",
                output_text=output,
                output_hash=content_hash(output),
                parser_version=model.parser_version,
                confounds=Confounds(),
            )
        )
    result = tuple(records)
    validate_generations(result, study, population)
    return population, result


def synthetic_routes(
    generation: GenerationRecord,
) -> tuple[VisibleTrace, tuple[MonitoringBinding, ...], tuple[TranslationRequest, TranslationRecord] | None]:
    """Create routing fixtures only. No monitor label or reference judgment is fabricated."""
    if generation.data_kind is not DataKind.SYNTHETIC:
        raise ValueError("synthetic routing rejects scientific records")
    study, snapshot = synthetic_design()
    population = select_population(study, snapshot)
    trace = VisibleTrace(
        data_kind=DataKind.SYNTHETIC,
        identity=generation.identity,
        generation_record_hash=generation.artifact_hash,
        parser_version=generation.parser_version,
        text=generation.output_text,
        text_hash=generation.output_hash,
        extraction_evidence_hash=content_hash("synthetic marker passthrough; not a CoT extraction"),
    )
    translation = None
    paths = (
        (MonitorPath.ENGLISH_BASELINE,)
        if generation.identity.language == "en"
        else (
            MonitorPath.NATIVE_HUMAN_REFERENCE,
            MonitorPath.DIRECT_URDU_MONITOR,
            MonitorPath.TRANSLATED_TO_ENGLISH_MONITOR,
        )
    )
    bindings = []
    for path in paths:
        human = path is MonitorPath.NATIVE_HUMAN_REFERENCE
        translated = path is MonitorPath.TRANSLATED_TO_ENGLISH_MONITOR
        spec = study.monitoring.human_reference if human else study.monitoring.automated_monitor
        assert spec is not None
        if translated:
            translator = synthetic_translator()
            request = TranslationRequest(
                blind_id=trace.artifact_hash,
                root_trace_hash=trace.text_hash,
                source_text=trace.text,
                source_hash=trace.text_hash,
                source_language="ur",
                target_language="en",
                control=TranslationControl.URDU_TO_ENGLISH,
                parent_translation_hash=None,
            )
            text = f"{SYNTHETIC_LABEL}: translation transport marker; NOT TRANSLATED\n{trace.artifact_hash}"
            record = TranslationRecord(
                request_hash=request.artifact_hash,
                source_trace_hash=trace.text_hash,
                source_hash=trace.text_hash,
                source_language="ur",
                translated_text=text,
                output_hash=content_hash(text),
                translator_spec=translator,
                translator_spec_hash=translator.artifact_hash,
                measured_input_units=len(trace.text),
                reserved_output_units=len(text),
                truncated=False,
                errors=(),
                provenance=synthetic_provenance(),
            )
            translation = (request, record)
        binding = MonitoringBinding(
            data_kind=DataKind.SYNTHETIC,
            identity=trace.identity,
            source_generation_hash=generation.artifact_hash,
            visible_trace_hash=trace.artifact_hash,
            path=path,
            actor="human" if human else "automated",
            specification_hash=spec.artifact_hash,
            judge_input_language="en" if translated else trace.identity.language,
            judge_input_hash=translation[1].output_hash if translated and translation else trace.text_hash,
            translation_record_hash=translation[1].artifact_hash if translated and translation else None,
        )
        validate_monitoring_binding(
            binding,
            trace,
            generation,
            study,
            population=population,
            translation=translation if translated else None,
        )
        bindings.append(binding)
    if len(bindings) == 3:
        validate_hdt_bindings(*bindings)
    return trace, tuple(bindings), translation


def run(output: Path) -> dict[str, Any]:
    """The only writer; exclusively built-in fixtures. New named directory required."""
    output = safe_unused_output(output, synthetic=True)
    root = Path(__file__).resolve().parents[3]
    commit = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
    ).stdout.strip()
    # Bind all package Python source, including uncommitted changes; no results/data read.
    source_files = sorted((root / "src/clsm").rglob("*.py"))
    source_hashes = {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files
    }
    environment = {
        "python": platform.python_version(),
        "pydantic": version("pydantic"),
        "numpy": version("numpy"),
        "pyyaml": version("pyyaml"),
        "platform": platform.platform(),
    }
    population, records = synthetic_records(
        code_commit=commit,
        working_tree_hash=object_hash(source_hashes),
        environment_hash=object_hash(environment),
        created_utc=datetime.now(UTC).isoformat(),
    )
    study, snapshot = synthetic_design()
    routes = [synthetic_routes(record) for record in records]
    # Prepare/validate every fixture before the first write. Exclusive mkdir/file writes;
    # failure leaves a clearly labeled incomplete directory, never a completed-looking run.
    output.mkdir(exist_ok=False)

    def write(name: str, text: str) -> None:
        write_new(output / name, text)

    write("README.txt", f"{SYNTHETIC_LABEL}\nOffline transport fixtures; no scientific outcomes.\n")
    (output / "outputs").mkdir()
    for record in records:
        write(record.output_path, record.output_text)
    write("study.json", study.model_dump_json(indent=2))
    write("snapshot.json", snapshot.model_dump_json(indent=2))
    write("population.json", population.model_dump_json(indent=2))
    write("generations.jsonl", "\n".join(r.model_dump_json() for r in records) + "\n")
    write(
        "routing.json",
        canonical(
            {
                "label": SYNTHETIC_LABEL,
                "traces": [trace.model_dump(mode="json") for trace, _, _ in routes],
                "bindings": [b.model_dump(mode="json") for _, bindings, _ in routes for b in bindings],
                "translations": [
                    [r.model_dump(mode="json") for r in translation]
                    for _, _, translation in routes
                    if translation
                ],
            }
        ),
    )
    artifacts = artifact_hashes(output)
    manifest = {
        "label": SYNTHETIC_LABEL,
        "status": "synthetic transport checks complete",
        "scientific_outcomes": "NOT RUN",
        "code_commit": commit,
        "source_hashes": source_hashes,
        "environment": environment,
        "study_hash": study.artifact_hash,
        "population_hash": population.artifact_hash,
        "fixture_generation_count": len(records),
        "model_families": 2,
        "language_roles": 2,
        "cue_conditions": 3,
        "artifact_hashes": artifacts,
    }
    write("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        manifest = run(args.output)
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({"label": SYNTHETIC_LABEL, "error": str(exc)}))
        return 1
    print(
        json.dumps(
            {
                "label": SYNTHETIC_LABEL,
                "fixture_generation_count": manifest["fixture_generation_count"],
                "scientific_outcomes": "NOT RUN",
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
