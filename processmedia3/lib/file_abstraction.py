from datetime import datetime
from base64 import b64encode
from pathlib import Path
from typing import override, TypedDict, NamedTuple
from functools import cached_property
from abc import abstractmethod
from typing import Self
import typing as t
from collections.abc import Mapping, Generator, Iterable
from os import stat_result
from io import BytesIO
import gzip

import dateparser


# Hash -------------------------------------------------------------------------

# from zlib import adler32
from hashlib import sha256


def hash_bytes(data: bytes) -> bytes:
    # return adler32(data).to_bytes(4)
    return sha256(data).digest()


# Abstract ---------------------------------------------------------------------


class AbstractFile:
    block_size: int = pow(2, 13)  # first and last 8k of the file

    @property
    @abstractmethod
    def absolute(self) -> str: ...

    @property
    @abstractmethod
    def relative(self) -> str: ...

    @property
    @abstractmethod
    def stem(self) -> str: ...

    @property
    @abstractmethod
    def suffix(self) -> str: ...

    @property
    @abstractmethod
    def size(self) -> int: ...

    @property
    @abstractmethod
    def mtime(self) -> datetime: ...

    @property
    @abstractmethod
    def text(self) -> str: ...

    @cached_property
    @abstractmethod
    def head_tail(self) -> bytes:
        """
        Get the head self.block_size and tail self.block_size
        if less then self.block_size total, just return the whole head
        """
        ...

    @cached_property
    def hash(self) -> str:
        hash = hash_bytes(self.head_tail + self.size.to_bytes(4))
        return re.sub("[+/=]", "_", b64encode(hash).decode("utf8"))


class AbstractFolder:
    @property
    @abstractmethod
    def files(self) -> Generator[AbstractFile]: ...

    @classmethod
    def from_str(cls, s: str) -> Self | None: ...


class AbstractFileException(Exception):
    pass


# Path/Local -------------------------------------------------------------------


class LocalFile(AbstractFile):
    def __init__(self, path: Path, root: Path):
        if not path.is_file():
            raise FileNotFoundError(path)
        self.path = path
        self.root = root or path.parent

    @property
    @override
    def absolute(self) -> str:
        return self.path.as_posix()

    @property
    @override
    def relative(self) -> str:
        return str(self.path.relative_to(self.root))

    @property
    @override
    def stem(self) -> str:
        return self.path.stem

    @property
    @override
    def suffix(self) -> str:
        return self.path.suffix

    @cached_property
    def stat(self) -> stat_result:
        return self.path.stat()

    @property
    @override
    def size(self) -> int:
        return self.stat.st_size

    @property
    @override
    def mtime(self) -> datetime:
        return datetime.fromtimestamp(self.stat.st_mtime)

    @cached_property
    @override
    def text(self) -> str:
        return self.path.read_text()

    @cached_property
    @override
    def head_tail(self) -> bytes:
        """
        >>> import tempfile
        >>> temp_dir = tempfile.TemporaryDirectory()
        >>> temp_path = Path(temp_dir.name)
        >>> file_path = temp_path.joinpath('test.bin')
        >>> file_path.write_bytes(b'A'*pow(2,16) + b'B'*pow(2,16))
        131072
        >>> file = LocalFile(path=file_path, root=temp_path)
        >>> file.hash
        'YNLr5Drsn7b9WgMy8JyL09fsUTSO12KFQen5gmyvurE_'
        >>> file.size
        131072
        >>> temp_dir.cleanup()
        """
        with self.path.open("rb") as f:
            if self.size < self.block_size * 2:
                return f.read()
            bytes_io = BytesIO()
            bytes_io.write(f.read(self.block_size))
            f.seek(self.size - self.block_size)
            bytes_io.write(f.read(self.block_size))
            return bytes_io.getvalue()


class LocalPath(AbstractFolder):
    def __init__(self, root: Path):
        if not root.is_dir():
            raise NotADirectoryError(root)
        self.root = root

    @override
    @classmethod
    def from_str(cls, s: str) -> Self | None:
        if (path := Path(s)).is_dir():
            return cls(path)
        return None

    @property
    @override
    def files(self) -> Generator[AbstractFile]:
        for path in self.root.glob("**/*"):
            # path.stat  # ? Investigate - this was part of `Source()` is this needed?
            if path.is_file():
                yield LocalFile(path, root=self.root)


# Remote/HTTP/Url --------------------------------------------------------------

import re
import json
import urllib.request  # TODO: use http2 client. (http1 involves LOTS of https handshaking)
from urllib.parse import urlparse, unquote

# from http.client import HTTPResponse, HTTPMessage


class HTTPResponse(NamedTuple):
    body: bytes
    headers: Mapping[str, str]
    status: int

    def has_headers(self, expected_headers: frozenset[str]) -> bool:
        return set(key.lower() for key in self.headers.keys()) >= expected_headers


def _http(url, headers={}, method="GET", timeout=5) -> HTTPResponse:
    request = urllib.request.Request(url, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return HTTPResponse(response.read(), response.headers, response.status)


class HttpFile(AbstractFile):
    """
    >>> file = HttpFile(
    ...     url='https://calaldees.dreamhosters.com/karakara_media/Captain%20America%20(1966).mp4',
    ...     url_root='https://calaldees.dreamhosters.com/karakara_media/',
    ...     mtime_str=', 2022-11-13 08:02   ',
    ...     size_str='8.1M'
    ... )
    >>> file.absolute
    'https://calaldees.dreamhosters.com/karakara_media/Captain%20America%20(1966).mp4'
    >>> file.relative
    'Captain%20America%20(1966).mp4'
    >>> file.stem
    'Captain America (1966)'
    >>> file.suffix
    '.mp4'
    >>> file.mtime
    datetime.datetime(2022, 11, 13, 8, 2)
    """

    HEADERS_REQUIRED = frozenset({"accept-ranges", "last-modified", "content-length"})
    HEADER_DATETIME_STRPTIME = r"%a, %d %b %Y %H:%M:%S %Z"

    def __init__(self, url: str, url_root: str, mtime_str: str = "", size_str: str = ""):
        self.url = url
        self.url_root = url_root
        self._size = size_str
        self._mtime = mtime_str
        assert self.url.startswith(self.url_root)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.absolute}"

    @property
    def absolute(self) -> str:
        return self.url

    @property
    @override
    def relative(self) -> str:
        # Less than ideal, nieave implementation
        return self.url.replace(self.url_root, "")

    @property
    def _path(self) -> Path:
        # Not to be used in local filesystem, but does have useful functions for parts
        return Path(unquote(urlparse(self.url).path))

    @property
    @override
    def stem(self) -> str:
        return self._path.stem

    @property
    @override
    def suffix(self) -> str:
        return self._path.suffix

    @cached_property
    @override
    def head_tail(self) -> bytes:
        r"""
        Use HTTP Range request to get first 8k and last 8k of the file.

        https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Range
        https://blog.adamchalmers.com/multipart/
        https://everything.curl.dev/http/modify/ranges.html
            `curl -r 0-199,1000-1199 http://example.com/`
        https://stackoverflow.com/a/15781202/3356840 Python - HTTP multipart/form-data POST request

        I generated the same file as the one the `LocalFile` test above and put it on a webserver can captured the response.
        I've gziped the response below to save space in the test. The test data was just `A`s and `B`s so it compressed well.
        You can decode the item below manually and see the range request headers
        >>> body = b'\x1f\x8b\x08\x00@\xb18h\x02\xff\xed\xda1\n\x830\x18\x86\xe1=\x90;x\x81\x1f\x8dR\x8c\xdd\xda\x9e$\x91X\x846\x8a\xfe\x8b\xb7\xafti\x87\x8e]\x84\xf7\x99?\xbe\x13\xbc\xd6\x88\xa4\xd6\xc7\xf6\x14k\xd7\xc5f\x18|m\xcdm\xca\x9a\xb2\x8ans:\x17a\x9e\x1fc\x1ft\x9cr9\xf5\x9aTV]Rx~vK\xc8\xf7}\x187MkQ\x89w\x9d+]\xe3\xaav\xff\xb2\xe6\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0e\xcf\xfe\xbf1pu\xed}%\xef\xc6\xe0;5\xb8\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80\xc3\xfb\x95\x1a\x88X\xf3\x02\xd1\xf2~b\xe7@\x00\x00'
        >>> response = HTTPResponse(
        ...     body=body,
        ...     headers={
        ...         'last-modified': 'Thu, 29 May 2025 18:37:46 GMT',
        ...         'etag': '"20000-6364a9806c97a"',
        ...         'accept-ranges': 'bytes',
        ...         'content-length': '171',
        ...         'cache-control': 'max-age=172800',
        ...         'expires': 'Sat, 31 May 2025 18:53:19 GMT',
        ...         'vary': 'User-Agent',
        ...         'content-type': 'multipart/byteranges; boundary=e78b75b219b3ff82',
        ...         'date': 'Thu, 29 May 2025 18:53:19 GMT',
        ...         'server': 'Apache',
        ...         'content-encoding': 'gzip',
        ...     },
        ...     status=206,
        ... )

        >>> from unittest.mock import patch
        >>> with patch('lib.file_abstraction._http') as mock_http:
        ...     mock_http.return_value = response
        ...     file = HttpFile(url='fake_root/fake_url', url_root='fake_root')
        ...     hash = file.hash

        >>> file.hash
        'YNLr5Drsn7b9WgMy8JyL09fsUTSO12KFQen5gmyvurE_'
        >>> file.mtime
        datetime.datetime(2025, 5, 29, 18, 37, 46, tzinfo=<StaticTzInfo 'GMT'>)
        >>> file.size
        131072

        """
        # TODO: Bug? Will this request fail of the ranges overlap? test filesize between 8k to 16k (suggest 10k?)
        response = _http(
            self.url,
            headers={"Range": f"bytes=0-{self.block_size - 1},-{self.block_size}"},
        )
        if not response.has_headers(self.HEADERS_REQUIRED):
            raise AbstractFileException(f"http server does support required headers: {self.HEADERS_REQUIRED}")
        self._mtime = response.headers.get("last-modified", "")
        multipart_boundary = re.match(
            r"multipart/byteranges; boundary=(.+)",
            response.headers.get("content-type", ""),
        )
        body = (
            gzip.decompress(response.body) if "gzip" in response.headers.get("content-encoding", "") else response.body
        )
        if not multipart_boundary:
            # self._size = response.headers.get('content-length', '')
            self._size = str(len(body))
            return body
        HEAD_END = b"\r\n\r\n"
        bytes_io = BytesIO()
        parts: Iterable[bytes] = body.split(f"\r\n--{multipart_boundary.group(1)}".encode("utf8"))
        parts = filter(lambda data: len(data) > self.block_size, parts)
        for part in parts:
            i = part.index(HEAD_END) + len(HEAD_END)
            meta, body = part[:i], part[i:]
            if size_match := re.search(r"Content-range: bytes [\d-]+/(\d+)", meta.decode("utf8"), re.IGNORECASE):
                self._size = size_match.group(1)
            bytes_io.write(body)
        return bytes_io.getvalue()

    @cached_property
    def headers(self) -> Mapping[str, str]:
        response = _http(self.url, method="HEAD")
        if not response.has_headers(self.HEADERS_REQUIRED):
            raise AbstractFileException(f"http server does support required headers: {self.HEADERS_REQUIRED}")
        return response.headers

    @property
    @override
    def size(self) -> int:
        # TODO: '8.1M' can come from apache. What do we do?
        return int(self._size or self.headers["content-length"])

    @property
    @override
    def mtime(self) -> datetime:
        mtime = self._mtime or self.headers["last-modified"]
        # dt = datetime.strptime(mtime, self.HEADER_DATETIME_STRPTIME)
        return dateparser.parse(mtime) or datetime.fromtimestamp(0)

    @cached_property
    @override
    def text(self) -> str:
        return _http(self.url).body.decode("utf8")  # TODO: gzip?


class HttpFolder(AbstractFolder):
    RE_FILE = re.compile(
        r'a.+?href="(?P<name>.*?\.\w{3,4})".*?(?P<mtime>[a-zA-Z0-9_: -]*(19|20|21)\d\d[a-zA-Z0-9_: -]*).*\s{2,99}(?P<size>[\w.]+)\s'
    )
    RE_FOLDER = re.compile(
        r'a.+?href="(?P<name>.*?[^.]/)".*(19|20|21)\d\d'
    )  # identify folder links. folders have an mtime, but we don't parse the mtime

    def __init__(self, url: str):
        self.url = url
        assert self.url.endswith("/"), "url should end in `/` because it should be a folder"

    @override
    @classmethod
    def from_str(cls, s: str) -> Self | None:
        url = urlparse(s)
        if "http" in url.scheme and url.path.endswith("/"):
            return cls(s)
        return None

    class FileItem(TypedDict):
        name: str
        type: str
        mtime: str
        size: str

    @property
    @override
    def files(self) -> Generator[AbstractFile]:
        r"""
        >>> from unittest.mock import patch
        >>> def build_response(body, content_type):
        ...     return HTTPResponse(body=body.encode('utf8'), headers={'accept-ranges': 'bytes', 'content-type': content_type}, status=200)

        >>> def HttpFolder_files(response):
        ...     with patch('lib.file_abstraction._http') as mock_http:
        ...         mock_http.return_value = response
        ...         return tuple(HttpFolder('http://fake_url/').files)

        >>> apache = '''<h1>Index of /karakara_media</h1>
        ... <pre>      <a href="?C=N;O=D">Name</a>                    <a href="?C=M;O=A">Last modified</a>      <a href="?C=S;O=A">Size</a>  <a href="?C=D;O=A">Description</a><hr>      <a href="/">Parent Directory</a>                             -
        ... <a href="Captain%20America%20(1966).mp4">Captain America (196..&gt;</a> 2022-11-13 09:09  8.1M
        ... <a href="Captain%20America%20(1966).srt">Captain America (196..&gt;</a> 2022-11-13 09:09  426
        ... <a href="Captain%20America%20(1966).txt">Captain America (196..&gt;</a> 2022-11-13 09:09  174
        ... <a href="KAT-TUN%20Your%20side%20%5bInstrumental%5d.jpg">KAT-TUN Your side [I..&gt;</a> 2022-11-13 08:02   43K
        ... <a href="KAT-TUN%20Your%20side%20%5bInstrumental%5d.mp3">KAT-TUN Your side [I..&gt;</a> 2022-11-13 08:02  8.2M
        ... <a href="KAT-TUN%20Your%20side%20%5bInstrumental%5d.srt">KAT-TUN Your side [I..&gt;</a> 2022-11-13 08:02  2.9K
        ... <a href="KAT-TUN%20Your%20side%20%5bInstrumental%5d.txt">KAT-TUN Your side [I..&gt;</a> 2022-11-13 08:02  136
        ... <hr></pre>'''
        >>> HttpFolder_files(build_response(apache, 'text/html'))
        (HttpFile: http://fake_url/Captain%20America%20(1966).mp4, HttpFile: http://fake_url/Captain%20America%20(1966).srt, HttpFile: http://fake_url/Captain%20America%20(1966).txt, HttpFile: http://fake_url/KAT-TUN%20Your%20side%20%5bInstrumental%5d.jpg, HttpFile: http://fake_url/KAT-TUN%20Your%20side%20%5bInstrumental%5d.mp3, HttpFile: http://fake_url/KAT-TUN%20Your%20side%20%5bInstrumental%5d.srt, HttpFile: http://fake_url/KAT-TUN%20Your%20side%20%5bInstrumental%5d.txt)

        >>> nginx = '''<h1>Index of /</h1><hr><pre><a href="../">../</a>
        ... <a href="folders_and_known_fileexts.conf">folders_and_known_fileexts.conf</a>                    19-May-2025 07:10                 599
        ... <a href="test.conf">test.conf</a>                                          19-May-2025 06:58                   0
        ... <a href="test.json">test.json</a>                                          19-May-2025 06:58                   0
        ... </pre>'''
        >>> HttpFolder_files(build_response(nginx, 'text/html'))
        (HttpFile: http://fake_url/folders_and_known_fileexts.conf, HttpFile: http://fake_url/test.conf, HttpFile: http://fake_url/test.json)

        >>> nginx_json = '''[{ "name":"folders_and_known_fileexts.conf", "type":"file", "mtime":"Mon, 19 May 2025 07:04:50 GMT", "size":598 },{ "name":"test.conf", "type":"file", "mtime":"Mon, 19 May 2025 06:58:55 GMT", "size":0 },{ "name":"test.json", "type":"file", "mtime":"Mon, 19 May 2025 06:58:55 GMT", "size":0 }]'''
        >>> HttpFolder_files(build_response(nginx_json, 'application/json'))
        (HttpFile: http://fake_url/folders_and_known_fileexts.conf, HttpFile: http://fake_url/test.conf, HttpFile: http://fake_url/test.json)
        """
        folders_visited: set[str] = set()
        folders_to_visit: set[str] = set((self.url,))
        while folders_to_visit:
            url = folders_to_visit.pop()
            response = _http(url, headers={"Accept": "application/json, text/html"})
            body = response.body.decode("utf8")
            folders_visited.add(url)
            content_type = response.headers.get("content-type", "")
            file_dicts: list[HttpFolder.FileItem] = []
            if "json" in content_type:
                data = json.loads(response.body)
                file_dicts[:] = (i for i in data if i["type"] == "file")
                folders_to_visit |= {f"{url}{i['name']}/" for i in data if i["type"] == "directory"}
            elif "html" in content_type:
                file_dicts[:] = [
                    file_match.groupdict() for file_match in self.RE_FILE.finditer(body)  # type: ignore[misc]
                ]
                folders_to_visit |= {f"{url}{folder_match.group(1)}" for folder_match in self.RE_FOLDER.finditer(body)}
            else:
                raise AbstractFileException(f"unknown {content_type}")
            folders_to_visit -= folders_visited
            for file_dict in file_dicts:
                yield HttpFile(
                    url=f"{url}{file_dict['name']}",
                    url_root=self.url,
                    mtime_str=(dateparser.parse(file_dict["mtime"]) or datetime.fromtimestamp(0)).strftime(
                        HttpFile.HEADER_DATETIME_STRPTIME
                    ),
                    size_str=file_dict["size"],
                )


# Factory ----------------------------------------------------------------------

FolderTypes = (HttpFolder, LocalPath)


def AbstractFolder_from_str(s: str) -> AbstractFolder:
    for cls in FolderTypes:
        if folder := cls.from_str(s):
            return folder
    raise ValueError(f"unable to identify folder type from {s}")


# Example ----------------------------------------------------------------------


def _examples() -> None:
    aa = HttpFile(
        "https://calaldees.dreamhosters.com/karakara_media/Captain%20America%20(1966).mp4",
        url_root="https://calaldees.dreamhosters.com/karakara_media/",
    )
    bb = LocalFile(Path("../media/source/Captain America (1966).mp4"), Path("../media/source/"))
    cc = HttpFile(
        "https://calaldees.dreamhosters.com/karakara_media/Captain%20America%20(1966).srt",
        url_root="https://calaldees.dreamhosters.com/karakara_media/",
    )
    # cc.head_tail
    # aa.head_tail
    # assert aa.hash == bb.hash
    ff = HttpFolder("https://calaldees.dreamhosters.com/karakara_media/")
    # ff = HttpFolder('http://host.docker.internal/')
