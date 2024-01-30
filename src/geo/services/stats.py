
class StatsApplicationService:

    def __init__(self, redis_client, config):
        self._redis_client = redis_client
        self._config = config

    async def get_stats(self) -> dict:
        return {
            "version": self._config.BASE.VERSION,
            "redis": await self._redis_client.ping()
        }
