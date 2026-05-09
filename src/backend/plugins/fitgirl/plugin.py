from bs4 import BeautifulSoup
from typing import List
from plugins.base import BasePlugin
from models.torrent import TorrentResult
import re

class FitGirlPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "FitGirl"

    @property
    def version(self) -> str:
        return "1.0"

    async def search(self, query: str, category: str = None) -> List[TorrentResult]:
        if category and category.lower() not in ["games", "software"]:
            return []

        url = "https://fitgirl-repacks.site/"
        params = {"s": query}
        headers = {"User-Agent": "Mozilla/5.0"}
        
        try:
            response = await self.fetch(url, params=params, headers=headers, timeout=15.0)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('article')
            
            results = []
            for article in articles:
                title_tag = article.find('h1', class_='entry-title')
                if not title_tag: continue
                title = title_tag.text.strip()
                
                # Get link to the post
                link_tag = title_tag.find('a')
                if not link_tag: continue
                post_url = link_tag['href']
                
                # Extract date
                date_tag = article.find('time', class_='entry-date')
                age = date_tag.text.strip() if date_tag else ""
                
                results.append(TorrentResult(
                    title=title,
                    size=0, # Need to visit post for size
                    seeders=0,
                    leechers=0,
                    age=age,
                    category="Games",
                    source=self.name,
                    magnet=post_url # Using post URL as magnet for now, user can visit
                ))
            
            return results
        except Exception as e:
            print(f"FitGirl search failed: {e}")
            return []
