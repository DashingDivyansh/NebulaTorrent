import httpx
from typing import List
from plugins.base import BasePlugin
from models.torrent import TorrentResult

class TPBPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "ThePirateBay"

    @property
    def version(self) -> str:
        return "1.0"

    async def search(self, query: str, category: str = None) -> List[TorrentResult]:
        # TPB API uses category IDs
        # 200: Video, 300: Applications, 100: Audio, 400: Games
        cat_id = 0
        if category:
            cat_map = {
                "movies": 200,
                "tv": 200,
                "games": 400,
                "software": 300,
                "music": 100,
            }
            cat_id = cat_map.get(category.lower(), 0)

        url = "https://apibay.org/q.php"
        params = {
            "q": query,
            "cat": cat_id
        }

        async with httpx.AsyncClient() as client:
            try:
                # Using a slightly longer timeout and trying a different indexer
                response = await client.get(url, params=params, timeout=15.0)
                response.raise_for_status()
                data = response.json()
                
                if not isinstance(data, list):
                    return []

                results = []
                for item in data:
                    if item.get("id") == "0": # No results found
                        continue
                        
                    results.append(TorrentResult(
                        title=item.get("name", ""),
                        size=int(item.get("size", 0)),
                        seeders=int(item.get("seeders", 0)),
                        leechers=int(item.get("leechers", 0)),
                        age=item.get("added", ""),
                        category=category or "Other",
                        source=self.name,
                        magnet=f"magnet:?xt=urn:btih:{item.get('info_hash')}&dn={item.get('name')}",
                        infoHash=item.get("info_hash")
                    ))
                return results
            except Exception as e:
                print(f"TPB search failed: {e}")
                return []
