"""Validate tokenizer accounting and no-loss segmentation after setup.

This command loads only the pinned tokenizer, never the translation model, and
accepts synthetic text only. It is intentionally not run during Falcon judging.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from clsm.workshop_v1.translation import indictrans_source_token_count, segment_source_chunks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tokenizer_dir", type=Path)
    args = parser.parse_args()
    from transformers import AutoTokenizer  # type: ignore[import-not-found]

    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer_dir, trust_remote_code=True)
    synthetic = "یہ ایک مصنوعی جملہ ہے۔\nیہ دوسرا مصنوعی جملہ ہے؛ اور یہ صرف جانچ کے لیے ہے۔"  # noqa: RUF001
    def token_count(value: str) -> int:
        return indictrans_source_token_count(tokenizer, value)
    chunks = segment_source_chunks(synthetic, token_count=token_count, max_source_tokens=200)
    if "".join(chunk.text for chunk in chunks).replace(" ", "") != synthetic.replace(" ", ""):
        raise SystemExit("FAIL: synthetic segmentation changed content/order")
    counts = [indictrans_source_token_count(tokenizer, chunk.text) for chunk in chunks]
    if any(count > 200 for count in counts):
        raise SystemExit("FAIL: tokenizer accounting exceeded 200 source tokens")
    print({"status": "PASS", "synthetic_chunks": len(chunks), "token_counts": counts, "model_loaded": False})


if __name__ == "__main__":
    main()
