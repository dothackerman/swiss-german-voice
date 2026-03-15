from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PersonalLexicon:
    words: list[str]

    @classmethod
    def from_config(cls, config: dict[str, list[str]] | None) -> "PersonalLexicon":
        if not config:
            return cls(words=[])
        words = config.get("words", [])
        normalized = [word.strip() for word in words if isinstance(word, str) and word.strip()]
        return cls(words=normalized)

    def to_prompt_fragment(self) -> str:
        if not self.words:
            return ""
        joined = ", ".join(self.words)
        return f"Prefer these terms: {joined}."
