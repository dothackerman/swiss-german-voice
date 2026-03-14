from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class TelegramNormalizationError(ValueError):
    """Raised when a Telegram update cannot be normalized."""


@dataclass(slots=True)
class TelegramVoiceEvent:
    chat_id: str
    user_id: str
    message_id: str
    file_id: str


def normalize_telegram_voice_update(update: dict[str, Any]) -> TelegramVoiceEvent:
    message = update.get("message")
    if not isinstance(message, dict):
        raise TelegramNormalizationError("update.message is required")

    voice = message.get("voice")
    if not isinstance(voice, dict):
        raise TelegramNormalizationError("message.voice is required")

    chat = message.get("chat")
    from_user = message.get("from")
    if not isinstance(chat, dict) or not isinstance(from_user, dict):
        raise TelegramNormalizationError("message.chat and message.from are required")

    chat_id = chat.get("id")
    user_id = from_user.get("id")
    message_id = message.get("message_id")
    file_id = voice.get("file_id")
    if None in (chat_id, user_id, message_id, file_id):
        raise TelegramNormalizationError("voice update missing chat/user/message/file identifiers")

    return TelegramVoiceEvent(
        chat_id=str(chat_id),
        user_id=str(user_id),
        message_id=str(message_id),
        file_id=str(file_id),
    )
