import unittest
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from swiss_german_voice.adapters.openclaw.adapter import OpenClawVoiceAdapter
from swiss_german_voice.core.correction import TranscriptCorrectionLayer
from swiss_german_voice.core.envelopes import CoreResponse, OutcomeStatus


@dataclass
class _FakeRuntime:
    requests: list

    def __init__(self) -> None:
        self.requests = []

    def handle(self, request):  # noqa: ANN001
        self.requests.append(request)
        return CoreResponse(
            status=OutcomeStatus.SUCCESS,
            actions=["store", "reply"],
            messages=["i ha en bug im branch"],
            artifacts={
                "transcript": "i ha en bug im branch",
                "segments": [
                    {"text": "i ha en bug", "start": 0.0, "end": 1.1, "avg_logprob": -0.25, "no_speech_prob": 0.05},
                    {"text": "im branch", "start": 1.1, "end": 2.1, "avg_logprob": -1.2, "no_speech_prob": 0.1},
                ],
            },
            errors=[],
        )


class OpenClawAdapterTests(unittest.TestCase):
    def test_process_voice_memo_maps_request_and_builds_reply(self) -> None:
        runtime = _FakeRuntime()
        adapter = OpenClawVoiceAdapter(runtime=runtime)

        result = adapter.process_voice_memo(
            "/tmp/input.ogg",
            user_ref="og-user-1",
            conversation_ref="conv-9",
        )

        self.assertEqual(len(runtime.requests), 1)
        request = runtime.requests[0]
        self.assertEqual(request.source_adapter, "openclaw")
        self.assertEqual(request.user_ref, "og-user-1")
        self.assertEqual(request.conversation_ref, "conv-9")
        self.assertEqual(request.payload["audio_path"], "/tmp/input.ogg")
        self.assertEqual(request.metadata["language_hint"], "de")

        self.assertEqual(result["transcript"], "i ha en bug im branch")
        self.assertIn("ich", result["interpretation"].lower())
        self.assertIn("medium - 1 segments flagged", result["confidence_summary"])
        self.assertIn("🎙 Transkript:", result["reply_text"])
        self.assertIn("💡 Interpretation:", result["reply_text"])
        self.assertIn("📊 Konfidenz: medium (1 Segmente unter Schwellenwert)", result["reply_text"])

    def test_process_voice_memo_uses_configurable_lexicon_layer(self) -> None:
        with TemporaryDirectory(prefix="swiss-german-voice-tests-") as tmp_dir:
            lexicon_path = Path(tmp_dir) / "lexicon.json"
            lexicon_path.write_text(
                '{"replacements":[{"from":"bug","to":"issue"},{"from":"branch","to":"zweig"}]}',
                encoding="utf-8",
            )
            runtime = _FakeRuntime()
            adapter = OpenClawVoiceAdapter(
                runtime=runtime,
                correction_layer=TranscriptCorrectionLayer.from_file(str(lexicon_path)),
            )

            result = adapter.process_voice_memo(
                "/tmp/input.ogg",
                user_ref="og-user-1",
                conversation_ref="conv-9",
            )

            self.assertIn("issue", result["interpretation"])
            self.assertIn("zweig", result["interpretation"])


if __name__ == "__main__":
    unittest.main()
