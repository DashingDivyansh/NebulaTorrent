import sqlite3
import os
import hashlib
import json
from datetime import datetime
from typing import List, Optional
from config import settings
from logger import logger
from models.torrent import TorrentResult

class Database:
    def __init__(self, db_path=None):
        self.db_path = db_path or settings.DB_PATH
        self._init_db()

    def _init_db(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS search_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query TEXT NOT NULL,
                        category TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS saved_searches (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query TEXT NOT NULL,
                        category TEXT,
                        filters TEXT
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS result_cache (
                        query_hash TEXT NOT NULL,
                        plugin_name TEXT NOT NULL,
                        page INTEGER NOT NULL DEFAULT 1,
                        results_json TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (query_hash, plugin_name, page)
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    def make_query_hash(self, query: str, category: str = None) -> str:
        payload = json.dumps(
            {"query": query.strip().lower(), "category": (category or "").strip().lower()},
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def add_search_history(self, query: str, category: str = None):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO search_history (query, category) VALUES (?, ?)",
                    (query, category)
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to add search history: {e}")

    def get_search_history(self, limit=10):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT query, category, timestamp FROM search_history ORDER BY id DESC LIMIT ?",
                    (limit,)
                )
                return [{"query": r[0], "category": r[1], "timestamp": r[2]} for r in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to fetch search history: {e}")
            return []

    def get_cached_results(
        self,
        query: str,
        plugin_name: str,
        category: str = None,
        page: int = 1,
        ttl_seconds: Optional[int] = None,
    ) -> List[TorrentResult]:
        ttl = ttl_seconds if ttl_seconds is not None else settings.CACHE_TTL_SECONDS
        query_hash = self.make_query_hash(query, category)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT results_json
                    FROM result_cache
                    WHERE query_hash = ?
                      AND plugin_name = ?
                      AND page = ?
                      AND created_at >= datetime('now', ?)
                    """,
                    (query_hash, plugin_name, page, f"-{ttl} seconds"),
                )
                row = cursor.fetchone()
                if not row:
                    return []
                return [TorrentResult(**item) for item in json.loads(row[0])]
        except Exception as e:
            logger.error(f"Failed to read result cache for {plugin_name}: {e}")
            return []

    def set_cached_results(
        self,
        query: str,
        plugin_name: str,
        results: List[TorrentResult],
        category: str = None,
        page: int = 1,
    ):
        query_hash = self.make_query_hash(query, category)
        try:
            payload = json.dumps([r.model_dump() for r in results])
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO result_cache
                        (query_hash, plugin_name, page, results_json, created_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (query_hash, plugin_name, page, payload),
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to write result cache for {plugin_name}: {e}")

db = Database()
