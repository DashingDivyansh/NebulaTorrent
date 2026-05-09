import sys
import os
import unittest
import asyncio
import json
import tempfile

# Add src/backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from models.torrent import TorrentResult
from search.dispatcher import SearchDispatcher
from plugins.base import BasePlugin
from plugins.sandbox import PluginSandboxError, SandboxedPlugin, audit_plugin_source


class DummyPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "Dummy"

    @property
    def version(self) -> str:
        return "1.0"

    async def search(self, query: str, category: str = None):
        return [
            TorrentResult(
                title=f"{query} result",
                size=1000,
                seeders=12,
                leechers=1,
                age="today",
                category=category or "Other",
                source=self.name,
                magnet="magnet:?xt=urn:btih:dummyhash",
                infoHash="dummyhash",
            )
        ]

class TestSearchDispatcher(unittest.TestCase):
    def setUp(self):
        self.dispatcher = SearchDispatcher(plugins_dir="non_existent")

    def test_deduplication_by_infohash(self):
        results = [
            TorrentResult(
                title="Torrent 1",
                size=1000,
                seeders=10,
                leechers=5,
                age="today",
                category="Movies",
                source="Source A",
                magnet="magnet:?xt=urn:btih:hash1",
                infoHash="hash1"
            ),
            TorrentResult(
                title="Torrent 1 Duplicate",
                size=1000,
                seeders=20,
                leechers=10,
                age="yesterday",
                category="Movies",
                source="Source B",
                magnet="magnet:?xt=urn:btih:hash1",
                infoHash="hash1"
            )
        ]
        
        deduped = self.dispatcher._deduplicate_and_rank(results)
        
        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0].seeders, 20)
        self.assertIn("Source A", deduped[0].source)
        self.assertIn("Source B", deduped[0].source)

    def test_deduplication_by_magnet_extraction(self):
        results = [
            TorrentResult(
                title="Torrent 2",
                size=500,
                seeders=5,
                leechers=2,
                age="today",
                category="Games",
                source="Source A",
                magnet="magnet:?xt=urn:btih:hash2&dn=test",
                infoHash=None
            ),
            TorrentResult(
                title="Torrent 2 Clone",
                size=500,
                seeders=2,
                leechers=1,
                age="today",
                category="Games",
                source="Source C",
                magnet="magnet:?xt=urn:btih:hash2",
                infoHash=None
            )
        ]
        
        deduped = self.dispatcher._deduplicate_and_rank(results)
        self.assertEqual(len(deduped), 1)
        self.assertEqual(deduped[0].seeders, 5)

    def test_ranking_by_seeders(self):
        results = [
            TorrentResult(title="Low", size=10, seeders=1, leechers=0, age="old", category="X", source="A", magnet="m1"),
            TorrentResult(title="High", size=10, seeders=100, leechers=0, age="new", category="X", source="B", magnet="m2"),
            TorrentResult(title="Mid", size=10, seeders=50, leechers=0, age="mid", category="X", source="C", magnet="m3")
        ]
        
        ranked = self.dispatcher._deduplicate_and_rank(results)
        self.assertEqual(ranked[0].title, "High")
        self.assertEqual(ranked[1].title, "Mid")
        self.assertEqual(ranked[2].title, "Low")

    def test_stream_search_emits_status_results_and_done(self):
        self.dispatcher.plugins = [DummyPlugin()]
        events = asyncio.run(self._collect_stream())
        event_types = [event["type"] for event in events]

        self.assertIn("plugin_status", event_types)
        self.assertIn("results", event_types)
        self.assertEqual(event_types[-1], "done")

    async def _collect_stream(self):
        events = []
        async for event in self.dispatcher.stream_search("ubuntu", "software"):
            events.append(event)
        return events

    def test_sandboxed_plugin_executes_in_subprocess(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin_dir = os.path.join(tmp, "dummy")
            os.makedirs(plugin_dir)
            with open(os.path.join(plugin_dir, "manifest.json"), "w", encoding="utf-8") as f:
                json.dump({"name": "SandboxDummy", "version": "1.0"}, f)
            with open(os.path.join(plugin_dir, "plugin.py"), "w", encoding="utf-8") as f:
                f.write(
                    "from plugins.base import BasePlugin\n"
                    "from models.torrent import TorrentResult\n"
                    "class SandboxDummy(BasePlugin):\n"
                    "    @property\n"
                    "    def name(self): return 'SandboxDummy'\n"
                    "    @property\n"
                    "    def version(self): return '1.0'\n"
                    "    async def search(self, query, category=None):\n"
                    "        return [TorrentResult(title=query, size=1, seeders=1, leechers=0, age='now', category=category or 'Other', source=self.name, magnet='magnet:?xt=urn:btih:safe', infoHash='safe')]\n"
                )

            plugin = SandboxedPlugin(plugin_dir, {"name": "SandboxDummy", "version": "1.0"})
            results = asyncio.run(plugin.search("ubuntu", "software"))

            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].title, "ubuntu")

    def test_sandbox_audit_rejects_unsafe_imports(self):
        with tempfile.TemporaryDirectory() as tmp:
            plugin_file = os.path.join(tmp, "plugin.py")
            with open(plugin_file, "w", encoding="utf-8") as f:
                f.write("import os\n")

            with self.assertRaises(PluginSandboxError):
                audit_plugin_source(plugin_file)

if __name__ == '__main__':
    unittest.main()
