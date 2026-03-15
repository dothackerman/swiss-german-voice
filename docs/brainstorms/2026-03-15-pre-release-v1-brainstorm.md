---
date: 2026-03-15
topic: pre-release-v1-improvements
---

# Pre-Release v1 Improvements Brainstorm

## What We're Building

We are preparing `swiss-german-voice` for a v1.0 public release by addressing five concrete gaps: transcript correction quality, docs drift, one-call adapter construction, external issue intake, and release process scaffolding.

## Why This Approach

Approach A (recommended): targeted hardening only. Ship minimal, composable improvements aligned to current architecture without refactoring unrelated runtime concerns.

Approach B: broader architecture cleanup before v1.0. This would likely delay release and increase regression risk outside the requested scope.

Chosen: Approach A, because requirements are explicit and constrained.

## Key Decisions

- Add a configurable correction layer in OpenClaw adapter instead of expanding regex logic.
- Add a factory function for one-call OpenClaw pipeline construction.
- Treat OpenClaw as primary runtime path in skill docs; Telegram remains reference/test adapter.
- Add public-facing issue templates focused on user reports and dialect context.
- Add a minimal tag-triggered release workflow stub.

## Constraints

- No behavioral regressions in adapter request mapping and confidence summary output.
- Lexicon extensibility must work without code changes.
- Keep release automation intentionally simple for initial public launch.

## Failure Modes

- Over-aggressive replacement rules could mutate valid transcripts.
- Docs could still drift if invocation examples are not validated against actual APIs.
- Release workflow may be too thin for future binary/artifact needs.

## Next Step

Proceed to implementation planning in `docs/plans/2026-03-15-001-pre-release-improvements-plan.md`.
