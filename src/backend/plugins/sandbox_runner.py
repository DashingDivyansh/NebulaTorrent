import asyncio
import builtins
import importlib.util
import json
import os
import sys
from contextlib import redirect_stdout
from io import StringIO

BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from models.torrent import TorrentResult
from plugins.base import BasePlugin


def _install_runtime_guards(plugin_dir: str):
    real_open = builtins.open

    def guarded_open(file, mode="r", *args, **kwargs):
        write_mode = any(flag in mode for flag in ("w", "a", "+", "x"))
        if write_mode:
            raise PermissionError("Plugin sandbox blocks file writes")
        return real_open(file, mode, *args, **kwargs)

    builtins.open = guarded_open


async def _run():
    payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    plugin_dir = os.path.abspath(payload["plugin_dir"])
    plugin_file = os.path.join(plugin_dir, "plugin.py")
    query = payload["query"]
    category = payload.get("category")
    timeout = float(payload.get("timeout", 10.0))
    max_results = int(payload.get("max_results", 500))

    spec = importlib.util.spec_from_file_location("sandboxed_plugin", plugin_file)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load plugin spec")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _install_runtime_guards(plugin_dir)

    plugin = None
    for attr in dir(module):
        candidate = getattr(module, attr)
        if isinstance(candidate, type) and issubclass(candidate, BasePlugin) and candidate is not BasePlugin:
            plugin = candidate()
            break

    if plugin is None:
        raise RuntimeError("No BasePlugin subclass found")

    results = await asyncio.wait_for(plugin.search(query, category), timeout=timeout)
    safe_results = []
    for item in (results or [])[:max_results]:
        if isinstance(item, TorrentResult):
            safe_results.append(item.model_dump())
        elif isinstance(item, dict):
            safe_results.append(TorrentResult(**item).model_dump())

    return {"results": safe_results}


def main():
    try:
        captured_stdout = StringIO()
        with redirect_stdout(captured_stdout):
            response = asyncio.run(_run())
        print(json.dumps(response), flush=True)
    except Exception as e:
        print(json.dumps({"error": str(e)}), flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
