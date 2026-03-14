from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class InputKind(str, Enum):
    VOICE = "voice"


class OutcomeStatus(str, Enum):
    SUCCESS = "success"
    RETRYABLE_FAILURE = "retryable_failure"
    TERMINAL_FAILURE = "terminal_failure"


@dataclass(slots=True)
class CoreRequest:
    source_adapter: str
    conversation_ref: str
    user_ref: str
    input_kind: InputKind
    payload: dict[str, Any]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CoreError:
    code: str
    message: str
    retryable: bool


@dataclass(slots=True)
class CoreResponse:
    status: OutcomeStatus
    actions: list[str]
    messages: list[str]
    artifacts: dict[str, Any] = field(default_factory=dict)
    errors: list[CoreError] = field(default_factory=list)


@dataclass(slots=True)
class SegmentUncertainty:
    text: str
    start: float
    end: float
    avg_logprob: float | None
    no_speech_prob: float | None


@dataclass(slots=True)
class TranscriptResult:
    text: str
    language: str | None
    duration_seconds: float | None
    segments: list[SegmentUncertainty]


@dataclass(slots=True)
class TranscriptionRecord:
    request: CoreRequest
    transcript: TranscriptResult
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: int | None = None
