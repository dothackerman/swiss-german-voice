from __future__ import annotations

from dataclasses import dataclass

from swiss_german_voice.core.envelopes import CoreError, CoreRequest, CoreResponse, OutcomeStatus, TranscriptionRecord
from swiss_german_voice.core.lexicon import PersonalLexicon
from swiss_german_voice.core.persistence import SQLiteTranscriptionStore
from swiss_german_voice.core.transcription import AudioProcessingError, FasterWhisperTranscriber


@dataclass(slots=True)
class CoreRuntime:
    transcriber: FasterWhisperTranscriber
    store: SQLiteTranscriptionStore
    lexicon: PersonalLexicon

    def handle(self, request: CoreRequest) -> CoreResponse:
        try:
            transcript = self.transcriber.transcribe_file(
                request.payload["audio_path"],
                lexicon=self.lexicon,
            )
        except AudioProcessingError as exc:
            return CoreResponse(
                status=OutcomeStatus.TERMINAL_FAILURE,
                actions=["reply"],
                messages=["Voice processing failed."],
                errors=[CoreError(code="audio_processing_failed", message=str(exc), retryable=False)],
            )

        record_id = self.store.save(TranscriptionRecord(request=request, transcript=transcript))
        confidence = _confidence_summary(transcript)

        return CoreResponse(
            status=OutcomeStatus.SUCCESS,
            actions=["store", "reply"],
            messages=[transcript.text or "(No speech detected)", confidence],
            artifacts={
                "transcript": transcript.text,
                "record_id": record_id,
                "language": transcript.language,
                "segments": [
                    {
                        "text": seg.text,
                        "start": seg.start,
                        "end": seg.end,
                        "avg_logprob": seg.avg_logprob,
                        "no_speech_prob": seg.no_speech_prob,
                    }
                    for seg in transcript.segments
                ],
            },
        )


def _confidence_summary(transcript) -> str:
    if not transcript.segments:
        return "Confidence: no segments available."

    avg_logprobs = [seg.avg_logprob for seg in transcript.segments if seg.avg_logprob is not None]
    no_speech_probs = [seg.no_speech_prob for seg in transcript.segments if seg.no_speech_prob is not None]

    avg_logprob_text = "n/a"
    if avg_logprobs:
        avg_logprob_text = f"{sum(avg_logprobs) / len(avg_logprobs):.2f}"

    no_speech_text = "n/a"
    if no_speech_probs:
        no_speech_text = f"{sum(no_speech_probs) / len(no_speech_probs):.2f}"

    return f"Confidence proxy: avg_logprob={avg_logprob_text}, no_speech_prob={no_speech_text}."
