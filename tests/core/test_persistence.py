import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from swiss_german_voice.core.envelopes import CoreRequest, InputKind, SegmentUncertainty, TranscriptResult, TranscriptionRecord
from swiss_german_voice.core.persistence import PersistenceError, SQLiteTranscriptionStore


class SQLiteTranscriptionStoreTests(unittest.TestCase):
    def test_save_and_fetch_roundtrip(self) -> None:
        with TemporaryDirectory(prefix="swiss-german-voice-tests-") as tmp_dir:
            db_path = Path(tmp_dir) / "transcriptions.sqlite"
            store = SQLiteTranscriptionStore(str(db_path))

            request = CoreRequest(
                source_adapter="telegram",
                conversation_ref="chat-1",
                user_ref="user-1",
                input_kind=InputKind.VOICE,
                payload={"audio_path": "/tmp/audio.ogg"},
                metadata={"trace_id": "abc"},
            )
            transcript = TranscriptResult(
                text="hoi zame",
                language="de",
                duration_seconds=2.5,
                segments=[
                    SegmentUncertainty(
                        text="hoi zame",
                        start=0.0,
                        end=2.5,
                        avg_logprob=-0.17,
                        no_speech_prob=0.04,
                    )
                ],
            )

            record_id = store.save(TranscriptionRecord(request=request, transcript=transcript))
            saved = store.fetch_by_id(record_id)

            self.assertIsNotNone(saved)
            assert saved is not None
            self.assertEqual(saved.id, record_id)
            self.assertEqual(saved.request.conversation_ref, "chat-1")
            self.assertEqual(saved.transcript.text, "hoi zame")
            self.assertEqual(saved.transcript.segments[0].avg_logprob, -0.17)

    def test_save_rejects_missing_audio_path(self) -> None:
        with TemporaryDirectory(prefix="swiss-german-voice-tests-") as tmp_dir:
            db_path = Path(tmp_dir) / "transcriptions.sqlite"
            store = SQLiteTranscriptionStore(str(db_path))
            record = TranscriptionRecord(request=_request(audio_path=None), transcript=_transcript())
            with self.assertRaisesRegex(PersistenceError, "audio_path is required"):
                store.save(record)

    def test_save_rejects_non_json_serializable_metadata(self) -> None:
        with TemporaryDirectory(prefix="swiss-german-voice-tests-") as tmp_dir:
            db_path = Path(tmp_dir) / "transcriptions.sqlite"
            store = SQLiteTranscriptionStore(str(db_path))
            record = TranscriptionRecord(
                request=_request(audio_path="/tmp/audio.ogg", metadata={"captured_at": datetime.now()}),
                transcript=_transcript(),
            )
            with self.assertRaisesRegex(PersistenceError, "JSON-serializable"):
                store.save(record)


def _request(audio_path, metadata: dict | None = None) -> CoreRequest:  # noqa: ANN001
    return CoreRequest(
        source_adapter="telegram",
        conversation_ref="chat-1",
        user_ref="user-1",
        input_kind=InputKind.VOICE,
        payload={"audio_path": audio_path} if audio_path is not None else {},
        metadata=metadata or {"trace_id": "abc"},
    )


def _transcript() -> TranscriptResult:
    return TranscriptResult(
        text="hoi zame",
        language="de",
        duration_seconds=2.5,
        segments=[
            SegmentUncertainty(
                text="hoi zame",
                start=0.0,
                end=2.5,
                avg_logprob=-0.17,
                no_speech_prob=0.04,
            )
        ],
    )


if __name__ == "__main__":
    unittest.main()
