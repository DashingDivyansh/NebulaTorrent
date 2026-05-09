from typing import List
from plugins.base import BasePlugin
from models.torrent import TorrentResult

class YTSPlugin(BasePlugin):
    @property
    def name(self) -> str:
        return "YTS"

    @property
    def version(self) -> str:
        return "1.0"

    async def search(self, query: str, category: str = None) -> List[TorrentResult]:
        # YTS is only for movies
        if category and category.lower() not in ["movies", "film"]:
            return []

        url = "https://yts.mx/api/v2/list_movies.json"
        params = {
            "query_term": query,
            "sort_by": "seeds",
            "limit": 20
        }

        try:
            response = await self.fetch(url, params=params, timeout=10.0)
            data = response.json()
            
            if data.get("status") != "ok" or data.get("data", {}).get("movie_count", 0) == 0:
                return []

            results = []
            for movie in data["data"].get("movies", []):
                title_base = f"{movie.get('title')} ({movie.get('year')})"
                for torrent in movie.get("torrents", []):
                    quality = torrent.get("quality")
                    type_ = torrent.get("type")
                    title = f"{title_base} [{quality}] [{type_}]"
                    
                    # YTS doesn't provide magnet in list, but we can construct it
                    # magnet:?xt=urn:btih:HASH&dn=TITLE&tr=...
                    hash_ = torrent.get("hash")
                    magnet = f"magnet:?xt=urn:btih:{hash_}&dn={title}"
                    # Add common trackers
                    trackers = [
                        "udp://open.demonii.com:1337/announce",
                        "udp://tracker.openbittorrent.com:80",
                        "udp://tracker.coppersurfer.tk:6969",
                        "udp://glotorrents.pw:6969/announce",
                        "udp://tracker.opentrackr.org:1337/announce",
                        "udp://torrent.gresille.org:80/announce",
                        "udp://p4p.arenabg.com:1337",
                        "udp://tracker.leechers-paradise.org:6969"
                    ]
                    for tr in trackers:
                        magnet += f"&tr={tr}"

                    results.append(TorrentResult(
                        title=title,
                        size=torrent.get("size_bytes", 0),
                        seeders=torrent.get("seeds", 0),
                        leechers=torrent.get("peers", 0),
                        age=torrent.get("date_uploaded", ""),
                        category="Movies",
                        source=self.name,
                        magnet=magnet,
                        infoHash=hash_
                    ))
            return results
        except Exception as e:
            print(f"YTS search failed: {e}")
            return []
