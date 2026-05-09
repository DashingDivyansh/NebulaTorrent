import httpx
from bs4 import BeautifulSoup
from typing import List
from plugins.base import BasePlugin
from models.torrent import TorrentResult
import re

class GloTorrentsPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "GloTorrents"

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
        url = "https://glodls.to/search_results.php"
        params = {
            "search": query,
            "sort": "seeders",
            "order": "desc"
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, headers=headers, timeout=15.0)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table', class_='ttable_headinner')
                if not table: return []
                
                results = []
                rows = table.find_all('tr')
                for row in rows:
                    if 'ttable_header' in row.get('class', []): continue
                    cols = row.find_all('td')
                    if len(cols) < 8: continue
                    
                    # Title is usually in the second or third column
                    title_col = cols[1]
                    title_link = title_col.find('a', title=True)
                    if not title_link: continue
                    title = title_link['title']
                    
                    # Magnet link is usually in a column with an icon
                    magnet_link = row.find('a', href=re.compile(r"magnet:\?"))
                    if not magnet_link: continue
                    magnet = magnet_link['href']
                    
                    size = self._parse_size(cols[4].text)
                    seeders = int(cols[5].text.replace(',', '')) if cols[5].text.strip().isdigit() else 0
                    leechers = int(cols[6].text.replace(',', '')) if cols[6].text.strip().isdigit() else 0
                    age = cols[3].text
                    
                    results.append(TorrentResult(
                        title=title,
                        size=size,
                        seeders=seeders,
                        leechers=leechers,
                        age=age,
                        category="Other",
                        source=self.name,
                        magnet=magnet
                    ))
                return results
            except Exception as e:
                print(f"GloTorrents search failed: {e}")
                return []
