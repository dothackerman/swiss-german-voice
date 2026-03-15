from __future__ import annotations

import os
import time

from swiss_german_voice.adapters.telegram.api import TelegramBotApi
from swiss_german_voice.adapters.telegram.handler import TelegramVoiceHandler
from swiss_german_voice.core.lexicon import PersonalLexicon
from swiss_german_voice.core.persistence import SQLiteTranscriptionStore
from swiss_german_voice.core.service import CoreRuntime
from swiss_german_voice.core.transcription import FasterWhisperTranscriber, WhisperConfig


def run_polling_loop() -> None:
    token = _required_env("TELEGRAM_BOT_TOKEN")
    media_dir = os.getenv("LOCAL_MEDIA_DIR", "var/media")
    db_path = os.getenv("SQLITE_DB_PATH", "var/swiss_german_voice.sqlite3")
    model_size = os.getenv("WHISPER_MODEL_SIZE", "small")
    language = os.getenv("WHISPER_LANGUAGE", "de")
    lexicon_words = [part.strip() for part in os.getenv("PERSONAL_LEXICON_WORDS", "").split(",") if part.strip()]

    api = TelegramBotApi(token=token)
    runtime = CoreRuntime(
        transcriber=FasterWhisperTranscriber(config=WhisperConfig(model_size=model_size, language=language)),
        store=SQLiteTranscriptionStore(db_path=db_path),
        lexicon=PersonalLexicon(words=lexicon_words),
    )
    handler = TelegramVoiceHandler(api=api, runtime=runtime, media_dir=media_dir)

    offset: int | None = None
    while True:
        updates = api.get_updates(offset=offset, timeout=25)
        for update in updates:
            update_id = update.get("update_id")
            if isinstance(update_id, int):
                offset = update_id + 1

            result = handler.try_handle_update(update)
            if result is not None:
                print(f"processed telegram voice message: {result}")
        time.sleep(1)


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"missing environment variable: {name}")
    return value


if __name__ == "__main__":
    run_polling_loop()
