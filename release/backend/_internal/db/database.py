import sqlite3
import os
from datetime import datetime
from config import settings
from logger import logger

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
                conn.commit()
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

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

db = Database()
