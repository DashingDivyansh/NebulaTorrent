import httpx
import xml.etree.ElementTree as ET
from typing import List
from plugins.base import BasePlugin
from models.torrent import TorrentResult
import re

class NyaaPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "Nyaa"

    @property
    def version(self) -> str:
        return "1.0"

    def _parse_size(self, size_str: str) -> int:
        match = re.match(r"([\d.]+)\s*([KMGT]i?B)", size_str, re.IGNORECASE)
        if not match:
            return 0
        value, unit = match.groups()
        value = float(value)
        unit = unit.upper()
        
        multipliers = {
            'B': 1,
            'KB': 1024,
            'KIB': 1024,
            'MB': 1024**2,
            'MIB': 1024**2,
            'GB': 1024**3,
            'GIB': 1024**3,
            'TB': 1024**4,
            'TIB': 1024**4,
        }
        return int(value * multipliers.get(unit, 1))

    async def search(self, query: str, category: str = None) -> List[TorrentResult]:
        # Only search Nyaa if category is anime or no category specified
        if category and category.lower() != "anime":
            return []

        url = "https://nyaa.si/"
        params = {
            "page": "rss",
            "q": query,
            "c": "0_0", # All categories
            "f": "0"    # No filter
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                
                root = ET.fromstring(response.text)
                results = []
                
                # Nyaa uses custom namespace
                ns = {'nyaa': 'https://nyaa.si/xmlns/nyaa'}
                
                for item in root.findall('.//item'):
                    title = item.find('title').text if item.find('title') is not None else ""
                    magnet = item.find('link').text if item.find('link') is not None else ""
                    
                    # Custom tags
                    seeders = int(item.find('nyaa:seeders', ns).text) if item.find('nyaa:seeders', ns) is not None else 0
                    leechers = int(item.find('nyaa:leechers', ns).text) if item.find('nyaa:leechers', ns) is not None else 0
                    size_str = item.find('nyaa:size', ns).text if item.find('nyaa:size', ns) is not None else "0 B"
                    info_hash = item.find('nyaa:infoHash', ns).text if item.find('nyaa:infoHash', ns) is not None else ""
                    cat = item.find('nyaa:category', ns).text if item.find('nyaa:category', ns) is not None else "Anime"
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""

                    results.append(TorrentResult(
                        title=title,
                        size=self._parse_size(size_str),
                        seeders=seeders,
                        leechers=leechers,
                        age=pub_date,
                        category=cat,
                        source=self.name,
                        magnet=magnet,
                        infoHash=info_hash
                    ))
                return results
            except Exception as e:
                import traceback
                print(f"Nyaa search failed: {e}")
                traceback.print_exc()
                return []
