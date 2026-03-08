# EPIC v1.0 — Epistemic Predictive Integrity Core

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: v1.0 Spec + Ref Impl](https://img.shields.io/badge/status-spec+%2B%20ref%20impl-blue)](https://github.com/PsychoFrogMultimedia/EPIC-truth-calibrated-architecture-)
[![Commits](https://img.shields.io/github/commit-activity/m/PsychoFrogMultimedia/EPIC-truth-calibrated-architecture-)](https://github.com/PsychoFrogMultimedia/EPIC-truth-calibrated-architecture-/commits/main)

A unified, model-agnostic architecture to enforce epistemic legibility in LLM outputs: distinguish grounded knowledge, inference, speculation, and unknowns **before** emission.

Integrates:
- Platonic 5+1 (processing spine)
- CFI (forecasting & steering)
- ARC (reality binding & continuity)

Addresses mathematical inevitability of hallucinations via upstream routing + disclosure + closed-loop calibration.

## Core Files
- `docs/EPIC-v10-Operational-Spec.json` — Complete runtime control spec
- `docs/EPIC-v10-Companion.md` — Runtime behavior guide
- `docs/EPIC-v1.0-Formalization.md` — Formalization
- `docs/EPIC-v1.0-Formal-Spec.md` —Formal Spec

## Status

- Conceptual + operational spec (v1.0)
- Reference implementation in `src/` — loads the JSON spec and executes the full 8-step runtime loop (Probe → Branch → Map → CFI → ARC → Resolve → Define → Maintain)
- Demo in `examples/run_epic.py` — run with `python examples/run_epic.py "your query"`
- Wrappers (e.g., LLM integration, real RAG anchors) coming soon
- Open for feedback, contributions, and evals!

## Contact: 

DM on X @D_McMillan76

## MIT License

## Built on ideas from 

https://github.com/PsychoFrogMultimedia/Contextual-Forecasting-Integrator


pip install anthropic sentence-transformers faiss-cpu
Anthropic API
