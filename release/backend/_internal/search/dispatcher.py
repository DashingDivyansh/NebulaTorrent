import asyncio
import importlib.util
import os
import json
from typing import List, Type
from plugins.base import BasePlugin
from models.torrent import TorrentResult
from logger import logger

class SearchDispatcher:
    def __init__(self, plugins_dir: str):
        self.plugins_dir = plugins_dir
        self.plugins: List[BasePlugin] = []

    def load_plugins(self):
        self.plugins = []
        if not os.path.exists(self.plugins_dir):
            logger.warning(f"Plugins directory not found: {self.plugins_dir}")
            os.makedirs(self.plugins_dir, exist_ok=True)
            return

        for folder in os.listdir(self.plugins_dir):
            plugin_path = os.path.join(self.plugins_dir, folder)
            if os.path.isdir(plugin_path) and not folder.startswith("__"):
                manifest_path = os.path.join(plugin_path, "manifest.json")
                py_path = os.path.join(plugin_path, "plugin.py")

                if os.path.exists(py_path):
                    try:
                        spec = importlib.util.spec_from_file_location(f"plugin_{folder}", py_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        # Look for a class that inherits from BasePlugin
                        loaded_count = 0
                        for attr in dir(module):
                            cls = getattr(module, attr)
                            if isinstance(cls, type) and issubclass(cls, BasePlugin) and cls is not BasePlugin:
                                self.plugins.append(cls())
                                loaded_count += 1
                        
                        if loaded_count > 0:
                            logger.info(f"Loaded plugin '{folder}' ({loaded_count} classes)")
                    except Exception as e:
                        logger.error(f"Failed to load plugin {folder}: {e}")

    async def search(self, query: str, category: str = None) -> List[TorrentResult]:
        """
        Legacy batch search (internal use or non-streaming fallbacks)
        """
        tasks = [plugin.search(query, category) for plugin in self.plugins]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        raw_results = []
        for res in results:
            if isinstance(res, list):
                raw_results.extend(res)
            elif isinstance(res, Exception):
                logger.error(f"Search plugin exception: {res}")
        
        return self._deduplicate_and_rank(raw_results)

    def _get_info_hash(self, result: TorrentResult) -> str:
        if result.infoHash:
            return result.infoHash.lower()
        
        if result.magnet:
            import re
            match = re.search(r"xt=urn:btih:([a-zA-Z0-9]+)", result.magnet)
            if match:
                return match.group(1).lower()
        
        return result.title.lower()

    def _deduplicate_and_rank(self, results: List[TorrentResult]) -> List[TorrentResult]:
        unique_results = {}
        
        for res in results:
            h = self._get_info_hash(res)
            if h in unique_results:
                existing = unique_results[h]
                if res.source not in existing.source:
                    existing.source = f"{existing.source}, {res.source}"
                if res.seeders > existing.seeders:
                    existing.seeders = res.seeders
                    existing.leechers = res.leechers
            else:
                unique_results[h] = res
        
        deduped = list(unique_results.values())
        deduped.sort(key=lambda x: x.seeders, reverse=True)
        return deduped
