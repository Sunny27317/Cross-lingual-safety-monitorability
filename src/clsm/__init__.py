"""clsm — Cross-Lingual Safety Monitorability.

Milestone 1 harness: an English-only reproduction of the Turpin (2023) / Chen (2025)
hidden-influence phenomenon on ``deepseek-ai/DeepSeek-R1-Distill-Qwen-7B``.

Scope of this package (Milestone 1 only):
    control  = MMLU multiple-choice question, no hint
    treatment = the same question + one frozen neutral "suggested wrong answer" hint
    measure  = answer-switch rate, disclosure rate, hidden-influence rate

**No experiment has been run. No model or dataset has been downloaded.**
The generation and disclosure-judge paths are blocked until explicitly authorized
(see ``clsm.generation`` and ``clsm.disclosure``).

Multilingual logic is deliberately absent — only interfaces that keep later
extension clean are present. The scientific specification lives in
``experiments/MILESTONE_1_READINESS.md`` and ``literature/DECISION_LOG.md``.
"""

from __future__ import annotations

__version__ = "0.0.0"

__all__ = ["__version__"]
