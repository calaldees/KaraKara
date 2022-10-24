from functools import reduce
from itertools import pairwise


def parse_tags(data):
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
    ... vocaltrack:on
    ... length:short
    ... vocalstyle:male
    ... lang:jp
    ... retro
    ... \ufeff'''
    >>> assert parse_tags(data) == {'category': {'anime'}, 'from': {'Macross'}, 'Macross': {'Macross Dynamite 7'}, 'use': {'opening'}, 'title': {'Dynamite Explosion'}, 'artist': {'Yoshiki Fukuyama', 'Fire Bomber'}, 'vocaltrack': {'on'}, 'length': {'short'}, 'vocalstyle': {'male'}, 'lang': {'jp'}, '': {'retro'}}
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

    return dict(reduce(_reduce, data.split("\n"), {}).items())


def parse_tags_file(filename):
    with open(filename) as fp:
        return parse_tags(fp.read())
