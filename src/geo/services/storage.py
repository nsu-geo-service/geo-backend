import os
from typing import AsyncGenerator, Literal

import aiofiles

FILE_MODE = Literal[
    "r+", "+r", "rt+", "r+t", "+rt", "tr+", "t+r", "+tr", "w+", "+w", "wt+", "w+t", "+wt", "tw+", "t+w", "+tw", "a+",
    "+a", "at+", "a+t", "+at", "ta+", "t+a", "+ta", "x+", "+x", "xt+", "x+t", "+xt", "tx+", "t+x", "+tx", "w", "wt",
    "tw", "a", "at", "ta", "x", "xt", "tx", "r", "rt", "tr", "U", "rU", "Ur", "rtU", "rUt", "Urt", "trU", "tUr", "Utr"
]


class FileStorage:

    def __init__(self, path: os.PathLike | str, chunk_size: int = 1024 * 1024):
        """


        :param path: path to storage directory
        :param chunk_size: per chunk size in bytes
        """

        self.path = path
        os.makedirs(self.path, exist_ok=True)
        self.chunk_size = chunk_size

    async def save(self, filepath: os.PathLike | str, data: bytes | str, mode: FILE_MODE) -> None:
        async with aiofiles.open(os.path.join(self.path, filepath), mode) as f:
            await f.write(data)

    async def load(self, filepath: os.PathLike | str, mode: FILE_MODE) -> bytes | str:
        async with aiofiles.open(os.path.join(self.path, filepath), mode) as f:
            return await f.read()

    async def save_gen(
            self,
            filepath: os.PathLike | str,
            data: AsyncGenerator[bytes | str, None],
            mode: FILE_MODE
    ) -> None:
        async with aiofiles.open(os.path.join(self.path, filepath), mode) as f:
            async for chunk in data:
                await f.write(chunk)

    async def load_gen(self, filepath: os.PathLike | str, mode: FILE_MODE) -> AsyncGenerator[bytes | str, None]:
        async with aiofiles.open(os.path.join(self.path, filepath), mode) as f:
            while chunk := await f.read(self.chunk_size):
                yield chunk

    async def delete(self, filepath: os.PathLike | str) -> None:
        os.remove(os.path.join(self.path, filepath))

    async def exists(self, filepath: os.PathLike | str) -> bool:
        return os.path.exists(os.path.join(self.path, filepath))

    def abs_path(self, filepath: os.PathLike | str) -> str:
        return os.path.abspath(os.path.join(self.path, filepath))

    def size(self, filepath: os.PathLike | str) -> int:
        """

        :param filepath:
        :return: size in bytes
        """
        return os.path.getsize(os.path.join(self.path, filepath))
