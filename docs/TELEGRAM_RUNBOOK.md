# Telegram Adapter Runbook (Phase C)

## Purpose

Run a minimal local/dev Telegram voice flow against the channel-agnostic core.

## Quick setup

1. Copy `.env.example` to `.env`.
2. Set `TELEGRAM_BOT_TOKEN` from BotFather.
3. Install dependencies:
   - `python3 -m pip install -e .`
4. Ensure local runtime dependencies exist:
   - `ffmpeg`
   - CUDA drivers if GPU path is expected

## First Telegram test (OG fast path)

1. Start the bot locally:
   - `scripts/run_telegram_dev.sh`
2. Open Telegram and send a short voice message to your bot.
3. Expected result:
   - bot replies with transcript line + confidence proxy line
   - transcription row appears in SQLite at `SQLITE_DB_PATH`
4. Inspect persistence quickly:
   - `sqlite3 var/swiss_german_voice.sqlite3 'select id, conversation_ref, transcript_text from transcriptions order by id desc limit 5;'`

## Common failures

- `missing environment variable: TELEGRAM_BOT_TOKEN`
  - `.env` not loaded or token unset.
- `faster-whisper is not installed`
  - run `python3 -m pip install -e .`.
- `unable to initialize faster-whisper model`
  - CUDA unavailable and CPU fallback failed; verify `ctranslate2` dependencies.
- No bot replies
  - ensure bot privacy settings and that `getUpdates` is allowed (no conflicting webhook).

## Adapter contract notes

- Telegram payload shapes stay in adapter modules only.
- Core sees only normalized request envelope.
- Confidence summary uses segment proxies (`avg_logprob`, `no_speech_prob`) when available.
