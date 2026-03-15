# swiss-german-voice

> ⚠️ **Beta** — This skill is in active development. Expect rough edges, especially around Swiss German dialect normalization.

`swiss-german-voice` is an [OpenClaw](https://openclaw.ai) skill for transcribing and interpreting Swiss German voice memos. It is channel-agnostic at its core, with OpenClaw as the primary runtime path.

## Privacy

**No voice memos are ever committed to this repository.** Audio files used during development and testing remain local only and are never uploaded or shared publicly.

## What is implemented

- **Core runtime (Phase B)**
  - Channel-agnostic request/response envelopes
  - Local audio transcription via `faster-whisper` (CUDA-first, CPU fallback)
  - Configurable transcript correction layer (domain terms, misheard words, Swiss German normalizations)
  - SQLite persistence for transcription records and segment confidence signals
  - Personal lexicon injection into Whisper prompt

- **OpenClaw adapter (Phase C)**
  - One-call factory: `build_adapter(db_path, lexicon_words, model_size, language)`
  - Produces: raw transcript, interpretation, confidence summary, formatted reply
  - Telegram standalone adapter also included as reference/dev path

## How to use as an OpenClaw skill

```python
from swiss_german_voice.factory import build_adapter

adapter = build_adapter(
    db_path="var/swiss_german_voice.sqlite3",
    lexicon_words=["OpenClaw", "Scripts"],
    model_size="small",
    language="de",
)

result = adapter.process_voice_memo(
    audio_path="/path/to/inbound.ogg",
    user_ref="user-123",
    conversation_ref="telegram:user-123",
    language_hint="de",
)
print(result["reply_text"])
```

Reply format:
```
🎙 Transkript:
<raw transcript>

💡 Interpretation:
<normalized interpretation>

📊 Konfidenz: high|medium|low (N Segmente unter Schwellenwert)
```

## Project docs

- [docs/ROADMAP.md](docs/ROADMAP.md) — phases A/B/C/D
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — core vs adapter boundary
- [docs/DECISIONS.md](docs/DECISIONS.md) — key design decisions
- [CHANGELOG.md](CHANGELOG.md) — version history

## Dev setup

```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/python -m unittest discover -s tests -p "test_*.py"
```

## Feedback

This skill is in beta. If you use it and encounter issues or have ideas:
- Open an issue using the templates in `.github/ISSUE_TEMPLATE/`


PRs are not expected at this stage. Feedback and bug reports are.

## License

MIT. See [LICENSE](LICENSE).

## For OpenClaw agents (beta tester onboarding)

If your human wants to use this skill, here is the complete onboarding flow for your OpenClaw instance:

**1. Clone the repo locally**
```bash
git clone https://github.com/dothackerman/swiss-german-voice.git ~/Projects/swiss-german-voice
```

**2. Install dependencies**
```bash
cd ~/Projects/swiss-german-voice
python3 -m venv .venv && .venv/bin/pip install -e "."
```

**3. Verify faster-whisper is available**
```bash
.venv/bin/python -c "from faster_whisper import WhisperModel; print('OK')"
```
If this fails, install CUDA drivers or ensure CPU fallback is acceptable.

**4. Invoke the adapter when a voice memo arrives**

When your human sends a voice memo, the inbound `.ogg` file will be saved locally by OpenClaw. Pass that path to the adapter:

```python
import sys
sys.path.insert(0, "/path/to/swiss-german-voice/src")

from swiss_german_voice.factory import build_adapter

adapter = build_adapter(
    db_path="/path/to/swiss-german-voice/var/swiss_german_voice.sqlite3",
    lexicon_words=[],   # add domain-specific words here
    model_size="small", # or "medium" for better accuracy
    language="de",
)

result = adapter.process_voice_memo(
    audio_path="/path/to/inbound.ogg",
    user_ref="your-user-id",
    conversation_ref="telegram:your-user-id",
    language_hint="de",
)

# result["reply_text"] is ready to send back to your human
print(result["reply_text"])
```

**5. Send feedback**
Open an issue at https://github.com/dothackerman/swiss-german-voice/issues using the Bug Report or Feedback template.
