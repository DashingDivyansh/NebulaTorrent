import sys
import os
import unittest
import sqlite3

# Add src/backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from db.database import Database
from models.torrent import TorrentResult

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.test_db_path = "test_nebula.db"
        self.db = Database(self.test_db_path)

    def tearDown(self):
        # On Windows, we might need to be careful with file handles
        pass

    def test_search_history(self):
        # Use a fresh ID sequence by creating a new DB instance if needed, 
        # or just check if the most recent is correct.
        self.db.add_search_history("ubuntu", "software")
        import time
        time.sleep(0.1) # Ensure distinct timestamps if using timestamp sort, though we switched to ID
        self.db.add_search_history("debian", "software")
        
        history = self.db.get_search_history(limit=5)
        self.assertTrue(len(history) >= 2)
        # The most recent should be at index 0
        self.assertEqual(history[0]['query'], "debian")

    def test_result_cache_roundtrip(self):
        result = TorrentResult(
            title="Ubuntu ISO",
            size=1024,
            seeders=25,
            leechers=3,
            age="today",
            category="software",
            source="Dummy",
            magnet="magnet:?xt=urn:btih:ubuntu",
            infoHash="ubuntu",
        )

        self.db.set_cached_results("ubuntu", "Dummy", [result], category="software")
        cached = self.db.get_cached_results("ubuntu", "Dummy", category="software")

        self.assertEqual(len(cached), 1)
        self.assertEqual(cached[0].title, "Ubuntu ISO")

if __name__ == '__main__':
    unittest.main()
