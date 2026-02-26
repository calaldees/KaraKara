#!/usr/bin/env python3

"""
For each "vocaloid" track in the database, if the "date" field is missing,
open a wiki page for the track title in Firefox.
"""

import sys
import webbrowser
from pathlib import Path


def parse_metadata(path):
    data = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if ":" in line:
                k, v = line.split(":", 1)
                data[k.strip().lower()] = v.strip()
    return data


def title_to_wiki_url(title):
    # convert spaces to underscores
    title = title.replace(" ", "_")
    if not title:
        return None
    # capitalize first letter, lowercase the rest
    title = title[0].upper() + title[1:].lower()
    return f"https://vocaloid.fandom.com/wiki/{title}"


def main():
    for path in sys.argv[1:]:
        path = Path(path)
        meta = parse_metadata(path)
        if "date" in meta:
            continue
        if meta.get("category") == "vocaloid" and meta.get("title"):
            url = title_to_wiki_url(meta["title"])
            if url:
                print(f"Opening: {url}")
                webbrowser.get("firefox").open_new_tab(url)


if __name__ == "__main__":
    main()
