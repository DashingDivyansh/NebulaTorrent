import httpx
import itertools
from abc import ABC, abstractmethod
from typing import List
from models.torrent import TorrentResult
from config import settings

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
]

_USER_AGENT_ROTATION = itertools.cycle(USER_AGENTS)


class BasePlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @abstractmethod
    async def search(self, query: str, category: str = None) -> List[TorrentResult]:
        pass

    def get_client(self, use_proxy: bool = True, **kwargs) -> httpx.AsyncClient:
        """
        Returns an httpx.AsyncClient configured with the global proxy if set and use_proxy is True.
        """
        if 'follow_redirects' not in kwargs:
            kwargs['follow_redirects'] = True

        headers = dict(kwargs.pop("headers", {}) or {})
        headers.setdefault("User-Agent", next(_USER_AGENT_ROTATION))
        headers.setdefault("Accept", "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8")
        kwargs["headers"] = headers
            
        if use_proxy and settings.PROXY_URL:
            kwargs['proxy'] = settings.PROXY_URL
            
        return httpx.AsyncClient(**kwargs)

    async def fetch(self, url: str, params: dict = None, timeout: float = 10.0, **kwargs):
        """
        Helper method to fetch data with optional proxy fallback.
        """
        # Try with proxy first if configured
        if settings.PROXY_URL:
            try:
                async with self.get_client(use_proxy=True, **kwargs) as client:
                    response = await client.get(url, params=params, timeout=timeout)
                    response.raise_for_status()
                    return response
            except Exception as e:
                if not settings.PROXY_FALLBACK:
                    raise e
                print(f"Proxy failed for {self.name}, trying direct connection: {e}")

        # Fallback to direct or try direct if no proxy
        async with self.get_client(use_proxy=False, **kwargs) as client:
            response = await client.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response

    async def post_json(self, url: str, payload: dict, timeout: float = 10.0, **kwargs):
        if settings.PROXY_URL:
            try:
                async with self.get_client(use_proxy=True, **kwargs) as client:
                    response = await client.post(url, json=payload, timeout=timeout)
                    response.raise_for_status()
                    return response
            except Exception as e:
                if not settings.PROXY_FALLBACK:
                    raise e
                print(f"Proxy failed for {self.name}, trying direct connection: {e}")

        async with self.get_client(use_proxy=False, **kwargs) as client:
            response = await client.post(url, json=payload, timeout=timeout)
            response.raise_for_status()
            return response
