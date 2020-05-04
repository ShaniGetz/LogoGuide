'''Immutable dict
'''

from collections import Mapping

__all__ = ['FrozenDict']


class FrozenDict(Mapping):
    '''An immutable dict'''
    def __init__(self, items):
        self._m = dict()
        for k, v in items.items():
            self._m[k] = v
        self._h = None

    def __len__(self):
        return len(self._m)

    def __iter__(self):
        return self._m.__iter__()

    def __contains__(self, key):
        return self._m.__contains__(key)

    def __eq__(self, other):
        return self._m.__eq__(other)

    def __ne__(self, other):
        return self._m.__ne__(other)

    def __getitem__(self, key):
        return self._m.__getitem__(key)

    def __hash__(self):
        if self._h is None:
            #TODO: do this properly
            mask = sum([ord(b) << (i * 8)
                        for (i, b) in enumerate(bytes('frzd'))])
            i = sum(list(hash(k) ^ hash(v) for (k, v) in self._m.items()))
            self._h = hash(i) ^ mask
        return self._h

    def keys(self):
        return self._m.keys()

    def items(self):
        return self._m.items()

    def values(self):
        return self._m.values()

    def get(self, key, default=None):
        return self._m.get(key, default)
