from bs4 import BeautifulSoup
from typing import List
from plugins.base import BasePlugin
from models.torrent import TorrentResult
import re

class BTDiggPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "BTDigg"

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
        url = "https://btdig.com/search"
        params = {"q": query}
        headers = {"User-Agent": "Mozilla/5.0"}
        
        try:
            response = await self.fetch(url, params=params, headers=headers, timeout=15.0)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            divs = soup.find_all('div', class_='one_result')
            
            results = []
            for div in divs:
                title_div = div.find('div', class_='torrent_name')
                if not title_div: continue
                title = title_div.text.strip()
                
                magnet_link = div.find('a', href=re.compile(r"magnet:\?"))
                if not magnet_link: continue
                magnet = magnet_link['href']
                
                attr_div = div.find('div', class_='torrent_attr')
                size = 0
                age = ""
                if attr_div:
                    attrs = attr_div.find_all('span', class_='attr_val')
                    if len(attrs) > 0:
                        size = self._parse_size(attrs[0].text)
                    if len(attrs) > 1:
                        age = attrs[1].text
                        
                results.append(TorrentResult(
                    title=title,
                    size=size,
                    seeders=0, # BTDigg is DHT based, often lacks seeds in list
                    leechers=0,
                    age=age,
                    category="Other",
                    source=self.name,
                    magnet=magnet
                ))
            return results
        except Exception as e:
            print(f"BTDigg search failed: {e}")
            return []
