"""Future English generator entry point. PRE-RUN tooling only: do not run without human review.

Stops after trace collection, parsing and completion accounting. Never judges or analyzes effects.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path

import yaml

from clsm.config import load_experiment_config
from clsm.track_a_artifacts import artifact_hashes, completion_from_records, write_new
from clsm.track_a_backend import LlamaCppBackend, load_llamacpp_runtime
from clsm.track_a_dataset_pin import canonical_json, load_pin, utcnow
from clsm.track_a_plan import build_plan, validate_pilot_workload
from clsm.track_a_preflight import CONFIG, RUNTIME, add_arguments, arguments, preflight
from clsm.track_a_run import authorize_track_a_run, capture_track_a_provenance, scientific_config_dict


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_arguments(parser)
    args = parser.parse_args(argv)
    options = arguments(args)
    report = preflight(**options)
    if not report.ready:
        print(report.model_dump_json(indent=2))
        return 1
    # No injected backend, preflight report or token factory is accepted by this command.
    token = authorize_track_a_run(**{k: v for k, v in options.items() if k != "stage"})
    cfg = load_experiment_config(CONFIG)
    runtime = load_llamacpp_runtime(RUNTIME)
    pin = load_pin(args.pin, cfg.dataset, require_real=True)
    if pin.content_sha256 != token.dataset_content_hash:
        raise ValueError("dataset content changed after authorization")
    specs = build_plan(cfg, pin, cfg.experiment_name)
    validate_pilot_workload(specs)
    output = Path(token.output_dir)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()  # exclusive reservation: never reuse/resume an existing run
    started = utcnow()
    write_new(output / "dataset_pin.json", pin.model_dump_json(indent=2))
    write_new(output / "plan.json", canonical_json([asdict(s) for s in specs]))
    write_new(
        output / "config.json",
        canonical_json(
            {
                "experiment": cfg.model_dump(),
                "runtime": yaml.safe_load(RUNTIME.read_text()),
                "scientific": scientific_config_dict(cfg, yaml.safe_load(RUNTIME.read_text())),
            }
        ),
    )
    backend = LlamaCppBackend(cfg.model, cfg.decoding, runtime, token, raw_dir=output / "raw")
    provenance = capture_track_a_provenance(
        token,
        experiment_id=cfg.experiment_name,
        llama_cpp_version_string=report.runtime_version or "",
        llama_cpp_build=report.runtime_build,
        gguf_sha256_verified=True,
        llama_cpp_identity_verified=True,
        datasets_library_version=pin.datasets_library_version,
        dataset_content_hash=pin.content_sha256,
        dataset_item_ids=pin.exact_item_ids,
        dataset_schema_verified=pin.schema_verified,
    )
    write_new(output / "provenance.json", provenance.model_dump_json(indent=2))
    records = []
    # Append and fsync each record; interrupted runs retain diagnostics, never get completion.json.
    import os

    with (output / "generations.jsonl").open("x", encoding="utf-8") as stream:
        for spec in specs:
            rec = backend.generate([spec])[0]  # exactly one attempt; no retry loop
            records.append(rec)
            stream.write(rec.model_dump_json() + "\n")
            stream.flush()
            os.fsync(stream.fileno())
    completion = completion_from_records(
        specs,
        records,
        scientific_hash=token.scientific_hash,
        git_commit=token.git_commit,
        dataset_content_hash=pin.content_sha256,
        raw_hashes=artifact_hashes(output / "raw"),
        started_utc=started,
        finished_utc=utcnow(),
    )
    completion.output_artifacts = artifact_hashes(output)
    write_new(output / "completion.json", completion.model_dump_json(indent=2))
    print("English trace collection complete. STOP: no judge, Urdu or confirmatory work authorized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
