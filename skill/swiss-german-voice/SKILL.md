# swiss-german-voice

Use this skill when handling Swiss German voice workflows for `swiss-german-voice`.

Primary OpenClaw usage pattern:

1. Build the full pipeline via `build_adapter(...)` from `swiss_german_voice.factory`.
2. OpenClaw provides a local media path; pass that path directly to the adapter.
3. Call `process_voice_memo(audio_path, user_ref=..., conversation_ref=..., language_hint="de")`.
4. Send `reply_text` through the OpenClaw message tool.

Factory invocation:

```python
from swiss_german_voice.factory import build_adapter

adapter = build_adapter(
    db_path="var/swiss_german_voice.sqlite3",
    lexicon_words=["OpenClaw", "Scripts"],
    model_size="small",
    language="de",
)
```

Notes:

- OpenClaw is the primary integration path for runtime usage.
- Telegram polling adapter remains a reference adapter and test harness, not the primary deployment interface.
- Keep adapters thin: normalize channel input to the shared core request envelope and keep channel transport details out of `src/swiss_german_voice/core/`.
