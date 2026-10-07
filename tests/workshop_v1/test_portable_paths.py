from clsm.workshop_v1.local_runtime import portable_path


def test_legacy_model_path_uses_portable_root(monkeypatch) -> None:
    monkeypatch.setenv("CLSM_MODEL_ROOT", "/tmp/models")
    assert portable_path("/Users/sullah1/models/clsm/Qwen/x.gguf") == "/tmp/models/Qwen/x.gguf"


def test_legacy_llama_path_uses_portable_root(monkeypatch) -> None:
    monkeypatch.setenv("CLSM_LLAMA_CPP_ROOT", "/tmp/llama")
    assert portable_path("/Users/sullah1/tools/llama.cpp/build/bin/llama-cli") == (
        "/tmp/llama/build/bin/llama-cli"
    )


def test_path_is_unchanged_without_override(monkeypatch) -> None:
    monkeypatch.delenv("CLSM_MODEL_ROOT", raising=False)
    monkeypatch.delenv("CLSM_LLAMA_CPP_ROOT", raising=False)
    assert portable_path("/Users/sullah1/models/clsm/Qwen/x.gguf") == "/Users/sullah1/models/clsm/Qwen/x.gguf"
