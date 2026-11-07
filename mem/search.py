"""Derived full-text index. Rebuilt from the log, never committed."""
import re
import sqlite3

from .core import fold, in_scope


class Index:
    def __init__(self, events, project=None, instance=None):
        self.db = sqlite3.connect(":memory:")
        self.db.execute(
            "CREATE VIRTUAL TABLE p USING fts5(id UNINDEXED, key, body, "
            "tokenize='unicode61 remove_diacritics 2')"
        )
        active, _ = fold(events)
        self.db.executemany(
            "INSERT INTO p VALUES (?,?,?)",
            [(e["id"], e.get("key") or "", e["body"]) for e in active
             if in_scope(e, project, instance)],
        )

    def search(self, query, k=5):
        words = re.findall(r"\w+", query.lower())
        if not words:
            return []
        match = " OR ".join(f'"{w}"' for w in words)
        rows = self.db.execute(
            "SELECT id FROM p WHERE p MATCH ? ORDER BY bm25(p) LIMIT ?", (match, k)
        )
        return [r[0] for r in rows]
