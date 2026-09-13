"""Synthetic-only downstream dry run; never reads a project-data path."""

from __future__ import annotations

from typing import Any

from clsm.downstream.contracts import content_hash
from clsm.downstream.fixtures import fixture_report, synthetic_bundle
from clsm.downstream.matching import MatchedHDTP, TraceIdentityKey
from clsm.downstream.reporting import result_tables_from_payload


def synthetic_downstream_dry_run() -> dict[str, Any]:
    bundle = synthetic_bundle()
    report = fixture_report()
    identity = TraceIdentityKey(
        source_item_id="synthetic-item-0",
        condition="control",
        language="ur",
        seed=0,
        generation_id="synthetic-generation-0",
    )
    matched = MatchedHDTP(
        identity=identity,
        source_trace_hash=content_hash("synthetic-source-trace"),
        rendered_language="en",
        judge_input_language="en",
        human_label_id=bundle.reference.labels[0].source_annotation_hashes[0],
        direct_label_id=bundle.direct[0].raw_response_hash,
        translated_label_id=bundle.translated[0].raw_response_hash,
        paraphrase_label_id=None,
        translation_or_rewrite_hash=bundle.translations[0][1].output_hash,
    )
    return {
        "status": "SYNTHETIC — NOT SCIENTIFIC DATA",
        "report": report.model_dump(mode="json"),
        "tables": result_tables_from_payload(report.payload),
        "matched_hdtp": matched.model_dump(mode="json"),
        "provenance": report.provenance.model_dump(mode="json"),
    }
