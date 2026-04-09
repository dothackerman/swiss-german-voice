---
name: swiss-german-voice
description: Transcribe and interpret Swiss German voice memos sent via OpenClaw. Use when a voice memo (.ogg/.m4a) arrives and the user communicates in Swiss German or German. Runs faster-whisper locally (CUDA-first, CPU fallback), returns raw transcript + interpretation + confidence summary.
metadata: {"openclaw": {"requires": {"bins": ["python3"]}}}
---

# swiss-german-voice

Transcribe and interpret a Swiss German voice memo.

## Trigger

When an inbound voice memo arrives and the user communicates in Swiss German or German.

## Invocation

```python
import sys
sys.path.insert(0, "/path/to/swiss-german-voice/src")

from swiss_german_voice.factory import build_adapter

adapter = build_adapter(
    db_path="/path/to/swiss-german-voice/var/swiss_german_voice.sqlite3",
    lexicon_words=[],  # personal terms auto-loaded from var/lexicon_personal.json
    model_size="large",
    language="de",
)

result = adapter.process_voice_memo(
    audio_path="<inbound media path from OpenClaw>",
    user_ref="<user id>",
    conversation_ref="<channel:user_id>",
    language_hint="de",
)

# Send result["reply_text"] back to the user
```

## Output format

```
🎙 Transkript:
<raw transcript>

💡 Interpretation:
<normalized interpretation>

📊 Konfidenz: high|medium|low (N Segmente unter Schwellenwert)

⚠️ Zur Überprüfung:
  [mm:ss–mm:ss] "<flagged segment text>"
    vorher:  "<previous segment>"
    nachher: "<next segment>"
```

## Notes

- Replace `/path/to/swiss-german-voice` with the actual clone location on your machine.
- `model_size="large"` recommended for long recordings and complex dialect; falls back to CPU if no CUDA.
- Personal lexicon auto-loaded from `var/lexicon_personal.json` (gitignored — stays local).
- Additional words can be passed via `lexicon_words` at invocation time.
- See `src/swiss_german_voice/data/lexicon_corrections.json` for correction rules.
- Full docs: `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`.
