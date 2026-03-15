from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

from importlib import resources


@dataclass(frozen=True, slots=True)
class LexiconRule:
    source: str
    target: str


@dataclass(slots=True)
class TranscriptCorrectionLayer:
    rules: list[LexiconRule]

    @classmethod
    def from_file(cls, path: str) -> "TranscriptCorrectionLayer":
        loaded = _load_rules_from_path(Path(path))
        return cls(rules=loaded)

    @classmethod
    def default(cls) -> "TranscriptCorrectionLayer":
        data_path = resources.files("swiss_german_voice").joinpath("data/lexicon_corrections.json")
        loaded = _load_rules_from_path(Path(str(data_path)))
        return cls(rules=loaded)

    def correct(self, transcript: str) -> str:
        cleaned = " ".join((transcript or "").split())
        if not cleaned:
            return "(Keine Interpretation verfuegbar)"

        corrected = cleaned
        for rule in self.rules:
            pattern = _token_boundary_pattern(rule.source)
            corrected = re.sub(pattern, rule.target, corrected, flags=re.IGNORECASE)
        return corrected


def _load_rules_from_path(path: Path) -> list[LexiconRule]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    entries = raw.get("replacements", []) if isinstance(raw, dict) else []
    rules: list[LexiconRule] = []
    for entry in entries:
        source, target = _extract_rule(entry)
        if source and target:
            rules.append(LexiconRule(source=source, target=target))

    rules.sort(key=lambda rule: len(rule.source), reverse=True)
    return rules


def _extract_rule(entry: Any) -> tuple[str, str]:
    if not isinstance(entry, dict):
        return ("", "")
    source = entry.get("from")
    target = entry.get("to")
    if not isinstance(source, str) or not isinstance(target, str):
        return ("", "")
    return (source.strip(), target.strip())


def _token_boundary_pattern(source: str) -> str:
    escaped = re.escape(source)
    return rf"(?<!\w){escaped}(?!\w)"
