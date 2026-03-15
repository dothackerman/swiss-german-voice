import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from swiss_german_voice.adapters.openclaw.adapter import OpenClawVoiceAdapter
from swiss_german_voice.factory import build_adapter


class FactoryTests(unittest.TestCase):
    def test_build_adapter_constructs_openclaw_pipeline(self) -> None:
        with TemporaryDirectory(prefix="swiss-german-voice-tests-") as tmp_dir:
            db_path = str(Path(tmp_dir) / "voice.sqlite3")
            adapter = build_adapter(
                db_path=db_path,
                lexicon_words=["OpenClaw", "Scripts"],
                model_size="small",
                language="de",
            )

            self.assertIsInstance(adapter, OpenClawVoiceAdapter)
            self.assertEqual(adapter.runtime.store.db_path, db_path)
            self.assertEqual(adapter.runtime.transcriber.config.model_size, "small")
            self.assertEqual(adapter.runtime.transcriber.config.language, "de")
            self.assertEqual(adapter.runtime.lexicon.words, ["OpenClaw", "Scripts"])


if __name__ == "__main__":
    unittest.main()
