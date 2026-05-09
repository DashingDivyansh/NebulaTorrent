from typing import List

from models.torrent import TorrentResult
from plugins.base import BasePlugin


class KnabenPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "Knaben"

    @property
    def version(self) -> str:
        return "2.0"

    async def search(self, query: str, category: str = None) -> List[TorrentResult]:
        payload = {
            "query": query,
            "search_field": "title",
            "search_type": "score",
            "order_by": "seeders",
            "order_direction": "desc",
            "hide_unsafe": True,
            "hide_xxx": True,
            "size": 75,
        }

        try:
            response = await self.post_json("https://api.knaben.org/v1", payload, timeout=15.0)
            data = response.json()
            hits = data.get("hits", []) if isinstance(data, dict) else []

            results = []
            for item in hits:
                magnet = item.get("magnetUrl") or ""
                info_hash = item.get("hash") or ""
                if not magnet and info_hash:
                    magnet = f"magnet:?xt=urn:btih:{info_hash}"
                if not magnet:
                    continue

                tracker = item.get("tracker") or item.get("cachedOrigin") or self.name
                results.append(
                    TorrentResult(
                        title=item.get("title", ""),
                        size=int(item.get("bytes") or 0),
                        seeders=int(item.get("seeders") or 0),
                        leechers=int(item.get("peers") or 0),
                        age=item.get("date") or item.get("lastSeen") or "",
                        category=item.get("category") or category or "Other",
                        source=f"{self.name}/{tracker}",
                        magnet=magnet,
                        infoHash=info_hash or None,
                    )
                )
            return results
        except Exception as e:
            print(f"Knaben API search failed: {e}")
            return []
