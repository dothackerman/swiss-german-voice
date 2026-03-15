import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from swiss_german_voice.core.correction import TranscriptCorrectionLayer


class TranscriptCorrectionLayerTests(unittest.TestCase):
    def test_default_layer_applies_known_replacements(self) -> None:
        layer = TranscriptCorrectionLayer.default()
        corrected = layer.correct("open cloud und skrips")
        self.assertEqual(corrected, "OpenClaw und Scripts")

    def test_from_file_uses_configurable_rules(self) -> None:
        with TemporaryDirectory(prefix="swiss-german-voice-tests-") as tmp_dir:
            path = Path(tmp_dir) / "lexicon.json"
            path.write_text(
                '{"replacements":[{"from":"alpha beta","to":"X"},{"from":"alpha","to":"Y"}]}',
                encoding="utf-8",
            )
            layer = TranscriptCorrectionLayer.from_file(str(path))
            corrected = layer.correct("alpha beta alpha")
            self.assertEqual(corrected, "X Y")


if __name__ == "__main__":
    unittest.main()
