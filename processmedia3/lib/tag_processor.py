from functools import reduce
from itertools import pairwise
from typing import Dict, List


def parse_tags(data: str) -> Dict[str, List[str]]:
    r"""
    >>> data = '''
    ... \ufeff
    ... category:anime
    ... from:Macross
    ... from:Macross:Macross Dynamite 7
    ... use:opening
    ... title:Dynamite Explosion
    ... artist:Fire Bomber
    ... artist:Yoshiki Fukuyama
    ... retro
    ... \ufeff'''
    >>> parse_tags(data)
    {'category': ['anime'], 'from': ['Macross'], 'Macross': ['Macross Dynamite 7'], 'use': ['opening'], 'title': ['Dynamite Explosion'], 'artist': ['Fire Bomber', 'Yoshiki Fukuyama'], '': ['retro']}
    """
    data = data.strip().strip("\ufeff").strip()

    def _reduce(accumulator, item):
        item = tuple(filter(None, (i.strip() for i in item.split(":"))))
        if len(item) == 1:
            accumulator.setdefault("", set()).add(item[0])
        else:
            for parent, tag in pairwise(item):
                accumulator.setdefault(parent, set()).add(tag)
        return accumulator

    return dict(
        (k, sorted(v)) for k, v in reduce(_reduce, data.split("\n"), {}).items()
    )
