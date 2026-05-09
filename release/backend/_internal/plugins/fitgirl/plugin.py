import httpx
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
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, headers=headers, timeout=15.0)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.find_all('article')
                
                results = []
                for article in articles:
                    title_tag = article.find('h1', class_='entry-title')
                    if not title_tag: continue
                    title = title_tag.text.strip()
                    
                    # FitGirl usually doesn't provide magnets on the search page.
                    # This plugin might need to visit the page.
                    # For now, let's just mark it as a "Source" and provides the link as magnet (UI can handle or we visit)
                    # Actually, if we want magnets, we MUST visit.
                    
                    # To keep it fast, I'll implement a 1-result-at-a-time or just the first few.
                    # Or skip FitGirl if it's too complex for "lots of indexers" fast.
                    
                    # Let's try to find if there's an indexer for FitGirl.
                    pass
                
                return results # Empty for now until I find a better way or decide to visit
            except Exception as e:
                print(f"FitGirl search failed: {e}")
                return []
