from abc import ABC, abstractmethod
from typing import List
from models.torrent import TorrentResult

class BasePlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @abstractmethod
    async def search(self, query: str, category: str = None) -> List[TorrentResult]:
        pass
