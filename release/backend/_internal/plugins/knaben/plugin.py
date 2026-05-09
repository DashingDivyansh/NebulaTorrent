import httpx
import xml.etree.ElementTree as ET
from typing import List
from plugins.base import BasePlugin
from models.torrent import TorrentResult
import re

class KnabenPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "Knaben"

    @property
    def version(self) -> str:
        return "1.0"

    async def search(self, query: str, category: str = None) -> List[TorrentResult]:
        url = "https://knaben.eu/rss.php"
        params = {"q": query}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=15.0)
                response.raise_for_status()
                
                root = ET.fromstring(response.text)
                results = []
                
                for item in root.findall('.//item'):
                    title = item.find('title').text if item.find('title') is not None else ""
                    magnet = item.find('link').text if item.find('link') is not None else ""
                    
                    if not magnet.startswith("magnet:?"):
                        continue
                        
                    results.append(TorrentResult(
                        title=title,
                        size=0, # Knaben RSS often lacks size
                        seeders=0,
                        leechers=0,
                        age="",
                        category="Other",
                        source=self.name,
                        magnet=magnet
                    ))
                return results
            except Exception as e:
                print(f"Knaben search failed: {e}")
                return []
