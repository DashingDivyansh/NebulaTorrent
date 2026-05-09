import xml.etree.ElementTree as ET
from typing import List
from plugins.base import BasePlugin
from models.torrent import TorrentResult
import re

class LimeTorrentsPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "LimeTorrents"

    @property
    def version(self) -> str:
        return "1.0"

    def _parse_size(self, size_str: str) -> int:
        if not size_str: return 0
        # LimeTorrents RSS often has size in the title or a custom tag
        match = re.search(r"Size:\s*([\d.]+)\s*([KMGT]B)", size_str, re.IGNORECASE)
        if not match: return 0
        val, unit = match.groups()
        multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
        return int(float(val) * multipliers.get(unit.upper(), 1))

    async def search(self, query: str, category: str = None) -> List[TorrentResult]:
        # LimeTorrents RSS search URL
        url = f"https://www.limetorrents.info/search/rss/{query}/"
        
        try:
            response = await self.fetch(url, timeout=15.0)
            
            root = ET.fromstring(response.text)
            results = []
            
            for item in root.findall('.//item'):
                title = item.find('title').text if item.find('title') is not None else ""
                link = item.find('link').text if item.find('link') is not None else ""
                
                # LimeTorrents RSS sometimes puts the magnet link in the <enclosure> or <link>
                # If it's a torrent file link, we can't easily use it as a magnet without downloading
                # But often they provide magnet:? links
                
                magnet = ""
                if "magnet:?" in link:
                    magnet = link
                
                # Extract info from description
                description = item.find('description').text if item.find('description') is not None else ""
                
                # Seeders/Leechers extraction
                seeders = 0
                leechers = 0
                s_match = re.search(r"Seeders:\s*(\d+)", description)
                l_match = re.search(r"Leechers:\s*(\d+)", description)
                if s_match: seeders = int(s_match.group(1))
                if l_match: leechers = int(l_match.group(1))
                
                size = self._parse_size(description)
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""

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
            print(f"LimeTorrents search failed: {e}")
            return []
