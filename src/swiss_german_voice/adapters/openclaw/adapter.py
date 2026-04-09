from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from swiss_german_voice.core.correction import TranscriptCorrectionLayer
from swiss_german_voice.core.normalize import normalize_core_request
from swiss_german_voice.core.service import CoreRuntime

_AVG_LOGPROB_THRESHOLD = -1.0
_NO_SPEECH_THRESHOLD = 0.6


@dataclass(slots=True)
class OpenClawVoiceAdapter:
    runtime: CoreRuntime
    correction_layer: TranscriptCorrectionLayer

    def __init__(
        self,
        runtime: CoreRuntime,
        correction_layer: TranscriptCorrectionLayer | None = None,
    ) -> None:
        self.runtime = runtime
        self.correction_layer = correction_layer or TranscriptCorrectionLayer.default()

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
        interpretation = self.correction_layer.correct(transcript)
        confidence_label, flagged_segments, flagged_details = _summarize_confidence(core_response.artifacts)
        confidence_summary = f"{confidence_label} - {flagged_segments} segments flagged"
        reply_text = _render_reply_text(
            transcript=transcript,
            interpretation=interpretation,
            confidence_label=confidence_label,
            flagged_segments=flagged_segments,
            flagged_details=flagged_details,
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


def _summarize_confidence(artifacts: dict[str, Any] | None) -> tuple[str, int, list[dict[str, Any]]]:
    segments = []
    if artifacts and isinstance(artifacts.get("segments"), list):
        segments = artifacts["segments"]

    if not segments:
        return ("low", 0, [])

    flagged_indices: list[int] = []
    for i, segment in enumerate(segments):
        if not isinstance(segment, dict):
            continue
        avg_logprob = segment.get("avg_logprob")
        no_speech_prob = segment.get("no_speech_prob")
        low_logprob = avg_logprob is not None and avg_logprob < _AVG_LOGPROB_THRESHOLD
        high_no_speech = no_speech_prob is not None and no_speech_prob > _NO_SPEECH_THRESHOLD
        if low_logprob or high_no_speech:
            flagged_indices.append(i)

    flagged_details: list[dict[str, Any]] = []
    for i in flagged_indices:
        seg = segments[i]
        prev_text = segments[i - 1].get("text", "").strip() if i > 0 else None
        next_text = segments[i + 1].get("text", "").strip() if i < len(segments) - 1 else None
        flagged_details.append({
            "text": seg.get("text", "").strip(),
            "start": seg.get("start"),
            "end": seg.get("end"),
            "prev": prev_text,
            "next": next_text,
        })

    ratio = len(flagged_indices) / len(segments)
    if ratio == 0:
        label = "high"
    elif ratio <= 0.5:
        label = "medium"
    else:
        label = "low"
    return (label, len(flagged_indices), flagged_details)


def _fmt_time(seconds: float | None) -> str:
    if seconds is None:
        return "?"
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def _render_reply_text(
    *,
    transcript: str,
    interpretation: str,
    confidence_label: str,
    flagged_segments: int,
    flagged_details: list[dict[str, Any]],
) -> str:
    lines = [
        "🎙 Transkript:",
        transcript,
        "",
        "💡 Interpretation:",
        interpretation,
        "",
        f"📊 Konfidenz: {confidence_label} ({flagged_segments} Segmente unter Schwellenwert)",
    ]

    if flagged_details:
        lines.append("")
        lines.append("⚠️ Zur Überprüfung:")
        for detail in flagged_details:
            start = _fmt_time(detail.get("start"))
            end = _fmt_time(detail.get("end"))
            text = detail.get("text") or ""
            prev_text = detail.get("prev")
            next_text = detail.get("next")
            lines.append(f"  [{start}–{end}] \"{text}\"")
            if prev_text:
                lines.append(f"    vorher:  \"{prev_text}\"")
            if next_text:
                lines.append(f"    nachher: \"{next_text}\"")

    return "\n".join(lines)
