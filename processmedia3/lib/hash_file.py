from base64 import b64encode
from pathlib import Path
from typing import override
from functools import cached_property
from abc import abstractmethod
from zlib import adler32


class AbstractHashable():
    block_size: int = pow(2, 13)  # first and last 8k of the file

    @cached_property
    @abstractmethod
    def head(self) -> bytes: ...

    @cached_property
    @abstractmethod
    def tail(self) -> bytes: ...

    @cached_property
    @abstractmethod
    def size(self) -> int: ...

    @cached_property
    @abstractmethod
    def mtime(self) -> int: ...

    @cached_property
    def hash(self) -> str:
        return b64encode(adler32(self.head + self.tail + self.size.to_bytes(4)).to_bytes(4)).decode('utf8').rstrip('=')


class PathHashable(AbstractHashable):
    def __init__(self, path: Path):
        self.path = path

    @cached_property
    @override
    def head(self) -> bytes:
        with self.path.open('rb') as f:
            return f.read(self.block_size)

    @cached_property
    @override
    def tail(self) -> bytes:
        with self.path.open('rb') as f:
            f.seek(self.size - self.block_size)
            return f.read(self.block_size)

    @cached_property
    @override
    def size(self) -> int:
        return self.path.stat().st_size


import urllib.request  # TODO: use http2 client. (http1 involves LOTS of https handshaking)
class UrlHashable(AbstractHashable):
    def __init__(self, url: str):
        self.url = url

    def _http_range(self, a:int , b: int) -> bytes:
        request = urllib.request.Request(self.url, headers={'Range': f'bytes={a}-{b-1}'}, method='GET')
        with urllib.request.urlopen(request) as response:
            return response.read()

    @cached_property
    @override
    def head(self) -> bytes:
        return self._http_range(0, self.block_size)

    @cached_property
    @override
    def tail(self) -> bytes:
        return self._http_range(self.size-self.block_size, self.size)

    @cached_property
    @override
    def size(self) -> int:
        request = urllib.request.Request(self.url, method='HEAD')
        with urllib.request.urlopen(request) as response:
            return int(response.headers['Content-Length'])


# aa = UrlHashable('https://calaldees.dreamhosters.com/karakara_media/Captain%20America%20(1966).mp4')
# bb = PathHashable(Path('../media/source/Captain America (1966).mp4'))
# assert aa.hash == bb.hash
# breakpoint()
