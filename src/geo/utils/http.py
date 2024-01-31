import httpx

class HttpProcessor:

    def __init__(self, timeout: int = 1, user_agent: str = None):
        if not user_agent:
            user_agent = "aiohttp/3.7.4"

        self.client = None
        self.timeout = timeout
        self.user_agent = user_agent

    async def __aenter__(self):
        self.client = await httpx.AsyncClient(
            timeout=self.timeout,
            headers={"User-Agent": self.user_agent}
        ).__aenter__()
        return self.client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)
