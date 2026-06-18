"""SQLite-based knowledge backend for persistent storage."""

from typing import Dict, Any, Optional, List
import sqlite3
import json
import threading
from pathlib import Path
from .base import KnowledgeBackend


class SQLiteKnowledgeBackend(KnowledgeBackend):
    """
    SQLite-based knowledge backend for persistent, ACID-compliant storage.
    Thread-safe with connection pooling via thread-local connections.
    """

    def __init__(self, path: str = "knowledge.db"):
        self._path = Path(path)
        self._local = threading.local()
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            self._local.conn = sqlite3.connect(str(self._path))
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn

    def _init_db(self):
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at REAL NOT NULL DEFAULT (julianday('now'))
            )
        """)
        conn.commit()

    def query(self, concept_key: str) -> Optional[Any]:
        conn = self._get_conn()
        cur = conn.execute("SELECT value FROM knowledge WHERE key = ?", (concept_key.lower(),))
        row = cur.fetchone()
        if row is None:
            return None
        return json.loads(row["value"])

    def query_concepts(self, concepts: List[str]) -> Dict[str, Optional[Any]]:
        return {c: self.query(c) for c in concepts}

    def update(self, concept_key: str, data: Any):
        conn = self._get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO knowledge (key, value, updated_at) VALUES (?, ?, julianday('now'))",
            (concept_key.lower(), json.dumps(data)),
        )
        conn.commit()

    def bulk_update(self, data: Dict[str, Any]):
        conn = self._get_conn()
        rows = [(k.lower(), json.dumps(v)) for k, v in data.items()]
        conn.executemany(
            "INSERT OR REPLACE INTO knowledge (key, value, updated_at) VALUES (?, ?, julianday('now'))",
            rows,
        )
        conn.commit()

    def get_all(self) -> Dict[str, Any]:
        conn = self._get_conn()
        cur = conn.execute("SELECT key, value FROM knowledge")
        return {row["key"]: json.loads(row["value"]) for row in cur.fetchall()}

    def clear(self):
        conn = self._get_conn()
        conn.execute("DELETE FROM knowledge")
        conn.commit()
