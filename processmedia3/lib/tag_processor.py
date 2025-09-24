from itertools import pairwise
import typing as t
from io import StringIO
import csv


def parse_tags(data: str) -> dict[str, list[str]]:
    r"""
    >>> data = '''
    ... \ufeff
    ... category:anime
    ... from:Macross:Macross Dynamite 7
    ... use:opening
    ... title:Dynamite Explosion
    ... artist:Fire Bomber
    ... artist:Yoshiki "Test" Fukuyama
    ... retro
    ... source:"https://www.youtube.com/watch?v=1b2a8d3e4f5"
    ... \ufeff'''
    >>> from pprint import pprint
    >>> pprint(parse_tags(data))
    {'': ['retro'],
     'Macross': ['Macross Dynamite 7'],
     'artist': ['Fire Bomber', 'Yoshiki "Test" Fukuyama'],
     'category': ['anime'],
     'from': ['Macross'],
     'source': ['https://www.youtube.com/watch?v=1b2a8d3e4f5'],
     'title': ['Dynamite Explosion'],
     'use': ['opening']}
    """
    data = data.strip().strip("\ufeff").strip()
    tags_values: dict[str, list[str]] = {}

    for row in csv.reader(StringIO(data), delimiter=":"):
        row = list(filter(None, (i.strip() for i in row)))
        if len(row) == 1:
            tags_values.setdefault("", []).append(row[0])
        else:
            for parent, tag in pairwise(row):
                tags_values.setdefault(parent, []).append(tag)

    return dict((k, sorted(set(v))) for k, v in tags_values.items())
