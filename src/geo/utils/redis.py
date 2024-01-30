import logging
from datetime import timedelta
from typing import Any, Mapping

import redis.asyncio as redis
from redis.exceptions import RedisError


class RedisClient:
    def __init__(self, pool: redis.Redis):
        self.redis_client = pool

    async def close(self):
        """Закрыть соединение с Redis.
        Закрывает соединение с Redis.
        """
        logging.debug("Закрытие соединения с Redis.")
        await self.redis_client.close()

    async def ping(self):
        """Выполнить команду Redis PING.
        Пингует сервер Redis.
        Returns:
            response: Логическое значение, может ли клиент Redis пинговать сервер Redis.
        Raises:
            aioredis.RedisError: Если клиент Redis дал сбой при выполнении команды.
        """

        logging.debug("Сформирована Redis PING команда")
        try:
            return await self.redis_client.ping()
        except RedisError as ex:
            logging.exception(
                "Команда Redis PING завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            return False

    async def set(self, key: Any, value: Any, expire: int = None):
        """Выполнить команду Redis SET.
         Установите ключ для хранения строкового значения. Если ключ уже содержит значение, оно
         перезаписывается независимо от его типа.
        Args:
            key (any): Ключ.
            value (any): Значение, которое необходимо установить.
            expire (int): Время в секундах, по истечении которого ключ будет удален.
            (по умолчанию 30 дней)
        Returns:
            response: Ответ команды Redis SET, для получения дополнительной информации
                look: https://redis.io/commands/set#return-value
        Raises:
            aioredis.RedisError: Если клиент Redis дал сбой при выполнении команды.
        """

        logging.debug(f"Сформирована Redis SET команда, key: {key}, value: {value}")
        try:
            await self.redis_client.set(key, value)
            if expire:
                await self.redis_client.expire(key, expire)
        except RedisError as ex:
            logging.exception(
                "Команда Redis SET завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    async def rpush(self, key, value):
        """Выполнить команду Redis RPUSH.
         Вставляет все указанные значения в конец списка, хранящегося в ключе.
         Если ключ не существует, он создается как пустой список перед выполнением
         операция проталкивания. Когда ключ содержит значение, не являющееся списком,
         возвращается ошибка.
        Args:
            key (str): Ключ.
            value (str, list): Одно или несколько значений для добавления.
        Returns:
            response: Длина списка после операции push.
        Raises:
            aioredis.RedisError: Если клиент Redis дал сбой при выполнении команды.
        """

        logging.debug(f"Сформирована Redis RPUSH команда, key: {key}, value: {value}")
        try:
            await self.redis_client.rpush(key, value)
        except RedisError as ex:
            logging.exception(
                "Команда Redis RPUSH завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    async def exists(self, key):
        """Выполнить команду Redis EXISTS.
        Возвращает True, если ключ существует.
        Args:
            key (str): Redis db key.
        Returns:
            response: Логическое значение, определяющее, существует ли ключ в Redis db.
        Raises:
            aioredis.RedisError: Если клиент Redis дал сбой при выполнении команды.
        """

        logging.debug(f"Сформирована Redis EXISTS команда, key: {key}, exists")
        try:
            return await self.redis_client.exists(key)
        except RedisError as ex:
            logging.exception(
                "Команда Redis EXISTS завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    async def get(self, key):
        """Выполнить команду Redis GET.
         Получает значение ключа. Если ключ не существует, то возвращается специальное
         значение None. Возвращается исключение, если значение, хранящееся в ключе, не является
         string, потому что GET обрабатывает только строковые значения.
        Args:
            key (str): Ключ.
        Returns:
            response: Значение ключа.
        Raises:
            aioredis.RedisError: Если клиент Redis дал сбой при выполнении команды.
        """

        logging.debug(f"Сформирована Redis GET команда, key: {key}")
        try:
            return await self.redis_client.get(key)
        except RedisError as ex:
            logging.exception(
                "Команда Redis GET завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    async def lrange(self, key, start, end):
        """Выполнить команду Redis LRANGE.
         Возвращает указанные элементы списка, хранящегося в ключе. Смещения
         start и stop — это индексы, начинающиеся с нуля, где 0 — первый элемент
         списка (голова списка), 1 — следующий элемент и так далее.
         Эти смещения также могут быть отрицательными числами, указывающими, что смещения начинаются
         в конце списка. Например, -1 — это последний элемент
         список, -2 предпоследний и так далее.
        Args:
            key (str): Ключ.
            start (int): Начальное значение смещения.
            end (int): Конечное значение смещения.
        Returns:
            response: Возвращает указанные элементы списка, хранящегося в ключе.
        Raises:
            aioredis.RedisError: Если клиент Redis дал сбой при выполнении команды.
        """

        logging.debug(f"Сформирована Redis LRANGE команда, key: {key}, start: {start}, end: {end}")
        try:
            return await self.redis_client.lrange(key, start, end)
        except RedisError as ex:
            logging.exception(
                "Команда Redis LRANGE завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    async def delete(self, key: str):

        logging.debug(f"Сформирована Redis DELETE команда, key: {key}")
        try:
            return await self.redis_client.delete(key)
        except RedisError as ex:
            logging.exception(
                "Команда Redis DELETE завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    async def keys(self, pattern: str, **kwargs):

        logging.debug(f"Сформирована Redis KEYS команда, key: {pattern}")
        try:
            return await self.redis_client.keys(pattern, **kwargs)
        except RedisError as ex:
            logging.exception(
                "Команда Redis KEYS завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    async def hset(self, hash_key: Any, mapping: dict, items: Any = None):
        logging.debug(f"Сформирована Redis HSET команда, name: {hash_key}, mapping: {mapping}, items: {items}")
        try:
            await self.redis_client.hset(name=hash_key, mapping=mapping, items=items)
        except RedisError as ex:
            logging.exception(
                "Команда Redis HSET завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    async def expire(
            self,
            name: Any,
            time: int | timedelta,
    ):
        logging.debug(f"Сформирована Redis EXPIRE команда, name: {name}, time: {time}")
        try:
            await self.redis_client.expire(name, time)
        except RedisError as ex:
            logging.exception(
                "Команда Redis EXPIRE завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    async def hgetall(self, hash_key: Any):
        logging.debug(f"Сформирована Redis HGETALL команда, hash_key: {hash_key}")
        try:
            return await self.redis_client.hgetall(hash_key)
        except RedisError as ex:
            logging.exception(
                "Команда Redis HGETALL завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    async def hexists(self, name: Any, key: Any):
        logging.debug(f"Сформирована Redis HEXISTS команда, name: {name}, key: {key}")
        try:
            return await self.redis_client.hexists(name, key)
        except RedisError as ex:
            logging.exception(
                "Команда Redis HEXISTS завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    async def hdel(self, name: Any, *keys: Any):
        logging.debug(f"Сформирована Redis HDEL команда, name: {name}, keys: {keys}")
        try:
            return await self.redis_client.hdel(name, *keys)
        except RedisError as ex:
            logging.exception(
                "Команда Redis HDEL завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    async def hget(self, name: Any, key: Any):
        logging.debug(f"Сформирована Redis HGET команда, name: {name}, key: {key}")
        try:
            return await self.redis_client.hget(name, key)
        except RedisError as ex:
            logging.exception(
                "Команда Redis HGET завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    async def zadd(self, name: Any, mapping: Mapping):
        logging.debug(f"Сформирована Redis ZADD команда, name: {name}, mapping: {mapping}")
        try:
            return await self.redis_client.zadd(name, mapping)
        except RedisError as ex:
            logging.exception(
                "Команда Redis ZADD завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    async def zrange(self, name: Any, start: int, end: int, with_scores: bool = False, offset: int = None):
        logging.debug(
            f"Сформирована Redis ZRANGE команда, name: {name}, start: {start}, end: {end}, with_scores: {with_scores}"
        )
        try:
            return await self.redis_client.zrange(name, start, end, offset=offset, withscores=with_scores)
        except RedisError as ex:
            logging.exception(
                "Команда Redis ZRANGE завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    async def zrem(self, name: Any, *values: Any):
        logging.debug(f"Сформирована Redis ZREM команда, name: {name}, values: {values}")
        try:
            return await self.redis_client.zrem(name, *values)
        except RedisError as ex:
            logging.exception(
                "Команда Redis ZREM завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex

    async def zcard(self, name: Any):
        logging.debug(f"Сформирована Redis ZCARD команда, name: {name}")
        try:
            return await self.redis_client.zcard(name)
        except RedisError as ex:
            logging.exception(
                "Команда Redis ZCARD завершена с исключением",
                exc_info=(type(ex), ex, ex.__traceback__),
            )
            raise ex
