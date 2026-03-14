import unittest
from dataclasses import dataclass

from swiss_german_voice.adapters.telegram.api import TelegramApiError
from swiss_german_voice.adapters.telegram.handler import TelegramVoiceHandler, render_telegram_reply
from swiss_german_voice.adapters.telegram.normalize import TelegramNormalizationError, normalize_telegram_voice_update
from swiss_german_voice.core.envelopes import CoreResponse, OutcomeStatus


@dataclass
class _FakeApi:
    downloaded: list[tuple[str, str]]
    sent: list[tuple[str, str]]

    def __init__(self) -> None:
        self.downloaded = []
        self.sent = []

    def get_file_path(self, file_id: str) -> str:
        return f"voice/{file_id}.ogg"

    def download_file(self, file_path: str, destination: str) -> str:
        self.downloaded.append((file_path, destination))
        return destination

    def send_message(self, chat_id: str, text: str) -> None:
        self.sent.append((chat_id, text))


class _FakeRuntime:
    def __init__(self) -> None:
        self.requests = []

    def handle(self, request):  # noqa: ANN001
        self.requests.append(request)
        return CoreResponse(
            status=OutcomeStatus.SUCCESS,
            actions=["reply"],
            messages=["hoi zame", "Confidence proxy: avg_logprob=-0.42, no_speech_prob=0.08."],
            artifacts={"record_id": 7},
            errors=[],
        )


class _RaisingRuntime:
    def handle(self, request):  # noqa: ANN001, ARG002
        raise RuntimeError("runtime failure")


class _RaisingApi(_FakeApi):
    def get_file_path(self, file_id: str) -> str:  # noqa: ARG002
        raise TelegramApiError("transport failure")


class TelegramNormalizeTests(unittest.TestCase):
    def test_normalize_voice_update(self) -> None:
        event = normalize_telegram_voice_update(
            {
                "message": {
                    "message_id": 12,
                    "chat": {"id": 99},
                    "from": {"id": 77},
                    "voice": {"file_id": "abc123"},
                }
            }
        )
        self.assertEqual(event.chat_id, "99")
        self.assertEqual(event.user_id, "77")
        self.assertEqual(event.file_id, "abc123")

    def test_normalize_voice_update_requires_voice(self) -> None:
        with self.assertRaises(TelegramNormalizationError):
            normalize_telegram_voice_update({"message": {"message_id": 1}})


class TelegramHandlerTests(unittest.TestCase):
    def test_handler_maps_update_to_core_and_replies(self) -> None:
        api = _FakeApi()
        runtime = _FakeRuntime()
        handler = TelegramVoiceHandler(api=api, runtime=runtime, media_dir="/tmp/tg-media")

        result = handler.handle_update(
            {
                "message": {
                    "message_id": 12,
                    "chat": {"id": 99},
                    "from": {"id": 77},
                    "voice": {"file_id": "abc123"},
                }
            }
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["record_id"], 7)

        self.assertEqual(len(runtime.requests), 1)
        mapped = runtime.requests[0]
        self.assertEqual(mapped.source_adapter, "telegram")
        self.assertEqual(mapped.conversation_ref, "99")
        self.assertEqual(mapped.user_ref, "77")
        self.assertIn("audio_path", mapped.payload)

        self.assertEqual(len(api.sent), 1)
        chat_id, text = api.sent[0]
        self.assertEqual(chat_id, "99")
        self.assertIn("hoi zame", text)
        self.assertIn("Confidence proxy", text)

    def test_render_telegram_reply(self) -> None:
        text = render_telegram_reply(["line one", "", "line two"])
        self.assertEqual(text, "line one\nline two")

    def test_handler_download_filename_ignores_untrusted_ids(self) -> None:
        api = _FakeApi()
        runtime = _FakeRuntime()
        handler = TelegramVoiceHandler(api=api, runtime=runtime, media_dir="/tmp/tg-media")

        handler.handle_update(
            {
                "message": {
                    "message_id": "../../../etc/passwd",
                    "chat": {"id": "../../tmp"},
                    "from": {"id": 77},
                    "voice": {"file_id": "abc123"},
                }
            }
        )

        self.assertEqual(len(api.downloaded), 1)
        _, destination = api.downloaded[0]
        self.assertTrue(destination.startswith("/tmp/tg-media/tg_"))
        self.assertTrue(destination.endswith(".ogg"))
        self.assertNotIn("..", destination)
        self.assertNotIn("passwd", destination)

    def test_try_handle_update_catches_transport_errors(self) -> None:
        handler = TelegramVoiceHandler(api=_RaisingApi(), runtime=_FakeRuntime(), media_dir="/tmp/tg-media")
        result = handler.try_handle_update(
            {
                "message": {
                    "message_id": 12,
                    "chat": {"id": 99},
                    "from": {"id": 77},
                    "voice": {"file_id": "abc123"},
                }
            }
        )
        self.assertIsNone(result)

    def test_try_handle_update_catches_unexpected_errors(self) -> None:
        handler = TelegramVoiceHandler(api=_FakeApi(), runtime=_RaisingRuntime(), media_dir="/tmp/tg-media")
        result = handler.try_handle_update(
            {
                "message": {
                    "message_id": 12,
                    "chat": {"id": 99},
                    "from": {"id": 77},
                    "voice": {"file_id": "abc123"},
                }
            }
        )
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
