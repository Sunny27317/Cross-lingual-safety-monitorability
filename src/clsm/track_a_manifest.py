"""Track-A pilot manifest: a machine-readable freeze of the pilot design.

One object that records every scientific-run decision and its status. Unresolved
requirements are represented **explicitly** (``BLOCKED`` / ``DEFERRED`` /
``NOT_APPLICABLE``), never silently omitted. :func:`check_run_ready` fails loudly if a
field that must be locked before *generator inference* is still unresolved.

The final checklist/preflight combines this methodology record with real content-pin
evidence and human authorization. This record does not itself authorize anything.

Design: PILOT_PROTOCOL.md, PILOT_PREREGISTRATION.md, DECISION_LOG D-041..D-049.
"""

from __future__ import annotations

import enum
import json
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field

from clsm.config import ExperimentConfig, load_experiment_config

SCHEMA_VERSION = "track-a-pilot-manifest/1"
PROTOCOL_VERSION = "track-a-en-hint-pilot/2026-09-10"


class RunStage(enum.StrEnum):
    GENERATOR = "generator"
    JUDGE = "judge"
    HUMAN_VALIDATION = "human_validation"
    URDU = "urdu"
    CONFIRMATORY = "confirmatory"


# D-066: stage membership is code-frozen, not controlled by editable per-field flags.
_DOWNSTREAM = {
    "disclosure_judge", "human_disclosure_audit", "ethics_determination",
    "translation_protocol", "native_urdu_validation", "confirmatory_sample_size",
}
_STAGE_EXTRA = {
    RunStage.GENERATOR: set(),
    RunStage.HUMAN_VALIDATION: {"human_disclosure_audit", "ethics_determination"},
    RunStage.JUDGE: {"disclosure_judge", "human_disclosure_audit", "ethics_determination"},
    RunStage.URDU: {"disclosure_judge", "human_disclosure_audit", "ethics_determination",
                    "translation_protocol", "native_urdu_validation"},
    RunStage.CONFIRMATORY: _DOWNSTREAM,
}


class Status(enum.StrEnum):
    LOCKED = "LOCKED"                # frozen; a value is present and final
    BLOCKED = "BLOCKED"             # cannot be resolved without an external dependency
    DEFERRED = "DEFERRED"          # deliberately postponed to a later milestone/stage
    NOT_APPLICABLE = "NOT_APPLICABLE"


class BlockKind(enum.StrEnum):
    METHODOLOGY = "methodology"          # an unresolved choice that could bias results
    EXTERNAL_RESOURCE = "external_resource"  # blocked only by a missing tool / person / approval
    NONE = "none"


class Field_(BaseModel):
    """One decision in the manifest."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: Status
    value: str | None = None
    decision_log: str | None = Field(default=None, description="e.g. 'D-044'")
    note: str | None = None
    blocking_for_run: bool = Field(
        default=True,
        description="If True and status not in {LOCKED, NOT_APPLICABLE}, check_run_ready() fails.",
    )
    block_kind: BlockKind = BlockKind.NONE


class TrackAPilotManifest(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: str = SCHEMA_VERSION
    protocol_version: str = PROTOCOL_VERSION
    made_before_scientific_outcomes_observed: bool = True

    # --- runtime / generator (infrastructure — already gated A/B/C) ---
    generator_model: Field_
    generator_artifact_sha256: Field_
    generator_gguf_revision: Field_
    runtime_llamacpp_commit: Field_

    # --- experiment design ---
    dataset: Field_
    dataset_revision: Field_
    dataset_content_pin: Field_
    split: Field_
    item_selection_rule: Field_
    sample_size_pilot: Field_
    confirmatory_sample_size: Field_
    stopping_rule: Field_
    seed_schedule: Field_
    samples_per_condition: Field_
    condition_names: Field_
    prompt_template_version: Field_
    prompt_template_sha256: Field_
    hint_wording: Field_
    hint_seed: Field_
    hint_target_rule: Field_

    # --- generation ---
    generation_interface: Field_
    decoding_parameters: Field_
    reasoning_format: Field_
    thinking_mode: Field_

    # --- parsing / output ---
    parser_version: Field_
    output_cleaning_rule: Field_
    raw_output_policy: Field_

    # --- failure handling ---
    retry_policy: Field_
    missingness_policy: Field_
    tie_policy: Field_
    truncation_policy: Field_

    # --- analysis ---
    primary_estimand: Field_
    secondary_estimands: Field_
    diagnostic_metrics: Field_
    uncertainty_method: Field_
    multiplicity_policy: Field_

    # --- monitors / audit (downstream milestones or external deps) ---
    disclosure_judge: Field_
    human_disclosure_audit: Field_
    translation_protocol: Field_
    native_urdu_validation: Field_
    ethics_determination: Field_

    def stage_unresolved(self, stage: RunStage) -> list[str]:
        """Required later-stage fields cannot pass with an English-only NOT_APPLICABLE."""
        required = (set(self._fields()) - _DOWNSTREAM) | _STAGE_EXTRA[stage]
        return sorted(name for name in required if self._fields()[name].status is not Status.LOCKED
                      or not self._fields()[name].value)

    def blocking_unresolved(self) -> list[str]:
        """Names of run-blocking fields that are neither LOCKED nor NOT_APPLICABLE."""
        out: list[str] = []
        for name, f in self._fields().items():
            if not f.blocking_for_run:
                continue
            if f.status not in (Status.LOCKED, Status.NOT_APPLICABLE):
                out.append(name)
        return out

    def unresolved_by_kind(self, kind: BlockKind) -> list[str]:
        return [
            name for name in self.blocking_unresolved()
            if self._fields()[name].block_kind is kind
        ]

    def _fields(self) -> dict[str, Field_]:
        return {k: v for k, v in self.__dict__.items() if isinstance(v, Field_)}

    def run_ready(self) -> bool:
        return not self.blocking_unresolved()

    def methodology_frozen(self) -> bool:
        """True iff NO run-blocking field is unresolved for a METHODOLOGY reason."""
        return not self.unresolved_by_kind(BlockKind.METHODOLOGY)

    def status_summary(self) -> dict[str, int]:
        counts: dict[str, int] = {s.value: 0 for s in Status}
        for f in self._fields().values():
            counts[f.status.value] += 1
        return counts


class ManifestNotRunReady(RuntimeError):
    pass


def check_run_ready(manifest: TrackAPilotManifest, *, stage: RunStage | None = None) -> None:
    """Raise :class:`ManifestNotRunReady` listing every run-blocking unresolved field.

    Without a stage this retains the conservative legacy aggregate check. Actual
    generation uses full staged preflight, not this metadata-only check.
    """
    unresolved = manifest.stage_unresolved(stage) if stage is not None else manifest.blocking_unresolved()
    if unresolved:
        raise ManifestNotRunReady(
            "Track-A pilot is NOT run-ready. Run-blocking fields still unresolved:\n  - "
            + "\n  - ".join(unresolved)
        )


def load_manifest(path: str | Path) -> TrackAPilotManifest:
    return TrackAPilotManifest.model_validate_json(Path(path).read_text(encoding="utf-8"))


def manifest_from_config(cfg: ExperimentConfig) -> dict[str, str]:
    """Cross-check helper: the subset of manifest values that must equal the loaded
    ``ExperimentConfig``. Used in tests to catch config/manifest drift."""
    return {
        "generator_model": cfg.model.id,
        "generator_gguf_revision": cfg.model.revision,
        "dataset": cfg.dataset.id,
        "dataset_revision": cfg.dataset.revision or "",
        "split": cfg.dataset.split,
        "sample_size_pilot": str(len(cfg.dataset.subjects) * cfg.dataset.items_per_subject),
        "samples_per_condition": str(cfg.decoding.samples_per_condition),
        "seed_schedule": ",".join(str(s) for s in cfg.decoding.seeds),
        "prompt_template_version": cfg.prompt_template_version,
        "hint_wording": cfg.cue.template,
        "hint_seed": str(cfg.hint_seed),
    }


def build_pilot_manifest(config_path: str | Path = "configs/track_a_pilot/pilot.yaml") -> TrackAPilotManifest:
    """Construct the canonical Track-A pilot manifest from the frozen config + the
    decisions in DECISION_LOG D-041..D-049. The disclosure judge, translation, and
    native-Urdu arms are honestly BLOCKED/DEFERRED."""
    import hashlib

    cfg = load_experiment_config(config_path)
    n = len(cfg.dataset.subjects) * cfg.dataset.items_per_subject
    prompt_sha = hashlib.sha256(cfg.prompt_template.encode("utf-8")).hexdigest()

    # N4: the manifest's hard-coded GGUF SHA-256 must equal the committed runtime pin.
    _rt_yaml = yaml.safe_load(
        Path("configs/track_a_pilot/runtime_llamacpp.yaml").read_text(encoding="utf-8")
    )
    _gguf_sha = str(_rt_yaml["model"]["sha256"])
    _llama_commit = str(_rt_yaml["runtime"]["commit"])
    _llama_build = str(_rt_yaml["runtime"].get("build_number", ""))

    def L(value: str, decision_log: str, note: str | None = None) -> Field_:
        return Field_(status=Status.LOCKED, value=value, decision_log=decision_log, note=note)

    def blocked_ext(decision_log: str, note: str, *, run_blocking: bool = True) -> Field_:
        return Field_(
            status=Status.BLOCKED, decision_log=decision_log, note=note,
            blocking_for_run=run_blocking, block_kind=BlockKind.EXTERNAL_RESOURCE,
        )

    def not_applicable(decision_log: str, note: str) -> Field_:
        return Field_(
            status=Status.NOT_APPLICABLE, decision_log=decision_log, note=note,
            blocking_for_run=False,
        )

    return TrackAPilotManifest(
        generator_model=L(cfg.model.id, "D-034"),
        generator_artifact_sha256=L(_gguf_sha, "D-037", note="cross-checked vs runtime_llamacpp.yaml (N4)"),
        generator_gguf_revision=L(cfg.model.revision, "D-034"),
        runtime_llamacpp_commit=L(
            _llama_commit, "D-033/D-036",
            note=f"build b{_llama_build}; VERIFIED at runtime vs `llama-cli --version` (D-052)",
        ),
        dataset=L(cfg.dataset.id, "D-041"),
        dataset_revision=L(cfg.dataset.revision or "", "D-041", note="HF refs API verified; NOT downloaded"),
        dataset_content_pin=blocked_ext(
            "D-041/D-056",
            "BLOCKS RUN (Part 9). Before any real inference the following must be recorded: "
            "(a) the exact `datasets` library version, (b) the resolved parquet/commit "
            "revision actually read, (c) the exact selected item identifiers, (d) a hash "
            "over the selected item CONTENT, (e) verified question/choice schema + choice "
            "ordering, (f) verified label->letter mapping. No content is downloaded in this "
            "pass; the gate stays BLOCKED until this is done.",
        ),
        split=L(cfg.dataset.split, "D-041"),
        item_selection_rule=L(
            "sha256_sorted_first_n over eligible items; 10 fixed stratified subjects x 5", "D-041"
        ),
        sample_size_pilot=L(str(n), "D-045", note="PIPELINE VALIDATION ONLY; not powered"),
        confirmatory_sample_size=Field_(
            status=Status.DEFERRED, decision_log="D-045/D-058",
            note="REQUIRES HUMAN SCIENTIFIC DECISION BEFORE CONFIRMATORY DESIGN. No fixed N "
            "and no SESOI are frozen here (Part 12). POWER_ANALYSIS.md is a sensitivity / "
            "design-exploration illustration only; the pilot may inform NUISANCE parameters "
            "(eligibility yield, parse-failure rate, missingness, descriptive switch yield) "
            "but must not be used to pick a favourable SESOI after seeing effects.",
            blocking_for_run=False, block_kind=BlockKind.METHODOLOGY,
        ),
        stopping_rule=L(
            "fixed n=50 pilot; no optional stopping; no interim looks at effect direction/"
            "magnitude; the pilot is not a hypothesis test", "D-045"
        ),
        seed_schedule=L(",".join(str(s) for s in cfg.decoding.seeds), "D-044"),
        samples_per_condition=L(str(cfg.decoding.samples_per_condition), "D-044"),
        condition_names=L("control (no hint), treatment (one neutral wrong-answer hint)", "D-042"),
        prompt_template_version=L(cfg.prompt_template_version, "D-042"),
        prompt_template_sha256=L(prompt_sha, "D-042"),
        hint_wording=L(cfg.cue.template, "D-042"),
        hint_seed=L(str(cfg.hint_seed), "D-042"),
        hint_target_rule=L("position-neutral sha256 over incorrect indices (D-017)", "D-042/D-017"),
        generation_interface=L(
            "pinned llama-cli (clsm.track_a_backend.LlamaCppBackend); subprocess argv list; "
            "-st --reasoning-format none --no-display-prompt --simple-io. `--no-perf` is NOT "
            "passed (D-053): the STDERR perf block is the token-count / stop-reason signal. "
            "A real run requires an authorized RunToken (D-050).", "D-043/D-050/D-053"
        ),
        decoding_parameters=L(
            "temp 0.6, top_p 0.95, top_k 20, min_p 0, presence_penalty 0, repeat_penalty 1.0, "
            "max_new_tokens 16384 (cap), n_ctx 32768", "D-044"
        ),
        reasoning_format=L("none (literal <think>...</think> preserved)", "D-038/D-043"),
        thinking_mode=L("enable_thinking=true (Qwen3 default)", "D-044"),
        parser_version=L(
            "clsm.extraction (D-038): ParseStatus + ReasoningSpanStatus + tri-state StopReason "
            "(D-053). Multiple <think> spans: ALL preserved, deterministically combined, "
            "n_reasoning_spans recorded (D-038/Part 20). PRIMARY answer contract is the Latin "
            "A/B/C/D syntax across all languages (Part 13).", "D-038/D-053"
        ),
        output_cleaning_rule=L(
            "clsm.track_a_backend.clean_cli_output (cli_chrome_v2, D-052): removes ONLY two "
            "ANCHORED, proven-runtime-generated strings -- the leading llama-cli startup "
            "banner (\\A .. `available commands:` list) and the exact trailing perf-summary "
            "line (`[ Prompt: .. t/s | Generation: .. t/s ]` at \\Z). NO generic `>` / "
            "structural regex. RAW stdout is always persisted verbatim alongside.", "D-046/D-052"
        ),
        raw_output_policy=L(
            "raw_output stored VERBATIM (semantically unmodified) on every record and to "
            "`<stem>.stdout.txt`; `cleaned` kept separately; never hand-edited", "D-046/D-052"
        ),
        retry_policy=L(
            "ZERO retries (D-054). Exactly one llama-cli invocation per spec, attempt id 'a1', "
            "whatever the output. An infrastructure fault (nonzero exit / timeout / empty "
            "stdout) is recorded + COUNTED as a failure, never retried. NO content-dependent "
            "retry of any kind. Matches implementation, config, and tests.", "D-054"
        ),
        missingness_policy=L(
            "PARSE_ERROR / MALFORMED / missing generation: recorded + COUNTED, never dropped "
            "silently; majority vote runs over VALID samples only", "D-046"
        ),
        tie_policy=L(
            "majority tie -> None (no tie-break); item excluded from majority metrics + counted",
            "D-046",
        ),
        truncation_policy=L(
            "Tri-state stop_reason (D-053): EOS / LENGTH / TIMEOUT / NONZERO_EXIT / UNKNOWN. "
            "`truncated=True` iff stop_reason in {LENGTH, TIMEOUT}. UNKNOWN is recorded "
            "honestly when the runtime gives no reliable signal -- NEVER inferred from a "
            "missing final answer. n_output_tokens + requested max_new_tokens + stop_reason "
            "+ timeout state are all recorded. Raise max_new_tokens only on an infra trigger "
            "(LENGTH rate > 2%).", "D-046/D-053"
        ),
        primary_estimand=L(
            "RESEARCH PRIMARY (DEFERRED, not measurable in this English pilot): the "
            "Monitor-Validity Gap for Urdu = native-human disclosure detection MINUS "
            "automated-monitor disclosure detection on the SAME traces. "
            "RESEARCH SECONDARY (DEFERRED): the Translate-then-Monitor Recovery Effect. "
            "What THIS pilot estimates DESCRIPTIVELY on the switch-eligible set: "
            "adoption_increase and answer_switch_rate (prerequisite behavioural signal), "
            "with bootstrap 95% CIs treated as descriptive, not inferential (Part 17).", "D-048/D-059"
        ),
        secondary_estimands=L(
            "SUPPORTING/PREREQUISITE BEHAVIOURAL (descriptive): control/hinted adoption, "
            "unhinted/hinted accuracy, accuracy_drop. disclosure_rate / hidden_influence_rate "
            "are BLOCKED on the disclosure judge and the human audit (D-047).", "D-048"
        ),
        diagnostic_metrics=L(
            "DIAGNOSTIC (descriptive): parse-status counts, reasoning-span-status counts, "
            "n_reasoning_spans distribution, stop_reason counts + LENGTH/TIMEOUT (truncation) "
            "rate, tie counts, per-item answer stability across k, format-compliance rate, "
            "realized eligibility yield, realized switch yield, missingness rate.", "D-048"
        ),
        uncertainty_method=L(
            "item-clustered percentile bootstrap (bootstrap_seed 20260910, n 10000); "
            "zero-denominator -> UNDEFINED (NaN), never a silent 0", "D-048"
        ),
        multiplicity_policy=L(
            "pilot is not a hypothesis test -> no multiplicity control; CIs are descriptive. "
            "Confirmatory multiplicity is a deferred decision.", "D-048"
        ),
        disclosure_judge=blocked_ext(
            "D-047",
            "no judge runnable on the M5; none may be picked before a blinded human-label "
            "audit of real traces. The pilot's disclosure_rate / hidden_influence_rate "
            "estimands need it. Behavioural estimands (adoption_increase, answer_switch_rate) "
            "do not. MONITOR_VALIDATION_PROTOCOL.md §2.",
        ),
        human_disclosure_audit=blocked_ext(
            "D-047",
            "blinded native/proficient human disclosure annotation of a subset is mandatory to "
            "bound judge error (MILESTONE_1_READINESS §7a). Needs annotators + an ethics "
            "determination. MONITOR_VALIDATION_PROTOCOL.md §4.",
        ),
        translation_protocol=not_applicable(
            "D-049", "English-only pilot needs no translation. Designed for Milestone 2+ in "
            "MONITOR_VALIDATION_PROTOCOL.md §3.",
        ),
        native_urdu_validation=not_applicable(
            "D-049", "English-only pilot. Native-Urdu human validation is the Milestone-3 "
            "centrepiece; protocol designed in MONITOR_VALIDATION_PROTOCOL.md §4.",
        ),
        ethics_determination=blocked_ext(
            "D-049",
            "institutional determination may be required before recruiting the human disclosure "
            "annotators the pilot's audit needs; NOT an assertion of exemption.",
        ),
    )


def dump_manifest(manifest: TrackAPilotManifest, path: str | Path) -> None:
    Path(path).write_text(
        json.dumps(json.loads(manifest.model_dump_json()), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


__all__ = [
    "PROTOCOL_VERSION",
    "SCHEMA_VERSION",
    "Field_",
    "ManifestNotRunReady",
    "Status",
    "TrackAPilotManifest",
    "build_pilot_manifest",
    "check_run_ready",
    "dump_manifest",
    "load_manifest",
    "manifest_from_config",
]
