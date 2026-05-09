from pydantic import BaseModel
from typing import Optional

class TorrentResult(BaseModel):
    title: str
    size: int  # Size in bytes
    seeders: int
    leechers: int
    age: str
    category: str
    source: str
    magnet: str
    infoHash: Optional[str] = None
