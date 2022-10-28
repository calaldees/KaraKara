from types import MappingProxyType
from typing import Mapping, Iterable

def harden(data):
    """
    >>> harden({"a": [1,2,3]})
    mappingproxy({'a': (1, 2, 3)})
    >>> harden({"a": [1,2, {3}] })
    mappingproxy({'a': (1, 2, (3,))})
    >>> harden({"a": [1,2, {"b": 2}] })
    mappingproxy({'a': (1, 2, mappingproxy({'b': 2}))})
    >>> harden([1, {"c": True, "d": 3.14, "e": {"no", "no"}}])
    (1, mappingproxy({'c': True, 'd': 3.14, 'e': ('no',)}))
    """
    if isinstance(data, Mapping):
        return MappingProxyType({k: harden(v) for k, v in data.items()})
    if isinstance(data, Iterable) and not isinstance(data, str):
        return tuple((harden(i) for i in data))
    return data


from itertools import chain, zip_longest
from functools import partial, reduce

def flatten(iterable):
    """
    https://docs.python.org/3/library/itertools.html#itertools-recipes

    >>> tuple(flatten(((1,2), (3,4))))
    (1, 2, 3, 4)
    """
    yield from chain.from_iterable(iterable)

def grouper(n, iterable, fillvalue=None):
    """
    https://stackoverflow.com/a/434411/3356840

    >>> tuple(grouper(3, 'ABCDEFG', 'x'))
    (('A', 'B', 'C'), ('D', 'E', 'F'), ('G', 'x', 'x'))
    """
    return zip_longest(*((iter(iterable),) * n), fillvalue=fillvalue)


class IteratorCombine():
    r"""
    >>> i = IteratorCombine().map(lambda x: x+1).filter(lambda y: y>3)
    >>> tuple(i.process((1,2,3,4,5)))
    (4, 5, 6)
    >>> i = i.group(2)
    >>> tuple(i.process((1,2,3,4,5)))
    ((4, 5), (6, None))
    >>> i = i.flatten()
    >>> tuple(i.process((1,2,3,4,5)))
    (4, 5, 6, None)

    >>> do_thing = IteratorCombine().map(partial(int.to_bytes, length=2, byteorder='big')).flatten().func(bytes).process
    >>> do_thing(b'abc')
    b'\x00a\x00b\x00c'
    """
    def __init__(self, operations=None):
        self._operations = operations or tuple()
    def func(self, func):
        return IteratorCombine(self._operations + (func,))
    def map(self, func):
        return self.func(partial(map, func))
    def filter(self, func):
        return self.func(partial(filter, func))
    def group(self, n):
        return self.func(partial(grouper, n))
    def flatten(self):
        return self.func(flatten)
    def reduction(self):
        raise NotImplementedError()
        return self.func()  # TODO: similar to `group`. It process multiple items and returns a single item.
    def process(self, data):
        return reduce(lambda iterable, func: func(iterable), self._operations, data)
