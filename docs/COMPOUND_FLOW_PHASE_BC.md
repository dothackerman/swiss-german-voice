# Compound Flow Log: Phases B + C

## Brainstorm

- Strong version: keep core contract stable and channel-agnostic while proving one full Telegram path.
- Critique: easiest failure is Telegram-specific fields leaking into core request and persistence.
- Constraint: keep implementation minimal and locally testable, no deployment scaffolding.
- Failure mode considered: confidence metrics absent for some segments; handled as `n/a` summary fields.

## Plan

1. Phase B:
   - define normalized envelopes and validation
   - implement faster-whisper local audio service (CUDA-first, CPU fallback)
   - persist transcription results and segment uncertainty signals in SQLite
   - add tests for normalization and persistence
2. Phase C:
   - add Telegram adapter intake + Bot API media download
   - map adapter event to core request envelope
   - render transcript + confidence summary reply
   - add adapter tests + Telegram runbook + local run script/env example

## Work

- Implemented core modules under `src/swiss_german_voice/core`.
- Implemented Telegram adapter under `src/swiss_german_voice/adapters/telegram`.
- Added tests in `tests/core` and `tests/adapters`.
- Added `.env.example`, `scripts/run_telegram_dev.sh`, and `docs/TELEGRAM_RUNBOOK.md`.

## Review

- Boundary check: core imports no Telegram modules.
- Scope check: no extra channels or deployment automation added.
- End-to-end local path exists: Telegram update -> media download -> core runtime -> reply + SQLite persistence.
