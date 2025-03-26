from types import MappingProxyType
import typing as t


def harden(data: t.Mapping | t.Iterable | t.Any) -> t.Mapping | t.Iterable | t.Any:
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
    if isinstance(data, t.Mapping):
        return MappingProxyType({k: harden(v) for k, v in data.items()})
    if isinstance(data, t.Iterable) and not isinstance(data, str):
        return tuple((harden(i) for i in data))
    return data

