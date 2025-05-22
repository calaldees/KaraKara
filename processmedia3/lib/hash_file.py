from datetime import datetime
from base64 import b64encode
from pathlib import Path
from typing import override, Self, TypedDict, NamedTuple
from functools import cached_property
from abc import abstractmethod
from collections.abc import Mapping, Generator, Sequence, MutableSet
from os import stat_result
#from zlib import adler32
from hashlib import sha256
from io import BytesIO
import urllib.response

import dateparser


def hash_bytes(data) -> bytes:
    #return adler32(data).to_bytes(4)
    return sha256(data).digest()


# Abstract ---------------------------------------------------------------------

class AbstractFile():
    block_size: int = pow(2, 13)  # first and last 8k of the file

    @property
    @abstractmethod
    def name(self) -> str: ...

    @cached_property
    @abstractmethod
    def head_tail(self) -> bytes: ...
        # Get the head self.block_size and tail self.block_size
        # if less then self.block_size total, just return the whole head

    @property
    @abstractmethod
    def size(self) -> int: ...

    @property
    @abstractmethod
    def mtime(self) -> int: ...

    @cached_property
    def hash(self) -> str:
        return re.sub("[+/=]", "_", b64encode(hash_bytes(self.head_tail + self.size.to_bytes(4))).decode('utf8'))


class AbstractFolder():
    @property
    @abstractmethod
    def files(self) -> Generator[AbstractFile]: ...



# Path/Local -------------------------------------------------------------------

class LocalFile(AbstractFile):
    def __init__(self, path: Path):
        self.path = path

    @property
    @override
    def name(self) -> str:
        return self.path.as_posix()

    @cached_property
    @override
    def head_tail(self) -> bytes:
        with self.path.open('rb') as f:
            if self.size < self.block_size*2:
                return f.read()
            bytes_io = BytesIO()
            bytes_io.write(f.read(self.block_size))
            f.seek(self.size - self.block_size)
            bytes_io.write(f.read(self.block_size))
            return bytes_io.getvalue()

    @cached_property
    def stat(self) -> stat_result:
        return self.path.stat()

    @property
    @override
    def size(self) -> int:
        return self.stat.st_size

    @property
    @override
    def mtime(self) -> int:
        return int(self.stat.st_mtime)


class LocalPath(AbstractFolder):
    def __init__(self, path: Path):
        self.path = path

    @property
    @override
    def files(self) -> Generator[AbstractFile]:
        for path in self.path.glob("**/*"):
            yield LocalFile(path)



# Remote/HTTP/Url --------------------------------------------------------------

import re
import json
import urllib.request  # TODO: use http2 client. (http1 involves LOTS of https handshaking)
#from http.client import HTTPResponse, HTTPMessage
class HTTPResponse(NamedTuple):
    body: bytes
    headers: Mapping[str, str]
def _http(url, headers={}, method='GET', timeout=5) -> HTTPResponse:
    request = urllib.request.Request(url, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return HTTPResponse(response.read(), response.headers)


class HttpFile(AbstractFile):
    HEADERS_REQUIRED = frozenset({'accept-ranges', 'last-modified', 'content-length'})
    HEADER_DATETIME_STRPTIME = r'%a, %d %b %Y %H:%M:%S %Z'

    def __init__(self, url: str, mtime_str: str = '', size_str: str = ''):
        self.url = url
        self._size = size_str
        self._mtime = mtime_str

    @property
    def name(self) -> str:
        return self.url

    @cached_property
    @override
    def head_tail(self) -> bytes:
        """
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Range
        https://blog.adamchalmers.com/multipart/
        https://everything.curl.dev/http/modify/ranges.html
            `curl -r 0-199,1000-1199 http://example.com/`
        https://stackoverflow.com/a/15781202/3356840 Python - HTTP multipart/form-data POST request
        """
        # TODO: Bug? Will this request fail of the ranges overlap? test filesize between 8k to 16k (suggest 10k?)
        response = _http(self.url, headers={'Range': f'bytes=0-{self.block_size-1},-{self.block_size}'})
        self._mtime = response.headers.get('Last-Modified', '')
        multipart_boundary = re.match(r'multipart/byteranges; boundary=(.+)', response.headers.get('content-type',''))
        if not multipart_boundary:
            self._size = response.headers.get('content-length', '')
            return response.body
        HEAD_END = b'\r\n\r\n'
        bytes_io = BytesIO()
        parts = response.body.split(f'\r\n--{multipart_boundary.group(1)}'.encode('utf8'))
        parts = filter(lambda data: len(data)>self.block_size, parts)
        for part in parts:
            i = part.index(HEAD_END) + len(HEAD_END)
            meta, body = part[:i], part[i:]
            if size_match := re.search(r'Content-range: bytes [\d-]+/(\d+)', meta.decode('utf8'), re.IGNORECASE):
                self._size = size_match.group(1)
            bytes_io.write(body)
        return bytes_io.getvalue()

        # Old way with multiple requests
        if self.size > self.block_size*2:
            return (
                _http(self.url, headers={'Range': f'bytes=0-{self.block_size-1}'}).body +
                _http(self.url, headers={'Range': f'bytes=-{self.block_size}'}).body
            )
        return _http(self.url).body

    @cached_property
    def headers(self) -> Mapping[str, str]:
        response = _http(self.url, method='HEAD')
        if set(key.lower() for key in response.headers.keys()) >= self.HEADERS_REQUIRED:
            return response.headers
        raise Exception(f'http server does support required headers: {self.HEADERS_REQUIRED}')

    @property
    @override
    def size(self) -> int:
        # TODO: '8.1M' can come from apache. What do we do?
        return int(self._size or self.headers['content-length'])

    @property
    @override
    def mtime(self) -> int:
        mtime = self._mtime or self.headers['last-modified']
        #dt = datetime.strptime(mtime, self.HEADER_DATETIME_STRPTIME)
        dt = dateparser.parse(mtime)
        return int(dt.timestamp())


class HttpFolder(AbstractFolder):
    RE_FILE = re.compile(r'a.+?href="(?P<name>.*?\.\w{3,4})".*?(?P<mtime>[a-zA-Z0-9_: -]*(19|20|21)\d\d[a-zA-Z0-9_: -]*).*\s{2,99}(?P<size>[\w.]+)\s')
    RE_FOLDER = re.compile(r'a.+?href="(?P<name>.*?[^.]/)".*(19|20|21)\d\d')  # identify folder links. folders have an mtime, but we don't parse the mtime

    def __init__(self, url: str):
        self.url = url

    class FileItem(TypedDict):
        name: str
        type: str
        mtime: str
        size: str

    @property
    @override
    def files(self) -> Generator[AbstractFile]:
        folders_visited: MutableSet[str] = set()
        folders_to_visit: MutableSet[str] = set((self.url,))
        while folders_to_visit:
            url = folders_to_visit.pop()
            response = _http(url, headers={'Accept': 'application/json, text/html'})
            body = response.body.decode('utf8')
            folders_visited.add(url)
            content_type = response.headers.get('content-type', '')
            file_dicts: Sequence[HttpFolder.FileItem] = []
            if 'json' in content_type:
                data = json.loads(response.body)
                file_dicts[:] = (i for i in data if i['type'] == 'file')
                folders_to_visit |= {f'{url}{i['name']}/' for i in data if i['type'] == 'directory'}
            elif 'html' in content_type:
                file_dicts[:] = [file_match.groupdict() for file_match in self.RE_FILE.finditer(body)]
                folders_to_visit |= {
                    f'{url}{folder_match.group(1)}'
                    for folder_match in self.RE_FOLDER.finditer(body)
                }
            folders_to_visit -= folders_visited
            for file_dict in file_dicts:
                yield HttpFile(
                    url = f'{url}{file_dict['name']}',
                    mtime_str = dateparser.parse(file_dict['mtime']).strftime(HttpFile.HEADER_DATETIME_STRPTIME),
                    size_str = file_dict['size']
                )


# Example ----------------------------------------------------------------------

# python3 hash_file.py
aa = HttpFile('https://calaldees.dreamhosters.com/karakara_media/Captain%20America%20(1966).mp4')
bb = LocalFile(Path('../media/source/Captain America (1966).mp4'))
cc = HttpFile('https://calaldees.dreamhosters.com/karakara_media/Captain%20America%20(1966).srt')
#breakpoint()
#cc.head_tail
#aa.head_tail
#assert aa.hash == bb.hash
ff = HttpFolder('https://calaldees.dreamhosters.com/karakara_media/')
#ff = HttpFolder('http://host.docker.internal/')

#for fi in ff.files:
#    breakpoint()
# breakpoint()

"""
\r\n--a3ce1fb8f44c97b4\r\nContent-type: video/mp4\r\nContent-range: bytes 0-8191/8495580\r\n\r\n

\r\n--a3ce1fb8f44c97b4\r\nContent-type: video/mp4\r\nContent-range: bytes 8487389-8495579/8495580\r\n\r\n
"""


"""apache?
<h1>Index of /karakara_media</h1>
<pre>      <a href="?C=N;O=D">Name</a>                    <a href="?C=M;O=A">Last modified</a>      <a href="?C=S;O=A">Size</a>  <a href="?C=D;O=A">Description</a><hr>      <a href="/">Parent Directory</a>                             -
      <a href="Captain%20America%20(1966).mp4">Captain America (196..&gt;</a> 2022-11-13 09:09  8.1M  
      <a href="Captain%20America%20(1966).srt">Captain America (196..&gt;</a> 2022-11-13 09:09  426   
      <a href="Captain%20America%20(1966).txt">Captain America (196..&gt;</a> 2022-11-13 09:09  174   
      <a href="KAT-TUN%20Your%20side%20%5bInstrumental%5d.jpg">KAT-TUN Your side [I..&gt;</a> 2022-11-13 08:02   43K  
      <a href="KAT-TUN%20Your%20side%20%5bInstrumental%5d.mp3">KAT-TUN Your side [I..&gt;</a> 2022-11-13 08:02  8.2M  
      <a href="KAT-TUN%20Your%20side%20%5bInstrumental%5d.srt">KAT-TUN Your side [I..&gt;</a> 2022-11-13 08:02  2.9K  
      <a href="KAT-TUN%20Your%20side%20%5bInstrumental%5d.txt">KAT-TUN Your side [I..&gt;</a> 2022-11-13 08:02  136   
<hr></pre>
"""
"""nginx
<h1>Index of /</h1><hr><pre><a href="../">../</a>
<a href="folders_and_known_fileexts.conf">folders_and_known_fileexts.conf</a>                    19-May-2025 07:10                 599
<a href="test.conf">test.conf</a>                                          19-May-2025 06:58                   0
<a href="test.json">test.json</a>                                          19-May-2025 06:58                   0
</pre>
"""
"""nginx json
[
{ "name":"folders_and_known_fileexts.conf", "type":"file", "mtime":"Mon, 19 May 2025 07:04:50 GMT", "size":598 },
{ "name":"test.conf", "type":"file", "mtime":"Mon, 19 May 2025 06:58:55 GMT", "size":0 },
{ "name":"test.json", "type":"file", "mtime":"Mon, 19 May 2025 06:58:55 GMT", "size":0 }
]
"""
"""
h1>Directory listing for /source/</h1>
<hr>
<ul>
<li><a href=".DS_Store">.DS_Store</a></li>
<li><a href=".gitignore">.gitignore</a></li>
<li><a href="Captain%20America%20%281966%29.mp4">Captain America (1966).mp4</a></li>
<li><a href="Captain%20America%20%281966%29.srt">Captain America (1966).srt</a></li>
<li><a href="Captain%20America%20%281966%29.txt">Captain America (1966).txt</a></li>
"""
