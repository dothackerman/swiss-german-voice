from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from swiss_german_voice.core.envelopes import CoreRequest, InputKind, SegmentUncertainty, TranscriptResult, TranscriptionRecord


class SQLiteTranscriptionStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._ensure_db()

    def save(self, record: TranscriptionRecord) -> int:
        conn = sqlite3.connect(self.db_path)
        try:
            with conn:
                cursor = conn.execute(
                    """
                    INSERT INTO transcriptions (
                        source_adapter,
                        conversation_ref,
                        user_ref,
                        input_kind,
                        audio_path,
                        transcript_text,
                        language,
                        duration_seconds,
                        segment_signals_json,
                        metadata_json,
                        created_at_utc
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.request.source_adapter,
                        record.request.conversation_ref,
                        record.request.user_ref,
                        record.request.input_kind.value,
                        record.request.payload.get("audio_path"),
                        record.transcript.text,
                        record.transcript.language,
                        record.transcript.duration_seconds,
                        json.dumps([asdict(seg) for seg in record.transcript.segments]),
                        json.dumps(record.request.metadata),
                        record.created_at.astimezone(timezone.utc).isoformat(),
                    ),
                )
            return int(cursor.lastrowid)
        finally:
            conn.close()

    def fetch_by_id(self, record_id: int) -> TranscriptionRecord | None:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                "SELECT * FROM transcriptions WHERE id = ?",
                (record_id,),
            ).fetchone()
            if row is None:
                return None

            request = CoreRequest(
                source_adapter=row["source_adapter"],
                conversation_ref=row["conversation_ref"],
                user_ref=row["user_ref"],
                input_kind=InputKind(row["input_kind"]),
                payload={"audio_path": row["audio_path"]},
                metadata=json.loads(row["metadata_json"]),
            )
            segments = [SegmentUncertainty(**item) for item in json.loads(row["segment_signals_json"])]
            transcript = TranscriptResult(
                text=row["transcript_text"],
                language=row["language"],
                duration_seconds=row["duration_seconds"],
                segments=segments,
            )
            created_at = datetime.fromisoformat(row["created_at_utc"])
            return TranscriptionRecord(request=request, transcript=transcript, created_at=created_at, id=row["id"])
        finally:
            conn.close()

    def _ensure_db(self) -> None:
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        try:
            with conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS transcriptions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_adapter TEXT NOT NULL,
                        conversation_ref TEXT NOT NULL,
                        user_ref TEXT NOT NULL,
                        input_kind TEXT NOT NULL,
                        audio_path TEXT NOT NULL,
                        transcript_text TEXT NOT NULL,
                        language TEXT,
                        duration_seconds REAL,
                        segment_signals_json TEXT NOT NULL,
                        metadata_json TEXT NOT NULL,
                        created_at_utc TEXT NOT NULL
                    )
                    """
                )
        finally:
            conn.close()
