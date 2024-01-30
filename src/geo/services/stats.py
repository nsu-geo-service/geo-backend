
class StatsApplicationService:

    def __init__(self, redis_queue, config):
        self._redis_queue = redis_queue
        self._config = config

    async def get_stats(self) -> dict:
        return {
            "version": self._config.BASE.VERSION,
            "redis": await self._redis_queue.ping()
        }
