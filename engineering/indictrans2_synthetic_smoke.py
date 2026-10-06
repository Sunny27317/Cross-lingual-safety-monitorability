"""Prepared real-backend smoke test; never uses Workshop-v1 traces."""
# ruff: noqa: RUF001 -- Urdu punctuation is synthetic test input.

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from clsm.workshop_v1.translation import indictrans_source_token_count, segment_source_chunks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_dir", type=Path)
    args = parser.parse_args()
    if not args.artifact_dir.is_dir():
        raise SystemExit("artifact directory missing")
    # Model loading is deliberately explicit and this command accepts only
    # synthetic strings; it never reads Workshop-v1 generation records.
    from IndicTransToolkit import IndicProcessor
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer  # type: ignore[import-not-found]

    device = torch.device("cpu")
    dtype = torch.float32
    tokenizer = AutoTokenizer.from_pretrained(
        args.artifact_dir, trust_remote_code=True, local_files_only=True
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(
        args.artifact_dir, trust_remote_code=True, local_files_only=True, torch_dtype=dtype
    ).to(device)
    processor = IndicProcessor(inference=True)
    synthetic = [
        "یہ ایک مصنوعی جملہ ہے۔",
        "یہ پہلی سطر ہے۔\nیہ دوسری سطر ہے؛ اور یہ صرف جانچ ہے۔",
    ]
    chunks = []
    for text in synthetic:
        chunks.extend(segment_source_chunks(
            text,
            token_count=lambda value: indictrans_source_token_count(tokenizer, value),
            max_source_tokens=200,
        ))
    prepared = processor.preprocess_batch(
        [chunk.text for chunk in chunks], src_lang="urd_Arab", tgt_lang="eng_Latn", visualize=False
    )
    batch = tokenizer(prepared, padding="longest", truncation=False, return_tensors="pt").to(device)
    with torch.inference_mode():
        generated = model.generate(**batch, num_beams=5, max_length=256, num_return_sequences=1)
    decoded = tokenizer.batch_decode(generated, skip_special_tokens=True, clean_up_tokenization_spaces=True)
    translated = processor.postprocess_batch(decoded, lang="eng_Latn")
    if len(translated) != len(chunks) or any(not value.strip() for value in translated):
        raise SystemExit("FAIL: synthetic translation output was incomplete")
    print(json.dumps({
        "status": "SYNTHETIC_TRANSLATION_PASS", "synthetic_only": True,
        "device": str(device), "dtype": str(dtype), "chunks": len(chunks),
        "source_token_counts": [chunk.source_token_count for chunk in chunks],
        "output_count": len(translated),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
