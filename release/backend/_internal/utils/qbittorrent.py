import httpx

class QBittorrentClient:
    def __init__(self, host="http://localhost:8080", username="admin", password="adminadmin"):
        self.host = host
        self.username = username
        self.password = password
        self.cookies = None

    async def login(self):
        url = f"{self.host}/api/v2/auth/login"
        data = {"username": self.username, "password": self.password}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, data=data)
                response.raise_for_status()
                self.cookies = response.cookies
                return True
            except Exception as e:
                print(f"qBittorrent login failed: {e}")
                return False

    async def add_torrent(self, magnet: str):
        if not self.cookies:
            await self.login()
        
        url = f"{self.host}/api/v2/torrents/add"
        data = {"urls": magnet}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, data=data, cookies=self.cookies)
                response.raise_for_status()
                return True
            except Exception as e:
                print(f"qBittorrent add failed: {e}")
                return False
