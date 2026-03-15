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

## Review round 1

- Scope: addressed 6 Copilot inline comments on PR #1 and re-reviewed branch diff against `main`.
- Persistence hardening:
  - added `PersistenceError` in `core/persistence.py`
  - enforce non-empty `audio_path` coercion to `str` before SQLite write
  - validate metadata is JSON-serializable and fail with structured error message
- Adapter resilience and security:
  - `TelegramVoiceHandler.try_handle_update()` now catches `TelegramApiError` and unexpected exceptions, logs, and continues loop execution
  - `_download_voice_file()` now uses UUID-based filenames to avoid untrusted identifier path injection
- Core normalization compatibility:
  - extended allowed audio extensions to include `.oga` for Telegram voice payload compatibility
- Test stability and coverage:
  - replaced fixed `/tmp` persistence test path with per-test `TemporaryDirectory()`
  - added regression tests for:
    - missing `audio_path` persistence rejection
    - non-serializable metadata rejection
    - `.oga` acceptance
    - transport/unexpected exception handling in `try_handle_update`
    - download destination safety against untrusted message/chat identifiers
- CE review feedback (branch vs `main`):
  - no new critical architecture issues found; current separation (core vs Telegram adapter) remains clean
  - key tradeoff: broad exception catch in polling path improves uptime but can hide recurring defects if logs are not monitored
  - next hardening step: add lightweight error counters/metrics in polling loop to detect repeated transient failures early

## OpenClaw adapter

- Added `src/swiss_german_voice/adapters/openclaw/adapter.py` as an OpenClaw-native ingress path for local inbound media files.
- Input contract:
  - local audio path from OpenClaw media persistence
  - `user_ref`, `conversation_ref`, and optional `language_hint` (default `de`)
- Adapter behavior:
  - normalizes into the existing core request envelope (`source_adapter=openclaw`)
  - calls `CoreRuntime`
  - returns structured output (`transcript`, `interpretation`, `confidence_summary`, `reply_text`) for direct OpenClaw message dispatch
- Constraint kept: legacy Telegram polling adapter stays in place for reference and separate bot-flow usage.
