import asyncio
import importlib.util
import os
import json
import time
from dataclasses import dataclass, field
from typing import AsyncIterator, List
from plugins.base import BasePlugin
from plugins.sandbox import SandboxedPlugin, audit_plugin_source
from models.torrent import TorrentResult
from ranking import deduplicate_and_rank
from config import settings
from logger import logger


@dataclass
class PluginState:
    failures: int = 0
    degraded_until: float = 0.0
    last_error: str | None = None
    status: str = "idle"
    semaphore: asyncio.Semaphore = field(default_factory=lambda: asyncio.Semaphore(settings.PLUGIN_DEFAULT_RATE_LIMIT))


class SearchDispatcher:
    def __init__(self, plugins_dir: str):
        self.plugins_dir = plugins_dir
        self.plugins: List[BasePlugin] = []
        self.plugin_meta: dict[str, dict] = {}
        self.plugin_state: dict[str, PluginState] = {}

    def load_plugins(self):
        self.plugins = []
        self.plugin_meta = {}
        self.plugin_state = {}
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
                        manifest = {}
                        if os.path.exists(manifest_path):
                            with open(manifest_path, "r", encoding="utf-8") as f:
                                manifest = json.load(f)

                        if settings.PLUGIN_SANDBOX_ENABLED:
                            audit_plugin_source(py_path)
                            plugin = SandboxedPlugin(plugin_path, manifest)
                            self.plugins.append(plugin)
                            self.plugin_meta[plugin.name] = manifest
                            rate_limit = int(manifest.get("rate_limit", settings.PLUGIN_DEFAULT_RATE_LIMIT) or 1)
                            self.plugin_state[plugin.name] = PluginState(
                                semaphore=asyncio.Semaphore(max(rate_limit, 1))
                            )
                            logger.info(f"Loaded sandboxed plugin '{folder}' as '{plugin.name}'")
                            continue

                        spec = importlib.util.spec_from_file_location(f"plugin_{folder}", py_path)
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)

                        # Look for a class that inherits from BasePlugin
                        loaded_count = 0
                        for attr in dir(module):
                            cls = getattr(module, attr)
                            if isinstance(cls, type) and issubclass(cls, BasePlugin) and cls is not BasePlugin:
                                plugin = cls()
                                self.plugins.append(plugin)
                                self.plugin_meta[plugin.name] = manifest
                                rate_limit = int(manifest.get("rate_limit", settings.PLUGIN_DEFAULT_RATE_LIMIT) or 1)
                                self.plugin_state[plugin.name] = PluginState(
                                    semaphore=asyncio.Semaphore(max(rate_limit, 1))
                                )
                                loaded_count += 1

                        if loaded_count > 0:
                            logger.info(f"Loaded plugin '{folder}' ({loaded_count} classes)")
                    except Exception as e:
                        logger.error(f"Failed to load plugin {folder}: {e}")

    async def search(self, query: str, category: str = None) -> List[TorrentResult]:
        raw_results = []
        async for event in self.stream_search(query, category):
            if event["type"] == "results":
                raw_results.extend(TorrentResult(**item) for item in event["results"])
        return deduplicate_and_rank(raw_results, query)

    async def stream_search(self, query: str, category: str = None) -> AsyncIterator[dict]:
        from db.database import db

        tasks: dict[asyncio.Task, BasePlugin] = {}

        try:
            for plugin in self.plugins:
                state = self.plugin_state.setdefault(plugin.name, PluginState())
                if state.degraded_until > time.time():
                    yield {
                        "type": "plugin_status",
                        "plugin": plugin.name,
                        "status": "degraded",
                        "message": state.last_error or "Temporarily disabled after repeated failures",
                    }
                    continue

                cached = db.get_cached_results(query, plugin.name, category=category)
                if cached:
                    fresh = deduplicate_and_rank(cached, query)
                    yield {
                        "type": "results",
                        "plugin": plugin.name,
                        "cached": True,
                        "results": [r.model_dump() for r in fresh],
                    }
                    yield {"type": "plugin_status", "plugin": plugin.name, "status": "cached"}
                    continue

                yield {"type": "plugin_status", "plugin": plugin.name, "status": "loading"}
                tasks[asyncio.create_task(self._run_plugin(plugin, query, category))] = plugin

            while tasks:
                done, _pending = await asyncio.wait(tasks.keys(), return_when=asyncio.FIRST_COMPLETED)
                for task in done:
                    plugin = tasks.pop(task)
                    try:
                        results = await task
                        db.set_cached_results(query, plugin.name, results, category=category)
                        fresh = deduplicate_and_rank(results, query)
                        yield {
                            "type": "results",
                            "plugin": plugin.name,
                            "cached": False,
                            "results": [r.model_dump() for r in fresh],
                        }
                        yield {"type": "plugin_status", "plugin": plugin.name, "status": "healthy"}
                    except asyncio.CancelledError:
                        raise
                    except Exception as e:
                        message = str(e)
                        logger.error(f"{plugin.name} search failed: {message}")
                        yield {
                            "type": "plugin_status",
                            "plugin": plugin.name,
                            "status": "error",
                            "message": message,
                        }

            yield {"type": "done"}
        finally:
            for task in tasks:
                task.cancel()

    async def _run_plugin(self, plugin: BasePlugin, query: str, category: str = None) -> List[TorrentResult]:
        state = self.plugin_state.setdefault(plugin.name, PluginState())
        async with state.semaphore:
            state.status = "loading"
            last_error: Exception | None = None
            for attempt in range(settings.PLUGIN_RETRIES + 1):
                try:
                    results = await asyncio.wait_for(
                        plugin.search(query, category),
                        timeout=settings.PLUGIN_TIMEOUT,
                    )
                    state.failures = 0
                    state.last_error = None
                    state.status = "healthy"
                    return results or []
                except Exception as e:
                    last_error = e
                    if attempt < settings.PLUGIN_RETRIES:
                        await asyncio.sleep(settings.PLUGIN_RETRY_BASE_DELAY * (2 ** attempt))

            state.failures += 1
            state.last_error = str(last_error)
            state.status = "error"
            if state.failures >= settings.CIRCUIT_BREAKER_FAILURES:
                state.status = "degraded"
                state.degraded_until = time.time() + settings.CIRCUIT_BREAKER_COOLDOWN_SECONDS
            raise last_error or RuntimeError(f"{plugin.name} failed")

    def _deduplicate_and_rank(self, results: List[TorrentResult], query: str = "") -> List[TorrentResult]:
        return deduplicate_and_rank(results, query)

    def plugin_health(self) -> list[dict]:
        health = []
        for plugin in self.plugins:
            state = self.plugin_state.setdefault(plugin.name, PluginState())
            if state.degraded_until and state.degraded_until <= time.time():
                state.degraded_until = 0.0
                state.status = "idle"
            health.append(
                {
                    "name": plugin.name,
                    "version": plugin.version,
                    "status": "degraded" if state.degraded_until > time.time() else state.status,
                    "failures": state.failures,
                    "lastError": state.last_error,
                    "degradedUntil": state.degraded_until or None,
                    "rateLimit": self.plugin_meta.get(plugin.name, {}).get("rate_limit", settings.PLUGIN_DEFAULT_RATE_LIMIT),
                    "sandboxed": isinstance(plugin, SandboxedPlugin),
                }
            )
        return health
