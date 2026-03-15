# swiss-german-voice

`swiss-german-voice` is a channel-agnostic Swiss German voice workflow with Telegram as the first adapter.

## What is implemented

- Phase B core runtime slice:
  - normalized request/response envelopes
  - local audio transcription service (`faster-whisper`, CUDA-first then CPU fallback)
  - SQLite persistence for transcription records
  - personal lexicon injection hook
- Phase C Telegram adapter:
  - Telegram voice intake normalization
  - media download via Bot API
  - mapping into core request envelope
  - transcript + confidence proxy replies

## Project docs

- [docs/ROADMAP.md](docs/ROADMAP.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/TELEGRAM_RUNBOOK.md](docs/TELEGRAM_RUNBOOK.md)
- [docs/COMPOUND_FLOW_PHASE_BC.md](docs/COMPOUND_FLOW_PHASE_BC.md)

## Quick local dev

1. Install dependencies:
   - `python3 -m pip install -e .`
2. Copy env:
   - `cp .env.example .env`
3. Fill `TELEGRAM_BOT_TOKEN` in `.env`.
4. Run Telegram polling adapter:
   - `scripts/run_telegram_dev.sh`

## Test

- `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`

## Design intent

The core does not import Telegram types. Adapters translate channel payloads into the shared core envelope and map core outcomes back to channel-native replies.

## License

MIT. See [LICENSE](LICENSE).
