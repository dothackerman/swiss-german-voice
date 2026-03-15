# Decisions

## 2026-03-15: Configurable transcript correction via JSON lexicon

- Decision: Replace regex-only interpretation logic in the OpenClaw adapter with `TranscriptCorrectionLayer`, loaded from configurable JSON rules.
- Why: OG requested extensibility without code changes and explicit support for domain and misheard term normalization.
- Tradeoff: JSON is strict and less ergonomic than YAML, but avoids adding a dependency and keeps runtime deterministic.

## 2026-03-15: Default correction rules shipped as package data

- Decision: Store default replacements in `src/swiss_german_voice/data/lexicon_corrections.json` and load with `importlib.resources`.
- Why: Provides a sane baseline while supporting overrides from custom files.
- Tradeoff: Runtime assumes packaged data is present; this is covered by setuptools package-data config.

## 2026-03-15: One-call OpenClaw factory entrypoint

- Decision: Add `build_adapter(db_path, lexicon_words, model_size, language)` in `src/swiss_german_voice/factory.py`.
- Why: the OpenClaw adapter can be instantiated without manually wiring core components.
- Tradeoff: Factory currently returns the OpenClaw adapter only; if more adapters need one-call factories, we will add explicit factory functions instead of a generic builder.

## 2026-03-15: Skill docs now treat OpenClaw as primary runtime path

- Decision: Update skill docs and references to center on OpenClaw + factory invocation, with Telegram kept as reference/testing path.
- Why: Current implementation and OG workflow use OpenClaw ingress as primary usage.
- Tradeoff: Telegram runbook still exists for development operations, but no longer framed as main integration.

## 2026-03-15: Public maintenance scaffolding before v1.0

- Decision: Add issue templates, `CHANGELOG.md`, and a release workflow triggered by version tags.
- Why: Pre-release governance and user reporting become explicit before public launch.
- Tradeoff: Release workflow is intentionally minimal (stub) and may need artifact upload expansion later.
