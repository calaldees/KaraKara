import re
import urllib.request
from urllib.parse import unquote_plus
import pathlib

URL = "https://calaldees.dreamhosters.com/karakara_media/"
RE_LINKS = re.compile(r'a.+?href="(.*?\.\w{3,4})"')
PATH = pathlib.Path(__file__).parent.resolve().joinpath('source')

def get_url(url):
    return urllib.request.urlopen(url).read().decode('utf8')

if __name__ == "__main__":
    for match in RE_LINKS.finditer(get_url(URL)):
        url = match.group(1)
        path = PATH.joinpath(unquote_plus(url))
        if path.exists():
            print(f"Exists ${url}")
            continue
        print(f"Downloading ${url}")
        urllib.request.urlretrieve(URL+url, path)
