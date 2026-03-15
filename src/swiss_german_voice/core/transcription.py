from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from swiss_german_voice.core.envelopes import SegmentUncertainty, TranscriptResult
from swiss_german_voice.core.lexicon import PersonalLexicon


class AudioProcessingError(RuntimeError):
    """Raised for local audio processing/transcription failures."""


@dataclass(slots=True)
class WhisperConfig:
    model_size: str = "small"
    language: str = "de"


class FasterWhisperTranscriber:
    """CUDA-first faster-whisper transcriber with CPU fallback."""

    def __init__(self, config: WhisperConfig | None = None) -> None:
        self.config = config or WhisperConfig()
        self._model: Any | None = None
        self._device_selected: str | None = None

    def transcribe_file(self, audio_path: str, lexicon: PersonalLexicon | None = None) -> TranscriptResult:
        path = Path(audio_path)
        if not path.exists() or not path.is_file():
            raise AudioProcessingError(f"audio file does not exist: {audio_path}")

        model = self._get_model()
        lexicon = lexicon or PersonalLexicon(words=[])
        prompt = lexicon.to_prompt_fragment() or None

        try:
            segments, info = model.transcribe(
                str(path),
                language=self.config.language,
                vad_filter=True,
                initial_prompt=prompt,
            )
        except Exception as exc:  # pragma: no cover - backend/runtime dependent
            raise AudioProcessingError(f"transcription failed: {exc}") from exc

        collected: list[SegmentUncertainty] = []
        text_parts: list[str] = []
        for segment in segments:
            segment_text = segment.text.strip()
            if segment_text:
                text_parts.append(segment_text)
            collected.append(
                SegmentUncertainty(
                    text=segment_text,
                    start=float(segment.start),
                    end=float(segment.end),
                    avg_logprob=_to_optional_float(getattr(segment, "avg_logprob", None)),
                    no_speech_prob=_to_optional_float(getattr(segment, "no_speech_prob", None)),
                )
            )

        return TranscriptResult(
            text=" ".join(text_parts).strip(),
            language=getattr(info, "language", None),
            duration_seconds=_to_optional_float(getattr(info, "duration", None)),
            segments=collected,
        )

    def _get_model(self) -> Any:
        if self._model is not None:
            return self._model

        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:  # pragma: no cover - environment dependent
            raise AudioProcessingError(
                "faster-whisper is not installed. Install project dependencies first."
            ) from exc

        attempts = [
            ("cuda", "float16"),
            ("cpu", "int8"),
        ]
        last_error: Exception | None = None

        for device, compute_type in attempts:
            try:
                self._model = WhisperModel(
                    self.config.model_size,
                    device=device,
                    compute_type=compute_type,
                )
                self._device_selected = device
                return self._model
            except Exception as exc:  # pragma: no cover - backend/runtime dependent
                last_error = exc

        raise AudioProcessingError(f"unable to initialize faster-whisper model: {last_error}")


def _to_optional_float(value: object) -> float | None:
    if value is None:
        return None
    return float(value)
