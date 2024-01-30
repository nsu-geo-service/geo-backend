
class RedisQueue:
    def __init__(self, client, namespace: str = 'queue'):
        self._client = client
        self.key = namespace

    def enqueue(self, item):
        self._client.rpush(self.key, item)

    def dequeue(self):
        return self._client.lpop(self.key)

    def is_empty(self):
        return self._client.llen(self.key) == 0
