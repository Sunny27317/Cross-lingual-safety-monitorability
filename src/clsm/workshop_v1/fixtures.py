"""Tiny synthetic-only fixtures; no real task, model, translation, or human annotation."""

from __future__ import annotations

from clsm.downstream.contracts import DataKind, content_hash, object_hash
from clsm.downstream.contracts import Decoding as MonitorDecoding
from clsm.downstream.fixtures import synthetic_provenance
from clsm.downstream.translation import TranslatorSpec
from clsm.workshop_v1.config import (
    Condition,
    CueRendering,
    CueSlot,
    CueSpec,
    DatasetSpec,
    Decoding,
    HumanReferenceSpec,
    Language,
    ModelSlot,
    ModelSpec,
    Monitoring,
    PromptSpec,
    Sampling,
    ServiceSpec,
    Study,
)
from clsm.workshop_v1.population import DatasetSnapshot, ItemRendering, SourceItem, snapshot_content_hash
from clsm.workshop_v1.records import SYNTHETIC_LABEL

LANGUAGES: tuple[Language, Language] = ("en", "ur")


def synthetic_translator() -> TranslatorSpec:
    return TranslatorSpec(
        provider="synthetic-local",
        model="synthetic-translator",
        version="synthetic-v1",
        context_limit=10000,
        context_unit="characters",
        context_accounting="synthetic-only",
        source_language="ur",
        target_language="en",
        decoding=MonitorDecoding(
            temperature=0.0,
            top_p=1.0,
            max_output_tokens=64,
            seed=0,
            determinism_note="synthetic-only",
        ),
        prompt=SYNTHETIC_LABEL,
        identity_evidence="synthetic-only",
        provenance=synthetic_provenance(),
    )


def synthetic_design() -> tuple[Study, DatasetSnapshot]:
    items = tuple(
        SourceItem(
            source_item_id=f"synthetic-item-{index}",
            category="synthetic-category",
            difficulty_metadata=None,
            equivalence_status="synthetic_only",
            equivalence_evidence=None,
            renderings=tuple(
                ItemRendering(
                    language=language,
                    text=f"{SYNTHETIC_LABEL}: item={index}, language-role={language}",
                    text_hash=content_hash(f"{SYNTHETIC_LABEL}: item={index}, language-role={language}"),
                )
                for language in LANGUAGES
            ),  # type: ignore[arg-type]  # exactly two fixed language roles above
        )
        for index in range(3)
    )
    dataset = DatasetSpec(
        dataset_id="synthetic-dataset",
        revision="synthetic-v1",
        split="synthetic",
        content_hash=snapshot_content_hash(items),
        license_evidence="synthetic-only",
        provenance_evidence="synthetic-only built-in fixtures",
    )
    snapshot = DatasetSnapshot(data_kind=DataKind.SYNTHETIC, dataset=dataset, items=items)
    decoding = Decoding(
        temperature=0.0,
        top_p=1.0,
        top_k=None,
        repetition_penalty=1.0,
        max_new_tokens=1,
        stop_sequences=(),
        sampling_mode="synthetic-deterministic-marker",
        determinism_note="synthetic-only",
        additional_settings_hash=object_hash({}),
    )
    models = tuple(
        ModelSlot(
            slot_id=f"synthetic-slot-{index}",
            status="frozen",
            spec=ModelSpec(
                model_id=f"synthetic-model-{index}",
                model_family=f"synthetic-family-{index}",
                revision="synthetic-v1",
                checkpoint_hash=content_hash(f"synthetic-checkpoint-{index}"),
                open_weight_evidence="synthetic-only; no actual weights",
                tokenizer_id="synthetic-tokenizer",
                tokenizer_revision="synthetic-v1",
                tokenizer_hash=content_hash("synthetic-tokenizer"),
                runtime="synthetic-local",
                runtime_version="synthetic-v1",
                backend="synthetic-marker",
                backend_version="synthetic-v1",
                quantization="none",
                decoding=decoding,
                parser_version="synthetic-marker/1",
                decision_record="synthetic fixture; not a scientific model selection",
            ),
        )
        for index in range(2)
    )
    cues = []
    for condition in Condition:
        renderings = []
        for language in LANGUAGES:
            text = (
                ""
                if condition is Condition.CONTROL
                else (
                    f"SYNTHETIC FIXTURE CUE {condition.value} language-role={language}; no scientific wording"
                )
            )
            renderings.append(CueRendering(language=language, text=text, text_hash=content_hash(text)))
        cues.append(
            CueSlot(
                condition=condition,
                status="frozen",
                spec=CueSpec(
                    cue_id=f"synthetic-{condition.value}",
                    version="synthetic-v1",
                    renderings=(renderings[0], renderings[1]),
                    target_rule="synthetic marker only",
                    equivalence_evidence="synthetic-only; no linguistic equivalence claimed",
                    decision_record="synthetic fixture; not scientific cue wording",
                ),
            )
        )
    prompts = tuple(
        PromptSpec(
            language=language,
            version="synthetic-v1",
            template="{item}\n{cue}",
            template_hash=content_hash("{item}\n{cue}"),
            renderer_version="synthetic-format/1",
            decision_record="synthetic fixture only",
        )
        for language in LANGUAGES
    )
    translator = synthetic_translator()
    study = Study(
        study_id="synthetic-workshop-v1",
        data_kind=DataKind.SYNTHETIC,
        status="frozen",
        designation="exploratory",
        scope="tested_models_and_settings_only",
        languages=LANGUAGES,
        models=models,
        conditions=(cues[0], cues[1], cues[2]),
        dataset=dataset,
        prompts=prompts,
        sampling=Sampling(
            planning_target_only=200,
            n_source_items=2,
            population_role="pilot",
            selection_rule="sha256_source_id_v1",
            selection_seed=0,
            selection_decision="synthetic-only",
            seeds=(0,),
            pairing="complete",
            pairing_decision="synthetic-only Cartesian fixture",
            sample_size_rationale="tiny synthetic test; no scientific sample-size rationale",
        ),
        monitoring=Monitoring(
            automated_monitor=ServiceSpec(
                service_id="synthetic-monitor",
                revision="synthetic-v1",
                specification_hash=content_hash("synthetic-monitor-only"),
                selection_record="synthetic-only",
            ),
            translator=ServiceSpec(
                service_id=translator.model,
                revision=translator.version,
                specification_hash=translator.artifact_hash,
                selection_record="synthetic-only",
            ),
            human_reference=HumanReferenceSpec(
                protocol_version="synthetic-v1",
                protocol_hash=content_hash("synthetic-human-protocol"),
                rubric_hash=content_hash("synthetic-rubric"),
                population_role="workshop_v1_native_urdu",
                decision_record="synthetic routing fixture; no human annotation",
            ),
        ),
        protocol_hash=content_hash("synthetic-protocol"),
        decision_record="synthetic-only",
    )
    return study, snapshot
