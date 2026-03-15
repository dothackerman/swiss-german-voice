---
title: feat: Pre-release improvements for v1.0
type: feat
status: active
date: 2026-03-15
origin: docs/brainstorms/2026-03-15-pre-release-v1-brainstorm.md
---

# feat: Pre-release improvements for v1.0

## Overview

Implement five pre-release improvements requested by OG across runtime quality, docs accuracy, and GitHub project hygiene.

## Scope

- [x] Add configurable lexicon correction layer for OpenClaw transcript interpretation.
- [x] Add `build_adapter(db_path, lexicon_words, model_size, language)` factory entrypoint.
- [x] Update skill docs and references to current OpenClaw-centric invocation.
- [x] Add GitHub issue templates for bug reports and feedback.
- [x] Add changelog and release workflow stub.
- [x] Capture significant decisions in `docs/DECISIONS.md`.

## Implementation Notes

- Use JSON lexicon replacement config to avoid new dependencies.
- Keep OpenClaw adapter surface stable (`process_voice_memo`).
- Add tests for correction and factory wiring.

## Validation

- Run unit tests: `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`
- Verify docs reference real modules and callable signatures.

## Risks

- Lexicon replacements can over-correct if patterns are too broad.
- Release workflow is a stub; artifacts beyond changelog are out of scope.
