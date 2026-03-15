from __future__ import annotations

from swiss_german_voice.adapters.openclaw.adapter import OpenClawVoiceAdapter
from swiss_german_voice.core.lexicon import PersonalLexicon
from swiss_german_voice.core.persistence import SQLiteTranscriptionStore
from swiss_german_voice.core.service import CoreRuntime
from swiss_german_voice.core.transcription import FasterWhisperTranscriber, WhisperConfig


def build_adapter(
    db_path: str,
    lexicon_words: list[str] | None,
    model_size: str,
    language: str,
) -> OpenClawVoiceAdapter:
    transcriber = FasterWhisperTranscriber(config=WhisperConfig(model_size=model_size, language=language))
    store = SQLiteTranscriptionStore(db_path=db_path)
    lexicon = PersonalLexicon.from_config({"words": lexicon_words or []})
    runtime = CoreRuntime(transcriber=transcriber, store=store, lexicon=lexicon)
    return OpenClawVoiceAdapter(runtime=runtime)
