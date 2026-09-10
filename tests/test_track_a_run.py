"""Track-A run-authorization gate + scientific-config hash + provenance.

Adversarial tests for the fail-closed gate (DECISION_LOG D-050..D-055). No real model,
no real dataset, no scientific data.
"""

from __future__ import annotations

import json

import pytest
import yaml

from clsm.config import load_experiment_config
from clsm.track_a_run import (
    ENV_AUTH,
    RunNotAuthorizedError,
    RunToken,
    authorize_track_a_run,
    capture_track_a_provenance,
    evaluate_readiness,
    scientific_config_dict,
    scientific_config_hash,
)

CFG = "configs/track_a_pilot/pilot.yaml"
RT = "configs/track_a_pilot/runtime_llamacpp.yaml"

_ASSERTION = (
    "I have reviewed the Track-A pilot manifest and preregistration and authorize this "
    "exact scientific configuration to run."
)


def _runtime_dict() -> dict:
    return yaml.safe_load(open(RT))


def _valid_payload(scientific_hash: str) -> str:
    return json.dumps(
        {
            "scientific_hash": scientific_hash,
            "reviewer": "test-reviewer",
            "reviewed_utc": "2026-09-10T00:00:00+00:00",
            "assertion": _ASSERTION,
        }
    )


# ---- readiness gate: fail-closed (Part 2) ----------------------------------------


def test_readiness_fails_closed_with_no_env(monkeypatch) -> None:
    monkeypatch.delenv(ENV_AUTH, raising=False)
    rep = evaluate_readiness(config_path=CFG, runtime_path=RT)
    assert rep.methodology_frozen is True          # methodology IS frozen
    assert rep.external_resources_cleared is False  # dataset pin + judge + audit + ethics
    assert rep.human_authorization_present is False
    assert rep.all_pass is False


def test_authorize_raises_when_not_ready(monkeypatch) -> None:
    monkeypatch.delenv(ENV_AUTH, raising=False)
    with pytest.raises(RunNotAuthorizedError) as ei:
        authorize_track_a_run(config_path=CFG, runtime_path=RT)
    msg = str(ei.value)
    assert "external resources" in msg and "human authorization" in msg


def test_boolean_toggle_is_rejected(monkeypatch) -> None:
    """'authorized=true' style toggles must NOT work (explicit user constraint)."""
    for val in ("true", "1", "yes", "on"):
        monkeypatch.setenv(ENV_AUTH, val)
        rep = evaluate_readiness(config_path=CFG, runtime_path=RT)
        assert rep.human_authorization_present is False
        assert "boolean toggle" in (rep.human_authorization_error or "")


def test_human_auth_needs_matching_scientific_hash(monkeypatch) -> None:
    monkeypatch.setenv(ENV_AUTH, _valid_payload("0" * 64))  # wrong hash
    rep = evaluate_readiness(config_path=CFG, runtime_path=RT)
    assert rep.human_authorization_present is False
    assert "does not match" in (rep.human_authorization_error or "")


def test_human_auth_needs_verbatim_assertion(monkeypatch) -> None:
    cfg = load_experiment_config(CFG)
    h = scientific_config_hash(cfg, _runtime_dict())
    bad = json.loads(_valid_payload(h))
    bad["assertion"] = "yeah sure go ahead"
    monkeypatch.setenv(ENV_AUTH, json.dumps(bad))
    rep = evaluate_readiness(config_path=CFG, runtime_path=RT)
    assert rep.human_authorization_present is False
    assert "assertion" in (rep.human_authorization_error or "")


def test_human_auth_present_but_still_blocked_by_external_resources(monkeypatch) -> None:
    """Even a perfectly-formed human token does NOT authorize a run while the dataset
    content pin / judge / audit / ethics remain unresolved. Fail-closed."""
    cfg = load_experiment_config(CFG)
    h = scientific_config_hash(cfg, _runtime_dict())
    monkeypatch.setenv(ENV_AUTH, _valid_payload(h))
    rep = evaluate_readiness(config_path=CFG, runtime_path=RT)
    assert rep.human_authorization_present is True
    assert rep.all_pass is False  # external resources still block
    with pytest.raises(RunNotAuthorizedError):
        authorize_track_a_run(config_path=CFG, runtime_path=RT)


# ---- scientific-config hash (Part 6) --------------------------------------------


def test_scientific_hash_is_deterministic() -> None:
    cfg = load_experiment_config(CFG)
    rt = _runtime_dict()
    assert scientific_config_hash(cfg, rt) == scientific_config_hash(cfg, rt)


@pytest.mark.parametrize(
    "update",
    [
        {"temperature": 0.9},
        {"top_p": 0.8},
        {"top_k": 40},
        {"max_new_tokens": 999},
        {"samples_per_condition": 3, "seeds": [0, 1, 2]},
        {"force_think_prefix": True},
    ],
)
def test_scientific_hash_changes_on_decoding_change(update) -> None:
    from clsm.config import DecodingConfig

    cfg = load_experiment_config(CFG)
    rt = _runtime_dict()
    base = scientific_config_hash(cfg, rt)
    payload = {**cfg.decoding.model_dump(), **update}
    cfg2 = cfg.model_copy(update={"decoding": DecodingConfig.model_validate(payload)})
    assert scientific_config_hash(cfg2, rt) != base


def test_scientific_hash_changes_on_scientific_doc_params() -> None:
    """Cue version, prompt-template version, hint seed, dataset selection, bootstrap
    seed -- all in the hash (Part 6)."""
    cfg = load_experiment_config(CFG)
    rt = _runtime_dict()
    base = scientific_config_hash(cfg, rt)
    for upd in (
        {"hint_seed": 1},
        {"bootstrap_seed": 1},
        {"prompt_template_version": "vX"},
    ):
        assert scientific_config_hash(cfg.model_copy(update=upd), rt) != base
    cue2 = cfg.cue.model_copy(update={"version": "v2-different"})
    assert scientific_config_hash(cfg.model_copy(update={"cue": cue2}), rt) != base


def test_scientific_hash_changes_on_runtime_identity_change() -> None:
    cfg = load_experiment_config(CFG)
    rt = _runtime_dict()
    base = scientific_config_hash(cfg, rt)
    rt["runtime"]["commit"] = "deadbeef" * 5
    assert scientific_config_hash(cfg, rt) != base
    rt = _runtime_dict()
    rt["model"]["sha256"] = "0" * 64
    assert scientific_config_hash(cfg, rt) != base
    rt = _runtime_dict()
    rt["runtime"]["build_number"] = "99999"
    assert scientific_config_hash(cfg, rt) != base


def test_scientific_hash_changes_on_timeout_seconds() -> None:
    """D-065: timeout_seconds can flip a trace to TIMEOUT and change missingness, so it
    MUST be part of the scientific config hash."""
    cfg = load_experiment_config(CFG)
    rt = _runtime_dict()
    base = scientific_config_hash(cfg, rt)
    assert "timeout_seconds" in scientific_config_dict(cfg, rt)
    rt["process"]["timeout_seconds"] = rt["process"]["timeout_seconds"] + 123
    assert scientific_config_hash(cfg, rt) != base


def test_scientific_hash_records_frozen_empty_extra_args() -> None:
    """D-065: the llama-cli command surface is frozen. The hash carries an explicit
    (empty) extra-args marker so a future re-introduction would move it."""
    cfg = load_experiment_config(CFG)
    assert scientific_config_dict(cfg, _runtime_dict())["llama_cli_extra_args"] == []


def test_scientific_hash_ignores_prose_provenance_tag() -> None:
    cfg = load_experiment_config(CFG)
    rt = _runtime_dict()
    base = scientific_config_hash(cfg, rt)
    d = scientific_config_dict(cfg, rt)
    assert "provenance_tag" not in json.dumps(d)  # prose excluded
    # changing a comment-only YAML value that is not in the curated dict must not move it
    rt["runtime"]["build"] = "some other build recipe string"
    assert scientific_config_hash(cfg, rt) == base


# ---- provenance (Part 8) --------------------------------------------------------


def test_capture_provenance_has_the_track_a_fields() -> None:
    tok = RunToken.for_synthetic_test()
    prov = capture_track_a_provenance(tok, experiment_id="track-a-en-hint-pilot-test")
    d = prov.model_dump()
    for key in (
        "scientific_config_hash", "git_commit", "git_dirty", "model_revision",
        "gguf_sha256", "llama_cpp_commit", "temperature", "top_p", "top_k", "min_p",
        "n_ctx", "timeout_seconds", "llama_cli_extra_args", "reasoning_format",
        "enable_thinking", "prompt_template_sha256", "cue_version", "cue_template_sha256",
        "hint_seed", "dataset_repo", "dataset_revision", "dataset_content_hash",
        "dataset_item_ids", "parser_version", "retry_policy_version", "bootstrap_seed",
        "bootstrap_n", "host_platform", "run_started_utc",
    ):
        assert key in d, key
    assert d["retry_policy_version"] == "zero-retry/D-054"
    assert d["dataset_content_hash"] is None  # honestly unset until the pre-run pin step
    assert d["llama_cli_extra_args"] == []   # D-065: frozen command surface
    assert d["timeout_seconds"] == 900.0


def test_runtoken_cannot_be_constructed_directly() -> None:
    with pytest.raises(RunNotAuthorizedError, match="only be created"):
        RunToken(scientific_hash="x", reviewer="x", reviewed_utc="x", manifest_status={})


def test_runtoken_for_synthetic_test_is_flagged() -> None:
    tok = RunToken.for_synthetic_test()
    assert tok.for_synthetic_test_only is True and "SYNTHETIC" in tok.scientific_hash
