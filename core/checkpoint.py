import sqlite3
import os
import json
import time
from typing import Optional, Dict, Any, List

class CheckpointDatabase:
    """
    SQLite persistence for recovery sessions and state checkpoints.
    Allows crash recovery, pause/resume, and history tracking.
    """

    def __init__(self, db_path: str = "database/recovery.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_hash TEXT,
                    file_name TEXT,
                    file_path TEXT,
                    attack_type TEXT,
                    config_json TEXT,
                    status TEXT,
                    candidate_position INTEGER DEFAULT 0,
                    elapsed_seconds REAL DEFAULT 0.0,
                    recovered_password TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def create_session(self, file_hash: str, file_name: str, file_path: str, attack_type: str, config: Dict[str, Any]) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO sessions (file_hash, file_name, file_path, attack_type, config_json, status, candidate_position, elapsed_seconds)
                VALUES (?, ?, ?, ?, ?, 'RUNNING', 0, 0.0)
            """, (file_hash, file_name, file_path, attack_type, json.dumps(config)))
            conn.commit()
            return cursor.lastrowid

    def update_checkpoint(self, session_id: int, candidate_position: int, elapsed_seconds: float, status: str = "RUNNING", recovered_password: Optional[str] = None):
        with self._get_connection() as conn:
            conn.execute("""
                UPDATE sessions
                SET candidate_position = ?,
                    elapsed_seconds = ?,
                    status = ?,
                    recovered_password = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (candidate_position, elapsed_seconds, status, recovered_password, session_id))
            conn.commit()

    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d["config"] = json.loads(d["config_json"]) if d["config_json"] else {}
                return d
            return None

    def list_all_sessions(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM sessions ORDER BY updated_at DESC")
            return [dict(row) for row in cursor.fetchall()]
