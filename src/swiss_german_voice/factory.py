from __future__ import annotations

import json
from pathlib import Path

from swiss_german_voice.adapters.openclaw.adapter import OpenClawVoiceAdapter
from swiss_german_voice.core.lexicon import PersonalLexicon
from swiss_german_voice.core.persistence import SQLiteTranscriptionStore
from swiss_german_voice.core.service import CoreRuntime
from swiss_german_voice.core.transcription import FasterWhisperTranscriber, WhisperConfig

_PERSONAL_LEXICON_PATH = Path(__file__).parent.parent.parent.parent / "var" / "lexicon_personal.json"


def _load_personal_lexicon(extra_words: list[str] | None = None) -> PersonalLexicon:
    words: list[str] = []
    if _PERSONAL_LEXICON_PATH.exists():
        try:
            data = json.loads(_PERSONAL_LEXICON_PATH.read_text(encoding="utf-8"))
            words = [w for w in data.get("words", []) if isinstance(w, str) and w.strip()]
        except Exception:
            pass
    words.extend(extra_words or [])
    return PersonalLexicon.from_config({"words": words})


def build_adapter(
    db_path: str,
    lexicon_words: list[str] | None,
    model_size: str,
    language: str,
) -> OpenClawVoiceAdapter:
    transcriber = FasterWhisperTranscriber(config=WhisperConfig(model_size=model_size, language=language))
    store = SQLiteTranscriptionStore(db_path=db_path)
    lexicon = _load_personal_lexicon(extra_words=lexicon_words)
    runtime = CoreRuntime(transcriber=transcriber, store=store, lexicon=lexicon)
    return OpenClawVoiceAdapter(runtime=runtime)
