"""Intent stream record/replay for regression testing."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from nekomimi_mcp.intent.tokens import IntentFrame

DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"


def _get_db() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DATA_DIR / "intent_stream.sqlite3"))
    db.row_factory = sqlite3.Row
    db.execute(
        """CREATE TABLE IF NOT EXISTS intent_stream (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            stream_name TEXT NOT NULL,
            sequence_index INTEGER NOT NULL,
            frame_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )"""
    )
    db.execute(
        """CREATE TABLE IF NOT EXISTS intent_recording (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            frame_count INTEGER NOT NULL DEFAULT 0
        )"""
    )
    db.commit()
    return db


def record_frame(stream_name: str, frame: IntentFrame, index: int) -> None:
    db = _get_db()
    sql = (
        "INSERT INTO intent_stream "
        "(stream_name, sequence_index, frame_json, created_at) "
        "VALUES (?, ?, ?, ?)"
    )
    db.execute(sql, (stream_name, index, frame.model_dump_json(), datetime.now(UTC).isoformat()))
    db.execute(
        "INSERT OR REPLACE INTO intent_recording (name, created_at, frame_count) VALUES (?, ?, "
        "(SELECT COUNT(*) FROM intent_stream WHERE stream_name = ?))",
        (stream_name, datetime.now(UTC).isoformat(), stream_name),
    )
    db.commit()


def list_recordings() -> list[dict]:
    db = _get_db()
    rows = db.execute("SELECT * FROM intent_recording ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def get_stream(stream_name: str) -> list[IntentFrame]:
    db = _get_db()
    rows = db.execute(
        "SELECT * FROM intent_stream WHERE stream_name = ? ORDER BY sequence_index",
        (stream_name,),
    ).fetchall()
    return [IntentFrame.model_validate_json(r["frame_json"]) for r in rows]


def delete_recording(name: str) -> bool:
    db = _get_db()
    db.execute("DELETE FROM intent_stream WHERE stream_name = ?", (name,))
    c = db.execute("DELETE FROM intent_recording WHERE name = ?", (name,))
    db.commit()
    return c.rowcount > 0
