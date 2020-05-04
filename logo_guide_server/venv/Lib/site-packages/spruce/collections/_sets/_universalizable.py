"""Universalizable set data types"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
from collections import MutableSet as _MutableSet, Set as _Set
from functools import total_ordering as _total_ordering
from itertools import product as _product

from . import _misc
from .. import _exc


@_total_ordering
class uset_abc(object):

    __metaclass__ = _ABCMeta

    def __init__(self, items=None):
        if not items:
            self._items = self._items_class()(())
        elif isinstance(self, self._frozen_class()) \
             and isinstance(items, self._frozen_class()) \
             and isinstance(items._items, self._items_class()):
            self._items = items._items
        elif (isinstance(items, (self._frozen_class(),
                                 self._unfrozen_class()))
              and not items.isfinite) \
             or (isinstance(items, basestring) and items == '*'):
            self._items = self._universe()
        else:
            self._items = self._items_class()(items)

    def __and__(self, other):

        if not isinstance(other, self.__class__):
            other = self.__class__(other)

        if not self.isfinite:
            return other
        elif not other.isfinite:
            return self
        else:
            return self.__class__(self._items & other._items)

    def __contains__(self, item):
        return not self.isfinite or item in self._items

    def __eq__(self, other):

        if not isinstance(other, self.__class__):
            other = self.__class__(other)

        return self._items == other._items

    def __gt__(self, other):

        if not isinstance(other, self.__class__):
            other = self.__class__(other)

        if not other.isfinite:
            return False
        elif not self.isfinite:
            return True
        else:
            return self._items < other._items

    def __iter__(self):
        if not self.isfinite and self._universe() == self._DEFAULT_UNIVERSE:
            raise _exc.UnsupportedUniversalSetOperation('iteration', set=self)
        else:
            return iter(self._items)

    def __len__(self):
        if not self.isfinite:
            return float('inf')
        else:
            return len(self._items)

    def __lt__(self, other):

        if not isinstance(other, self.__class__):
            other = self.__class__(other)

        if not self.isfinite:
            return False
        elif not other.isfinite:
            return True
        else:
            return self._items < other._items

    def __nonzero__(self):
        return bool(self._items)

    def __or__(self, other):

        if not isinstance(other, self.__class__):
            other = self.__class__(other)

        if not self.isfinite:
            return self
        elif not other.isfinite:
            return other
        else:
            return self.__class__(self._items | other._items)

    def __repr__(self):
        return '{}({!r})'\
                .format(self.__class__.__name__,
                        self._items if self.isfinite else '*')

    def __str__(self):
        return '{{{}}}'.format(', '.join(sorted(str(item)
                                                for item in self._items))) \
                   if self.isfinite \
                   else '*'

    def __sub__(self, other):

        if not isinstance(other, self.__class__):
            other = self.__class__(other)

        if not self.isfinite:
            raise _exc.UnsupportedUniversalSetOperation('set difference',
                                                        set=self)
        elif not other.isfinite:
            return self.__class__()
        else:
            return self.__class__(self._items - other._items)

    def __xor__(self, other):

        if not isinstance(other, self.__class__):
            other = self.__class__(other)

        if not (self.isfinite or other.isfinite):
            return self.__class__()
        elif not self.isfinite:
            raise _exc.UnsupportedUniversalSetOperation('XOR', set=self)
        elif not other.isfinite:
            raise _exc.UnsupportedUniversalSetOperation('XOR', set=other)
        else:
            return self.__class__(self._items ^ other._items)

    def copy(self):
        return self.__class__(self._items.copy())

    @_abstractmethod
    def frozen(self):
        pass

    def isdisjoint(self, other):

        if not isinstance(other, self.__class__):
            other = self.__class__(other)

        if not self.isfinite:
            return not other._items
        elif not other.isfinite:
            return not self._items
        else:
            return self._items.isdisjoint(other._items)

    @property
    def isfinite(self):
        """

        .. note:: **TODO:**
            refactor as :attr:`!isuniversal` with opposite semantics

        """
        return self._items != self._universe()

    def set(self):
        if not self.isfinite:
            raise _exc.UnsupportedUniversalSetOperation\
                   ('conversion to a finite set', set=self)
        else:
            return self._items

    @_abstractmethod
    def unfrozen(self):
        pass

    @_abstractmethod
    def unfrozen_copy(self):
        pass

    _DEFAULT_UNIVERSE = object()

    @classmethod
    def _frozen_class(cls):
        return frozenuset

    @classmethod
    @_abstractmethod
    def _items_class(cls):
        pass

    @classmethod
    def _unfrozen_class(cls):
        return uset

    @classmethod
    def _universe(cls):
        return cls._DEFAULT_UNIVERSE


class frozenuset(uset_abc, _Set):

    """An immutable universalizable set

    .. seealso:: :class:`uset`

    """

    def __hash__(self):
        return hash(self._items)

    def __str__(self):
        return '=' + super(frozenuset, self).__str__()

    def frozen(self):
        return self

    @classmethod
    def _items_class(cls):
        return _misc.frozenset

    def unfrozen(self):
        return self._unfrozen_class()(self)

    def unfrozen_copy(self):
        return self.unfrozen()


class uset(uset_abc, _MutableSet):

    """A universalizable set

    A universalizable set can be universal---that is, it can represent the
    set of all possible items that it supports.

    .. note:: **TODO:**
        support set difference and XOR by storing and operating on
        compositions

    :param items:
        The items.  The value ``'*'`` has special meaning, denoting all
        possible items.
    :type items:
        :class:`uset` or :class:`frozenuset` or ~{:obj:`object`}
        or :obj:`str` or null

    """

    def __iand__(self, other):

        if not isinstance(other, self.__class__):
            other = self.__class__(other)

        if not self.isfinite:
            self._items = other._items
        elif not other.isfinite:
            pass
        else:
            self._items &= other._items

        return self

    def __ior__(self, other):

        if not isinstance(other, self.__class__):
            other = self.__class__(other)

        if not self.isfinite:
            pass
        elif not other.isfinite:
            self._items = other._items
        else:
            self._items |= other._items

        return self

    def __isub__(self, other):

        if not isinstance(other, self.__class__):
            other = self.__class__(other)

        if not self.isfinite:
            raise _exc.UnsupportedUniversalSetOperation\
                   ('in-place set difference', set=self)
        elif not other.isfinite:
            self.clear()
        else:
            self._items -= other._items

        return self

    def __ixor__(self, other):

        if not isinstance(other, self.__class__):
            other = self.__class__(other)

        if not (self.isfinite or other.isfinite):
            self.clear()
        elif not self.isfinite:
            raise _exc.UnsupportedUniversalSetOperation\
                   ('in-place XOR with a finite set', set=self)
        elif not other.isfinite:
            raise _exc.UnsupportedUniversalSetOperation\
                   ('in-place XOR with a finite set', set=other)
        else:
            self._items -= other._items

        return self

    def add(self, item):
        if not self.isfinite:
            pass
        else:
            self._items.add(item)

    def clear(self):
        self._items = self._items_class()()

    def discard(self, item):
        if not self.isfinite:
            raise _exc.UnsupportedUniversalSetOperation('discarding an item',
                                                        set=self)
        else:
            self._items.discard(item)

    def frozen(self):
        return self._frozen_class()(self)

    def unfrozen(self):
        return self

    def unfrozen_copy(self):
        return self.copy()

    @classmethod
    def _items_class(cls):
        return set


class usetset_abc(uset_abc):

    __metaclass__ = _ABCMeta

    def __init__(self, items=()):
        if not items or isinstance(items, (self._frozen_class(),
                                           self._unfrozen_class())) \
                     or (isinstance(items, basestring) and items == '*'):
            super(usetset_abc, self).__init__(items)
        else:
            self._items = self._items_class()(self._normalized_item(item)
                                              for item in items)

    def all_contain(self, item):
        return self.isfinite \
               and self._items \
               and all(item in own_item for own_item in self._items)

    def all_lt(self, item):
        return self.isfinite \
               and self._items \
               and all(own_item < item for own_item in self._items)

    def all_lte(self, item):
        return self.isfinite \
               and self._items \
               and all(own_item <= item for own_item in self._items)

    def all_gt(self, item):
        return self.isfinite \
               and self._items \
               and all(own_item > item for own_item in self._items)

    def all_gte(self, item):
        return self.isfinite \
               and self._items \
               and all(own_item >= item for own_item in self._items)

    def any_contain(self, item):
        return not self.isfinite or any(item in own_item
                                        for own_item in self._items)

    def any_eq(self, item):
        return not self.isfinite or any(own_item == item
                                        for own_item in self._items)

    def any_lt(self, item):
        return not self.isfinite or any(own_item < item
                                        for own_item in self._items)

    def any_lte(self, item):
        return not self.isfinite or any(own_item <= item
                                        for own_item in self._items)

    def any_gt(self, item):
        return not self.isfinite or any(own_item > item
                                        for own_item in self._items)

    def any_gte(self, item):
        return not self.isfinite or any(own_item >= item
                                        for own_item in self._items)

    def intersection_product(self, other):

        if not isinstance(other, usetset_abc):
            other = self.__class__(other)

        if self and other:
            return self.__class__({self._item_class()(item & other_item)
                                   for item, other_item
                                   in _product(self._items, other._items)})
        else:
            return self.__class__()

    def union_product(self, other):

        if not isinstance(other, usetset_abc):
            other = self.__class__(other)

        if self and other:
            if not self.isfinite or not other.isfinite:
                return self.__class__('*')
            else:
                return self.__class__({self._item_class()(item | other_item)
                                       for item, other_item
                                       in _product(self._items, other._items)})
        elif self:
            return self
        else:
            return other

    @classmethod
    def _frozen_class(cls):
        return frozenusetset

    @classmethod
    @_abstractmethod
    def _item_class(cls):
        pass

    @classmethod
    def _normalized_item(cls, item):
        item_class = cls._item_class()
        return item if isinstance(item, item_class) else item_class(item)

    @classmethod
    def _unfrozen_class(cls):
        return usetset


class frozenusetset(usetset_abc, frozenuset):

    """An immutable universalizable set of immutable sets

    .. seealso:: :class:`frozenuset`

    """

    @classmethod
    def _item_class(cls):
        return _misc.frozenset


class usetset(usetset_abc, uset):

    """A universalizable set of immutable sets

    .. seealso:: :class:`uset`

    """

    def add(self, item):
        if not self.isfinite:
            pass
        else:
            self._items.add(self._normalized_item(item))

    @classmethod
    def _item_class(cls):
        return _misc.frozenset
