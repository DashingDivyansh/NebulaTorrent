from bs4 import BeautifulSoup
from typing import List
from plugins.base import BasePlugin
from models.torrent import TorrentResult
import re

class EZTVPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "EZTV"

    @property
    def version(self) -> str:
        return "1.0"

    def _parse_size(self, size_str: str) -> int:
        match = re.search(r"([\d.]+)\s*([KMGT]B)", size_str, re.IGNORECASE)
        if not match: return 0
        val, unit = match.groups()
        multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
        return int(float(val) * multipliers.get(unit.upper(), 1))

    async def search(self, query: str, category: str = None) -> List[TorrentResult]:
        if category and category.lower() not in ["tv", "shows"]:
            return []

        url = f"https://eztv.re/search/{query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        try:
            response = await self.fetch(url, headers=headers, timeout=15.0)
            if response.status_code == 404: return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', class_='forum_header_border')
            if not table: return []
            
            results = []
            rows = table.find_all('tr', class_='forum_header_border')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 5: continue
                
                title_link = cols[1].find('a')
                if not title_link: continue
                title = title_link.text
                
                magnet_link = cols[2].find('a', class_='magnet')
                if not magnet_link: continue
                magnet = magnet_link['href']
                
                size_text = cols[3].text
                size = self._parse_size(size_text)
                
                age = cols[4].text
                seeders = int(cols[5].text.replace(',', '')) if cols[5].text.strip() else 0
                
                results.append(TorrentResult(
                    title=title,
                    size=size,
                    seeders=seeders,
                    leechers=0, # EZTV often doesn't show leechers in list
                    age=age,
                    category="TV Shows",
                    source=self.name,
                    magnet=magnet
                ))
            return results
        except Exception as e:
            print(f"EZTV search failed: {e}")
            return []
