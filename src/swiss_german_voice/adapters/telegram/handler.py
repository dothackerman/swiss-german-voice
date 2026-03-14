from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from swiss_german_voice.adapters.telegram.api import TelegramBotApi
from swiss_german_voice.adapters.telegram.normalize import TelegramNormalizationError, normalize_telegram_voice_update
from swiss_german_voice.core.normalize import normalize_core_request
from swiss_german_voice.core.service import CoreRuntime


@dataclass(slots=True)
class TelegramVoiceHandler:
    api: TelegramBotApi
    runtime: CoreRuntime
    media_dir: str

    def handle_update(self, update: dict[str, Any]) -> dict[str, Any]:
        event = normalize_telegram_voice_update(update)
        file_path = self.api.get_file_path(event.file_id)
        local_audio_path = self._download_voice_file(file_path, event)

        core_request = normalize_core_request(
            {
                "source_adapter": "telegram",
                "conversation_ref": event.chat_id,
                "user_ref": event.user_id,
                "input_kind": "voice",
                "payload": {"audio_path": local_audio_path},
                "metadata": {"telegram_message_id": event.message_id, "telegram_file_path": file_path},
            }
        )

        core_response = self.runtime.handle(core_request)
        reply_text = render_telegram_reply(core_response.messages)
        self.api.send_message(event.chat_id, reply_text)

        return {
            "chat_id": event.chat_id,
            "message_id": event.message_id,
            "status": core_response.status.value,
            "record_id": core_response.artifacts.get("record_id"),
        }

    def try_handle_update(self, update: dict[str, Any]) -> dict[str, Any] | None:
        try:
            return self.handle_update(update)
        except TelegramNormalizationError:
            return None

    def _download_voice_file(self, file_path: str, event) -> str:
        suffix = Path(file_path).suffix or ".ogg"
        destination = Path(self.media_dir) / f"tg_{event.chat_id}_{event.message_id}{suffix}"
        return self.api.download_file(file_path, str(destination))


def render_telegram_reply(messages: list[str]) -> str:
    return "\n".join(message.strip() for message in messages if message and message.strip())
