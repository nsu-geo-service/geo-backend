
class StatsApplicationService:

    def __init__(self, config):
        self._config = config

    async def get_stats(self) -> dict:
        return {
            "ping": "ok",
        }
