from __future__ import annotations

from pathlib import Path
from typing import Any

from swiss_german_voice.core.envelopes import CoreRequest, InputKind

_ALLOWED_AUDIO_EXTENSIONS = {".m4a", ".ogg", ".webm", ".wav"}


class NormalizationError(ValueError):
    """Raised when the request envelope is invalid."""


def normalize_core_request(raw: dict[str, Any]) -> CoreRequest:
    required = ["source_adapter", "conversation_ref", "user_ref", "payload"]
    missing = [key for key in required if not raw.get(key)]
    if missing:
        raise NormalizationError(f"missing required fields: {', '.join(missing)}")

    payload = raw["payload"]
    if not isinstance(payload, dict):
        raise NormalizationError("payload must be an object")

    audio_path = payload.get("audio_path")
    if not audio_path:
        raise NormalizationError("payload.audio_path is required")

    extension = Path(audio_path).suffix.lower()
    if extension not in _ALLOWED_AUDIO_EXTENSIONS:
        allowed = ", ".join(sorted(_ALLOWED_AUDIO_EXTENSIONS))
        raise NormalizationError(f"unsupported audio extension '{extension}', expected one of: {allowed}")

    input_kind = raw.get("input_kind", InputKind.VOICE.value)
    if input_kind != InputKind.VOICE.value:
        raise NormalizationError(f"unsupported input_kind '{input_kind}'")

    metadata = raw.get("metadata", {})
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise NormalizationError("metadata must be an object")

    return CoreRequest(
        source_adapter=str(raw["source_adapter"]),
        conversation_ref=str(raw["conversation_ref"]),
        user_ref=str(raw["user_ref"]),
        input_kind=InputKind.VOICE,
        payload={"audio_path": str(audio_path), **{k: v for k, v in payload.items() if k != "audio_path"}},
        metadata=metadata,
    )
