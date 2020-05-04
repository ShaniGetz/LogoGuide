"""Miscellaneous set data types"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import __builtin__
from collections import Sequence as _Sequence, Set as _Set
from functools import reduce as _reduce
from operator import xor as _xor
import oset as _oset


class set(__builtin__.set):

    """A set

    .. seealso:: :class:`set <python:set>`

    """

    def __repr__(self):
        return '{{{}}}'.format(', '.join(repr(item) for item in self)) \
               if self else 'set()'

    def __str__(self):
        return '{{{}}}'.format(', '.join(str(item) for item in self)) \
               if self else 'set()'


class frozenoset(_Set, _Sequence):

    """An immutable ordered set

    .. seealso:: :mod:`oset` from :pypi:`oset`

    """

    def __init__(self, *args, **kwargs):
        self._hash = None
        self._oset = oset(*args, **kwargs)

    def __getitem__(self, key):
        return self._oset[key]

    def __hash__(self):
        if self._hash is None:
            self._hash = _reduce(_xor, (hash(item) for item in self))
        return self._hash

    def __len__(self):
        return len(self._oset)

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, list(self))

    def __str__(self):
        return '=>{{{}}}'.format(', '.join(str(item) for item in self))


class frozenset(__builtin__.frozenset):

    """An immutable set.

    .. seealso:: :class:`frozenset <python:frozenset>`

    """

    def __repr__(self):
        return '={{{}}}'.format(', '.join(repr(item) for item in self))

    def __str__(self):
        return '={{{}}}'.format(', '.join(str(item) for item in self))


class oset(_oset.oset):

    """An ordered set.

    .. seealso:: :mod:`oset` from :pypi:`oset`

    """

    def __repr__(self):
        return '{}({!r})'.format(self.__class__.__name__, list(self))

    def __str__(self):
        return '>{{{}}}'.format(', '.join(str(item) for item in self))
