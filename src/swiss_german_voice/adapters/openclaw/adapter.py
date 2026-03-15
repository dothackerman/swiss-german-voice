from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

from swiss_german_voice.core.normalize import normalize_core_request
from swiss_german_voice.core.service import CoreRuntime

_AVG_LOGPROB_THRESHOLD = -1.0
_NO_SPEECH_THRESHOLD = 0.6


@dataclass(slots=True)
class OpenClawVoiceAdapter:
    runtime: CoreRuntime

    def process_voice_memo(
        self,
        audio_path: str,
        *,
        user_ref: str,
        conversation_ref: str,
        language_hint: str = "de",
    ) -> dict[str, str]:
        core_request = normalize_core_request(
            {
                "source_adapter": "openclaw",
                "conversation_ref": conversation_ref,
                "user_ref": user_ref,
                "input_kind": "voice",
                "payload": {"audio_path": audio_path},
                "metadata": {"language_hint": language_hint},
            }
        )

        core_response = self.runtime.handle(core_request)
        transcript = _extract_transcript(core_response)
        interpretation = _interpret_transcript(transcript)
        confidence_label, flagged_segments = _summarize_confidence(core_response.artifacts)
        confidence_summary = f"{confidence_label} - {flagged_segments} segments flagged"
        reply_text = _render_reply_text(
            transcript=transcript,
            interpretation=interpretation,
            confidence_label=confidence_label,
            flagged_segments=flagged_segments,
        )

        return {
            "transcript": transcript,
            "interpretation": interpretation,
            "confidence_summary": confidence_summary,
            "reply_text": reply_text,
        }


def _extract_transcript(core_response: Any) -> str:
    transcript = ""
    if getattr(core_response, "artifacts", None):
        transcript = str(core_response.artifacts.get("transcript") or "")

    if not transcript:
        messages = getattr(core_response, "messages", []) or []
        if messages:
            transcript = str(messages[0])

    return transcript.strip() or "(Keine Sprache erkannt)"


def _interpret_transcript(transcript: str) -> str:
    cleaned = " ".join(transcript.split())
    if not cleaned:
        return "(Keine Interpretation verfuegbar)"

    replacements = [
        (r"\bi\b", "ich"),
        (r"\bmer\b", "wir"),
        (r"\bhei?t\b", "heisst"),
        (r"\bgit\b", "gibt"),
        (r"\bned\b", "nicht"),
        (r"\bnid\b", "nicht"),
        (r"\bschaffe\b", "arbeiten"),
        (r"\bbugfix\b", "bug fix"),
        (r"\bfehlermeldig\b", "bug report"),
        (r"\bdeploye\b", "deployen"),
    ]

    interpreted = cleaned
    for pattern, target in replacements:
        interpreted = re.sub(pattern, target, interpreted, flags=re.IGNORECASE)

    return interpreted[:1].upper() + interpreted[1:]


def _summarize_confidence(artifacts: dict[str, Any] | None) -> tuple[str, int]:
    segments = []
    if artifacts and isinstance(artifacts.get("segments"), list):
        segments = artifacts["segments"]

    if not segments:
        return ("low", 0)

    flagged = 0
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        avg_logprob = segment.get("avg_logprob")
        no_speech_prob = segment.get("no_speech_prob")
        low_logprob = avg_logprob is not None and avg_logprob < _AVG_LOGPROB_THRESHOLD
        high_no_speech = no_speech_prob is not None and no_speech_prob > _NO_SPEECH_THRESHOLD
        if low_logprob or high_no_speech:
            flagged += 1

    ratio = flagged / len(segments)
    if ratio == 0:
        return ("high", flagged)
    if ratio <= 0.5:
        return ("medium", flagged)
    return ("low", flagged)


def _render_reply_text(
    *,
    transcript: str,
    interpretation: str,
    confidence_label: str,
    flagged_segments: int,
) -> str:
    return (
        "🎙 Transkript:\n"
        f"{transcript}\n\n"
        "💡 Interpretation:\n"
        f"{interpretation}\n\n"
        f"📊 Konfidenz: {confidence_label} ({flagged_segments} Segmente unter Schwellenwert)"
    )
