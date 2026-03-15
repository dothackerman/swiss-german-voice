# Changelog

All notable changes to `swiss-german-voice` will be documented in this file.

## v0.0.1-rc1 - 2026-03-15

### Added

- Core runtime envelope for channel-agnostic voice processing.
- Local `faster-whisper` transcription pipeline with CUDA-first and CPU fallback behavior.
- SQLite transcription persistence with uncertainty signal storage.
- Personal lexicon prompt injection for transcription hints.
- Telegram adapter for normalized voice intake, media download, and reply dispatch.
- OpenClaw adapter for local media-path processing and structured reply rendering.
- Initial project documentation, runbook, and contribution guide.
