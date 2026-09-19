from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from nekomimi_mcp.intent.schema import IntentStream, IntentToken


def _token_str(t: IntentToken | str) -> str:
    # IntentStream coerces StrEnum members to plain str on validation —
    # accept both so recording never crashes the calling tool.
    return t.value if isinstance(t, IntentToken) else str(t)


class IntentRecorder:
    def __init__(self, db_path: str | None = None):
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / "data" / "intents.db")
        self._db_path = db_path
        _ensure_db(db_path)

    def record(self, stream: IntentStream, renderer: str, results: list[dict]) -> int:
        conn = sqlite3.connect(self._db_path)
        try:
            cur = conn.execute(
                "INSERT INTO recordings (renderer, token_sequence, params_json, results_json, recorded_at) VALUES (?, ?, ?, ?, ?)",
                (
                    renderer,
                    json.dumps([_token_str(t) for t in stream.tokens]),
                    stream.params.model_dump_json(),
                    json.dumps(results),
                    int(time.time()),
                ),
            )
            conn.commit()
            return cur.lastrowid or 0
        finally:
            conn.close()

    def list_recordings(
        self, limit: int = 20, renderer: str | None = None, offset: int = 0
    ) -> list[dict]:
        conn = sqlite3.connect(self._db_path)
        try:
            if renderer:
                rows = conn.execute(
                    "SELECT * FROM recordings WHERE renderer=? ORDER BY id DESC LIMIT ? OFFSET ?",
                    (renderer, limit, offset),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM recordings ORDER BY id DESC LIMIT ? OFFSET ?",
                    (limit, offset),
                ).fetchall()
            return [_row_to_dict(r) for r in rows]
        finally:
            conn.close()

    def get_recording(self, recording_id: int) -> dict | None:
        conn = sqlite3.connect(self._db_path)
        try:
            row = conn.execute("SELECT * FROM recordings WHERE id=?", (recording_id,)).fetchone()
            return _row_to_dict(row) if row else None
        finally:
            conn.close()

    def export_jsonl(self, path: str) -> int:
        conn = sqlite3.connect(self._db_path)
        try:
            rows = conn.execute("SELECT * FROM recordings ORDER BY id").fetchall()
            count = 0
            with open(path, "w", encoding="utf-8") as f:
                for row in rows:
                    rec_id, renderer, tokens_json, params_json, results_json, ts = row
                    f.write(
                        json.dumps(
                            {
                                "id": rec_id,
                                "renderer": renderer,
                                "tokens": json.loads(tokens_json),
                                "params": json.loads(params_json),
                                "results": json.loads(results_json),
                                "timestamp": ts,
                            }
                        )
                        + "\n"
                    )
                    count += 1
            return count
        finally:
            conn.close()


def _row_to_dict(row: tuple) -> dict:
    rec_id, renderer, tokens_json, params_json, results_json, ts = row
    return {
        "id": rec_id,
        "renderer": renderer,
        "tokens": json.loads(tokens_json),
        "params": json.loads(params_json),
        "results": json.loads(results_json),
        "timestamp": ts,
    }


def _ensure_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS recordings (id INTEGER PRIMARY KEY AUTOINCREMENT, renderer TEXT NOT NULL, token_sequence TEXT NOT NULL, params_json TEXT NOT NULL, results_json TEXT NOT NULL, recorded_at INTEGER NOT NULL)"
        )
        conn.commit()
    finally:
        conn.close()
