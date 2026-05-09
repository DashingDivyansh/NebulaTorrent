from typing import List
from plugins.base import BasePlugin
from models.torrent import TorrentResult

class SolidTorrentsPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "SolidTorrents"

    @property
    def version(self) -> str:
        return "1.0"

    async def search(self, query: str, category: str = None) -> List[TorrentResult]:
        url = "https://solidtorrents.net/api/v1/search"
        params = {
            "q": query,
            "sort": "seeders",
        }
        if category:
            # Map NebulaTorrent categories to SolidTorrents categories
            category_map = {
                "movies": "video",
                "tv": "video",
                "anime": "video",
                "games": "software",
                "software": "software",
                "music": "audio",
                "books": "ebook"
            }
            params["category"] = category_map.get(category.lower(), "")

        try:
            response = await self.fetch(url, params=params, timeout=10.0)
            data = response.json()
            
            results = []
            for item in data.get("results", []):
                results.append(TorrentResult(
                    title=item.get("title", ""),
                    size=item.get("size", 0),
                    seeders=item.get("seeders", 0),
                    leechers=item.get("leechers", 0),
                    age=item.get("createdAt", ""), # Or format date
                    category=item.get("category", ""),
                    source=self.name,
                    magnet=item.get("magnet", ""),
                    infoHash=item.get("infoHash", "")
                ))
            return results
        except Exception as e:
            import traceback
            print(f"SolidTorrents search failed: {e}")
            traceback.print_exc()
            return []
