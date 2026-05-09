import httpx
import xml.etree.ElementTree as ET
from typing import List
from plugins.base import BasePlugin
from models.torrent import TorrentResult
import re

class TorrentGalaxyPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "TorrentGalaxy"

    @property
    def version(self) -> str:
        return "1.0"

    def _parse_size(self, size_str: str) -> int:
        if not size_str: return 0
        match = re.search(r"Size:\s*([\d.]+)\s*([KMGT]B)", size_str, re.IGNORECASE)
        if not match:
            return 0
        value, unit = match.groups()
        value = float(value)
        unit = unit.upper()
        multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
        return int(value * multipliers.get(unit, 1))

    async def search(self, query: str, category: str = None) -> List[TorrentResult]:
        url = "https://torrentgalaxy.to/rss.php"
        params = {"search": query}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                
                root = ET.fromstring(response.text)
                results = []
                
                for item in root.findall('.//item'):
                    title = item.find('title').text if item.find('title') is not None else ""
                    # TG RSS description often contains Size, Seeders, Leechers
                    description = item.find('description').text if item.find('description') is not None else ""
                    link = item.find('link').text if item.find('link') is not None else ""
                    
                    # Try to find magnet in the link or description
                    magnet = ""
                    if "magnet:?" in link:
                        magnet = link
                    
                    # Extract seeders/leechers from description if available
                    seeders = 0
                    leechers = 0
                    s_match = re.search(r"Seeders:\s*(\d+)", description)
                    l_match = re.search(r"Leechers:\s*(\d+)", description)
                    if s_match: seeders = int(s_match.group(1))
                    if l_match: leechers = int(l_match.group(1))
                    
                    size = self._parse_size(description)
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""

                    if not magnet and item.find('guid') is not None:
                        # Sometimes guid is the page, we might need to scrape or it might be a direct link
                        pass

                    # Note: TG RSS doesn't always have magnets directly. 
                    # If magnet is missing, this plugin is less useful.
                    # Let's try to find if there's a better TG RSS or use scraping.
                    
                    if magnet:
                        results.append(TorrentResult(
                            title=title,
                            size=size,
                            seeders=seeders,
                            leechers=leechers,
                            age=pub_date,
                            category="Other",
                            source=self.name,
                            magnet=magnet
                        ))
                return results
            except Exception as e:
                print(f"TorrentGalaxy search failed: {e}")
                return []
