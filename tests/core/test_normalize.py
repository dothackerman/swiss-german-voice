import unittest

from swiss_german_voice.core.envelopes import InputKind
from swiss_german_voice.core.normalize import NormalizationError, normalize_core_request


class NormalizeCoreRequestTests(unittest.TestCase):
    def test_normalize_core_request_success(self) -> None:
        request = normalize_core_request(
            {
                "source_adapter": "telegram",
                "conversation_ref": "chat-123",
                "user_ref": "user-42",
                "payload": {"audio_path": "/tmp/test.ogg"},
                "metadata": {"locale": "gsw-CH"},
            }
        )

        self.assertEqual(request.source_adapter, "telegram")
        self.assertEqual(request.input_kind, InputKind.VOICE)
        self.assertEqual(request.payload["audio_path"], "/tmp/test.ogg")
        self.assertEqual(request.metadata["locale"], "gsw-CH")

    def test_normalize_core_request_rejects_bad_extension(self) -> None:
        with self.assertRaisesRegex(NormalizationError, "unsupported audio extension"):
            normalize_core_request(
                {
                    "source_adapter": "telegram",
                    "conversation_ref": "chat-123",
                    "user_ref": "user-42",
                    "payload": {"audio_path": "/tmp/test.mp3"},
                }
            )

    def test_normalize_core_request_accepts_telegram_oga_extension(self) -> None:
        request = normalize_core_request(
            {
                "source_adapter": "telegram",
                "conversation_ref": "chat-123",
                "user_ref": "user-42",
                "payload": {"audio_path": "/tmp/test.oga"},
            }
        )
        self.assertEqual(request.payload["audio_path"], "/tmp/test.oga")

    def test_normalize_core_request_requires_fields(self) -> None:
        with self.assertRaisesRegex(NormalizationError, "missing required fields"):
            normalize_core_request({"source_adapter": "telegram"})


if __name__ == "__main__":
    unittest.main()
