'''MultiDict:  Stores tuples in a dict.  Each element of the tuple is stored
in a separate dict.
'''

from collections import namedtuple, Mapping, MutableMapping


__all__ = ['FrozenMultiDict', 'MultiDict']


class MultiDictBase(Mapping):
    '''An abstract source.   This is a read-only dict-like object that maps key
    strings to a user-defined tuple of objects.  The length of the tuple is the
    same for all ids.  Each element of the tuple is called a "part", and each
    part is stored in a separate Mapping.
    '''
    def __init__(self, parts):
        '''
        :param parts: (name, Mapping) tuples 
        :type parts: sequence of (str, Mapping) 
        '''
        self._order = [name for (name, _) in parts]
        self._parts = {name: part for (name, part) in parts}
        self.itype = namedtuple(self.__class__.__name__ + '_itype',
                                ' '.join(self._order))
        self._keys = set()
        for p in self._parts.values():
            self._keys.update(p.keys())

    def get_part(self, part_name, key):
        '''get one tuple part associated with an key.
        
        :param key: the key to look up.
        :type key: str
        :return: the part of the tupleassociated with the given key.
        '''
        return self._parts[part_name][key]

    def __len__(self):
        return len(self._keys)

    def __iter__(self):
        for k in self.keys():
            yield k

    def __contains__(self, key):
        return key in self._keys

    def __eq__(self, other):
        sk = self._keys
        ok = set(other.keys())
        if len(sk.difference(ok)) > 0:
            return False
        for k, v in self.items():
            if v != other[k]:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, key):
        result = []
        for n in self._order:
            try:
                part = self.get_part(n, key)
            except KeyError:
                raise KeyError(repr(key))
            result.append(part)
        return self.itype(*result)

    def keys(self):
        for k in self._keys:
            yield k

    def items(self):
        for k in self.keys():
            yield (k, self.get(k))

    def values(self):
        for k in self.keys():
            yield self.get(k)

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default


class FrozenMultiDict(MultiDictBase):
    '''A read-only MultiDict'''
    def __init__(self, parts):
        super(FrozenMultiDict, self).__init__(parts)
        self._h = None

    def __hash__(self):
        if self._h is None:
            self._h = hash(frozenset(self.items()))
        return self._h


class MultiDict(MultiDictBase, MutableMapping):
    '''A read-write version of ItemSource
    '''

    def __setitem__(self, key, value):
        self._keys.add(key)
        for i, n in enumerate(self._order):
            self._put_part(n, key, value[i])

    def __delitem__(self, key):
        for n in self._order:
            self._del_part(n, key)
        self._keys.remove(key)

    def _put_part(self, part_name, key, value):
        '''Put an value into a part.
        
        :param part_name: part_name to use for storage
        :type part_name: str
        :param key: the key to associate with this value
        :param value: the value to store
        :type value: a tuple with the same length as the number of writers,
          each tuple element must be appropriate for the associated writer.
        '''
        self._parts[part_name][key] = value

    def _del_part(self, part_name, key):
        '''delete a key from a part.
        
        :param part_name: part_name to use for storage
        :type part_name: str
        :param key: the key to delete
        '''
        del self._parts[part_name][key]

