"""
Created on Aug 19, 2011

@author: Dan Bullok
"""

__all__ = ['ImmutableDictChain', 'DictChain']
from collections import Mapping, MutableMapping


class ImmutableDictChain(Mapping):
    '''A chain of dictionaries.  None of the dictionaries in the chain can be
    modified through this class.  Dictionaries in the chain override the
    dictionaries that occur later in the chain.
    '''

    def __init__(self, dicts):
        self._dicts = [d for d in dicts]

    def __len__(self):
        return len(self.keys())

    def __iter__(self):
        for k in self.keys():
            yield k

    def __contains__(self, key):
        return key in self.keys()

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for (k, v) in self.items():
            if v != other[k]:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, key):
        for d in self._dicts:
            try:
                return d[key]
            except KeyError:
                pass

    def keys(self):
        s = set()
        for d in self._dicts:
            s.update(d.keys())
        return s

    def items(self):
        for k in self.keys():
            yield (k, self[k])

    def values(self):
        for k in self.keys():
            yield self[k]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def dicts(self):
        ''':return: the dicts that make up this chain
        :rtype:hb iterator over Mappings
        '''
        for d in self._dicts:
            yield d

    def append(self, d):
        '''Add a dict to the end of the chain.
        
        :param d: the dict to add
        :type d: Mapping
        '''
        self._dicts.append(d)

    def prepend(self, d):
        '''Add a dict to the beginning of the chain.
        
        :param d: the dict to add
        :type d: Mapping
        '''
        self._dicts.insert(0, d)

    def remove(self, d):
        '''Remove a dict from the chain.
        
        :param d: the dict to remove
        :type d: Mapping
        '''
        self._dicts.remove(d)


class DictChain(ImmutableDictChain, MutableMapping):
    '''A chain of dictionaries.  The dictionaries can be modified.  Setting a
    key modifies only the first dictionary in the chain.  Deleting a key 
    removes it from whichever dictionary it was in.'''

    def __setitem__(self, key, value):
        self._dicts[0][key] = value

    def __delitem__(self, key):
        for d in self._dicts:
            try:
                del d[key]
            except KeyError:
                pass
        raise KeyError(repr(key))

