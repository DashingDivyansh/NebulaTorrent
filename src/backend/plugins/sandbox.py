import ast
import asyncio
import json
import os
import sys
from dataclasses import dataclass
from typing import List

from config import settings
from models.torrent import TorrentResult
from plugins.base import BasePlugin


class PluginSandboxError(RuntimeError):
    pass


UNSAFE_IMPORT_ROOTS = {
    "ctypes",
    "multiprocessing",
    "os",
    "pathlib",
    "pickle",
    "runpy",
    "shutil",
    "socket",
    "subprocess",
    "sys",
}

UNSAFE_CALLS = {
    "__import__",
    "compile",
    "eval",
    "exec",
    "globals",
    "input",
    "locals",
    "open",
}


def audit_plugin_source(plugin_file: str):
    with open(plugin_file, "r", encoding="utf-8") as source_file:
        tree = ast.parse(source_file.read(), filename=plugin_file)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in UNSAFE_IMPORT_ROOTS:
                    raise PluginSandboxError(f"Unsafe import blocked: {alias.name}")

        if isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".", 1)[0]
            if root in UNSAFE_IMPORT_ROOTS:
                raise PluginSandboxError(f"Unsafe import blocked: {node.module}")

        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id in UNSAFE_CALLS:
                raise PluginSandboxError(f"Unsafe call blocked: {func.id}")

            if isinstance(func, ast.Attribute) and func.attr in {"system", "popen", "remove", "unlink", "rmdir"}:
                raise PluginSandboxError(f"Unsafe attribute call blocked: {func.attr}")


@dataclass
class SandboxedPlugin(BasePlugin):
    plugin_dir: str
    manifest: dict

    @property
    def name(self) -> str:
        return self.manifest.get("name") or os.path.basename(self.plugin_dir)

    @property
    def version(self) -> str:
        return self.manifest.get("version", "unknown")

    async def search(self, query: str, category: str = None) -> List[TorrentResult]:
        plugin_file = os.path.join(self.plugin_dir, "plugin.py")
        audit_plugin_source(plugin_file)

        runner = os.path.join(os.path.dirname(__file__), "sandbox_runner.py")
        timeout = settings.PLUGIN_TIMEOUT + settings.PLUGIN_SANDBOX_PROCESS_GRACE_SECONDS
        payload = {
            "plugin_dir": self.plugin_dir,
            "query": query,
            "category": category,
            "timeout": settings.PLUGIN_TIMEOUT,
            "max_results": settings.PLUGIN_SANDBOX_MAX_RESULTS,
        }

        process = await asyncio.create_subprocess_exec(
            sys.executable,
            runner,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.path.dirname(os.path.dirname(__file__)),
            env=self._sandbox_env(),
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(json.dumps(payload).encode("utf-8")),
                timeout=timeout,
            )
        except asyncio.TimeoutError as e:
            process.kill()
            await process.communicate()
            raise PluginSandboxError(f"{self.name} sandbox timed out") from e

        if process.returncode != 0:
            message = stderr.decode("utf-8", errors="replace").strip() or "Sandbox process failed"
            raise PluginSandboxError(message)

        try:
            response = json.loads(stdout.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise PluginSandboxError(f"{self.name} returned invalid sandbox JSON") from e

        if response.get("error"):
            raise PluginSandboxError(str(response["error"]))

        return [TorrentResult(**item) for item in response.get("results", [])]

    def _sandbox_env(self) -> dict[str, str]:
        allowed_keys = {
            "PATH",
            "SYSTEMROOT",
            "WINDIR",
            "TEMP",
            "TMP",
            "LOCALAPPDATA",
            "APPDATA",
            "PYTHONPATH",
            "PROXY_URL",
            "PROXY_FALLBACK",
        }
        env = {key: value for key, value in os.environ.items() if key.upper() in allowed_keys}
        env["PYTHONUNBUFFERED"] = "1"
        env["NEBULA_PLUGIN_SANDBOX"] = "1"
        return env
