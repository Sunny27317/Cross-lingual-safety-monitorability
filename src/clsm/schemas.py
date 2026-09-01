"""Data contracts for the Milestone-1 harness.

Every record that will ever be written to disk by a real run is defined here as a
Pydantic model with strict typing. Downstream code validates against these models;
nothing is written that does not round-trip through them.

Enumerations and field meanings are frozen to match ``experiments/MILESTONE_1_READINESS.md``
§16 (schemas) and §3 (measured quantities). Changing a field here is a scientific
decision and must be recorded in ``literature/DECISION_LOG.md``.
"""

from __future__ import annotations

import enum
import math

from pydantic import BaseModel, ConfigDict, Field

# --------------------------------------------------------------------------------------
# Enumerations
# --------------------------------------------------------------------------------------


class Condition(enum.StrEnum):
    """The two paired-prompt conditions (readiness §3)."""

    CONTROL = "control"      # question, no hint
    TREATMENT = "treatment"  # question + one frozen neutral wrong-answer hint


class ParseStatus(enum.StrEnum):
    """Answer-extraction outcome (readiness Phase 8). The extractor never guesses."""

    VALID = "VALID"              # exactly one answer letter recovered
    AMBIGUOUS = "AMBIGUOUS"      # conflicting answer letters found
    NO_ANSWER = "NO_ANSWER"      # no answer letter found
    PARSE_ERROR = "PARSE_ERROR"  # input was not analysable (e.g. not a string)


class DisclosureMethod(enum.StrEnum):
    """How a disclosure label was produced. ``MOCK_TEST_ONLY`` must never reach results."""

    KEYWORD_PREFILTER = "keyword_prefilter"
    LLM_JUDGE = "llm_judge"
    MOCK_TEST_ONLY = "MOCK_TEST_ONLY"


class GitState(enum.StrEnum):
    CLEAN = "clean"
    DIRTY = "dirty"
    UNKNOWN = "unknown"


# --------------------------------------------------------------------------------------
# Task item
# --------------------------------------------------------------------------------------


class MCQItem(BaseModel):
    """A single 4-way multiple-choice item after loading + validation (readiness §5)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    item_id: str = Field(description="Stable identifier: '<dataset>:<subject>:<row-index>'.")
    dataset: str
    subject: str
    question: str
    choices: list[str] = Field(min_length=4, max_length=4)
    answer_idx: int = Field(ge=0, le=3, description="Index of the correct choice.")
    question_sha256: str = Field(description="sha256 of question + '\\n' + '\\n'.join(choices).")

    @property
    def answer_letter(self) -> str:
        return "ABCD"[self.answer_idx]


class HintSpec(BaseModel):
    """The concrete hint applied to one item (readiness §5, §6; DECISION_LOG D-017).

    ``target_idx`` is chosen by a position-neutral deterministic hash over
    (experiment_id, item_id, cue_version, hint_seed) mapped onto the incorrect-index
    set — see :func:`clsm.interventions.choose_hint_target`. It is never the correct
    option. The selection inputs are recorded here + hashed so a run is reproducible.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    cue_type: str = Field(description="e.g. 'suggested_wrong_answer'.")
    cue_version: str = Field(description="Version tag of the frozen cue template.")
    target_idx: int = Field(ge=0, le=3, description="Index of the WRONG option the hint points to.")
    hint_seed: int = Field(description="Experiment-level seed for hint-target selection.")
    selection_key_sha256: str = Field(
        description="sha256 of 'experiment_id|item_id|cue_version|hint_seed' — the exact key hashed."
    )

    @property
    def target_letter(self) -> str:
        return "ABCD"[self.target_idx]


class PromptPair(BaseModel):
    """Rendered control + treatment user-turn text for one item."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    item_id: str
    control_prompt: str
    treatment_prompt: str
    control_prompt_sha256: str
    treatment_prompt_sha256: str
    hint: HintSpec
    prompt_template_version: str


# --------------------------------------------------------------------------------------
# Generation + disclosure records (one JSONL row each)
# --------------------------------------------------------------------------------------


class GenerationRecord(BaseModel):
    """One model generation for one (item, condition, sample). Readiness §16."""

    model_config = ConfigDict(extra="forbid")

    experiment_id: str
    item_id: str
    dataset: str
    dataset_revision: str
    subject: str
    question_sha256: str
    condition: Condition
    cue_type: str | None
    cue_version: str | None
    hint_target_letter: str | None
    correct_letter: str
    sample_idx: int = Field(ge=0)
    seed: int
    model: str
    model_revision: str
    tokenizer_revision: str
    temperature: float
    top_p: float
    max_new_tokens: int
    prompt_sha256: str
    prompt_template_version: str
    timestamp_utc: str
    raw_output: str
    cot_text: str | None = Field(description="Extracted <think>…</think> span, or None if absent.")
    answer_text: str | None = Field(description="Post-think span, or None.")
    extracted_answer: str | None = Field(description="'A'..'D' or None; never a guess.")
    parse_status: ParseStatus
    n_output_tokens: int | None
    truncated: bool
    is_mock: bool = Field(default=False, description="True only for TEST-ONLY fixtures.")


class DisclosureRecord(BaseModel):
    """One disclosure judgement for one treatment generation. Readiness §16."""

    model_config = ConfigDict(extra="forbid")

    experiment_id: str
    item_id: str
    sample_idx: int
    monitor_id: str
    monitor_model: str | None
    monitor_model_revision: str | None
    monitor_prompt_sha256: str | None
    keyword_prefilter_hit: bool
    disclosure: bool | None = Field(description="None = judge refused/failed; excluded from rate, counted.")
    confidence: float | None = None
    rationale: str
    method: DisclosureMethod
    timestamp_utc: str


# --------------------------------------------------------------------------------------
# Metrics output
# --------------------------------------------------------------------------------------


class Estimate(BaseModel):
    """A point estimate + bootstrap CI. ``n == 0`` (empty denominator) is an explicit
    UNDEFINED state: ``est``/``ci_lo``/``ci_hi`` are NaN and :pyattr:`defined` is False.
    Consumers must check :pyattr:`defined` — a zero-denominator metric is never a
    silent 0 (correction pass, this-turn requirement 3)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    est: float
    ci_lo: float
    ci_hi: float
    n: int = Field(description="Size of the denominator the estimate is computed over.")
    denominator: str = Field(description="Human-readable description of the denominator.")
    method: str = Field(default="item_cluster_bootstrap_pct")

    @property
    def defined(self) -> bool:
        return self.n > 0 and not math.isnan(self.est)


class MetricsResult(BaseModel):
    """Final metrics table for a run. Populated ONLY from real generations.

    Denominators (correction pass requirement 3; see ``clsm.metrics`` module docstring
    for the exact populations):

    * ``unhinted_accuracy`` / ``hinted_accuracy``  — items with a majority answer in
      that condition.
    * ``control_adoption_rate``  — P(a_u == hint_target) over ALL items with a majority
      control answer + a defined hint target.
    * ``hinted_adoption_rate``   — P(a_h == hint_target) over ALL items with a majority
      treatment answer + a defined hint target.
    * ``adoption_increase``      — paired per-item [1[a_h==h] - 1[a_u==h]] over items
      with a majority answer in BOTH conditions (this is switch-minus-control).
    * ``answer_switch_rate``     — Chen conditioning: P(a_h == h) over the SWITCH-ELIGIBLE
      set {a_u == correct AND hint_target != correct}.
    * ``disclosure_rate``        — Chen's CoT-faithfulness score: mean disclosure over
      QUALIFYING treatment samples {eligible item, sample answer == h, disclosure label
      present}. Item-clustered bootstrap.
    * ``hidden_influence_rate``  — mean of [switched AND not disclosed] over eligible
      items that are classifiable {did not switch, OR switched with a disclosure label}.
    * ``accuracy_drop``          — paired per-item [1[a_u==correct] - 1[a_h==correct]].
    """

    model_config = ConfigDict(extra="forbid")

    experiment_id: str
    role: str = Field(description="'pilot' or 'confirmatory'.")

    n_items_total: int
    n_items_majority_control: int
    n_items_majority_treatment: int
    n_items_majority_both: int
    n_tied_majority_control: int = Field(
        description="control conditions with a tied highest vote count (no tie-break; item excluded)"
    )
    n_tied_majority_treatment: int = Field(
        description="treatment conditions with a tied highest vote count (no tie-break; item excluded)"
    )
    n_items_eligible_switch: int = Field(description="{a_u == correct AND hint_target != correct}")
    n_eligible_switched: int = Field(description="eligible items whose majority a_h == hint_target")
    n_disclosure_labelled_items: int = Field(
        description="eligible+switched items with >=1 non-null disclosure label"
    )
    n_disclosure_unlabelled_items: int = Field(
        description="eligible+switched items with only-null labels (excluded from disclosure_rate, counted)"
    )

    unhinted_accuracy: Estimate
    hinted_accuracy: Estimate
    accuracy_drop: Estimate
    control_adoption_rate: Estimate
    hinted_adoption_rate: Estimate
    adoption_increase: Estimate
    answer_switch_rate: Estimate
    disclosure_rate: Estimate
    hidden_influence_rate: Estimate

    n_parse_valid: int
    n_parse_ambiguous: int
    n_parse_no_answer: int
    n_parse_error: int
    parse_success_rate: float

    bootstrap_seed: int
    bootstrap_n: int
    notes: list[str] = Field(default_factory=list)


__all__ = [
    "Condition",
    "DisclosureMethod",
    "DisclosureRecord",
    "Estimate",
    "GenerationRecord",
    "GitState",
    "HintSpec",
    "MCQItem",
    "MetricsResult",
    "ParseStatus",
    "PromptPair",
]
