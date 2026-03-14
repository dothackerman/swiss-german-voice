import unittest
from pathlib import Path

from swiss_german_voice.core.envelopes import CoreRequest, InputKind, SegmentUncertainty, TranscriptResult, TranscriptionRecord
from swiss_german_voice.core.persistence import SQLiteTranscriptionStore


class SQLiteTranscriptionStoreTests(unittest.TestCase):
    def test_save_and_fetch_roundtrip(self) -> None:
        tmp_dir = Path("/tmp/swiss-german-voice-tests")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        db_path = tmp_dir / "transcriptions.sqlite"
        if db_path.exists():
            db_path.unlink()

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


if __name__ == "__main__":
    unittest.main()
