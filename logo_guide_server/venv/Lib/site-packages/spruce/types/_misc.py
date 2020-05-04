"""Data types miscellany"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from abc import ABCMeta as _ABCMeta
from collections import MutableSet as _MutableSet, Set as _Set
from functools import total_ordering as _total_ordering
import re as _re
from textwrap import dedent as _dedent

from . import _converters


class enum(object):

    """An enumerated type

    .. deprecated:: 0.1.0
      In Python 3.4 and higher, use :class:`enum.Enum`.  In lower versions, use
      :class:`enum.Enum` from :pypi:`enum34`.

    An :class:`!enum` object is a named set of allowed values of any type.
    It provides a means to consistently identify such a set and validate
    that a given value exists in it.

    Calling an :class:`!enum` object on a value validates that the value
    exists in the enumeration.  The :attr:`enum_values` property provides
    access to the set of allowed values.

    For example, an :class:`!enum` over the set of card suits can be
    defined as follows::

        from spruce.lang import converter as _converter, enum as _enum

        @_converter('stripped lowercase string')
        def str_strip_lower(string):
            return string.strip().lower()

        CardSuit = _enum('card suit',
                         ('clubs', 'diamonds', 'hearts', 'spades'),
                         converter=str_strip_lower)

    The resulting class can be used to validate an ``input_suit`` like so::

        suit = CardSuit(input_suit)

    The resulting ``suit`` is guaranteed to be one of the values
    {``'clubs'``, ``'diamonds'``, ``'hearts'``, ``'spades'``}.  To iterate
    over the allowed suits, use ``CardSuit.enum_values``::

        print 'the {} is one of the following: {}'\\
               .format(CardSuit.enum_displayname,
                       ', '.join(CardSuit.displayname(value)
                                 for value in sorted(CardSuit.enum_values)))

    When using literal enum values, pass them through the enum class for
    early validation and self-documentation::

        cards = ((2, CardSuit('clubs')), (5, CardSuit('hearts')))

    :param str enum_displayname:
        A display name for this enum.

    :param values:
        The allowed values.
    :type values: ~[:obj:`object`]

    :param ord:
        The values' ordinals.
    :type ord: {:obj:`object`: :obj:`int`}

    :param converter:
        A converter from acceptable input values to the canonical *values*.
    :type converter: :obj:`object` -> :obj:`object`

    :param values_attrs:
        Other attributes of the values.
    :type values_attrs: {:obj:`object`: {:obj:`object`: :obj:`object`}}

    """

    def __init__(self, enum_displayname, values, ord=None, converter=None,
                 **values_attrs):

        self._enum_displayname = enum_displayname

        if not ord:
            ord = dict(zip(values, range(len(values))))
        self._ord = ord

        self._enum_values = sorted(values, key=(lambda value: ord[value]))

        for attrname, attrvalue_by_value in values_attrs.iteritems():
            priv_attrname = '_' + attrname
            setattr(self, priv_attrname, dict(attrvalue_by_value))

            def attr(value):
                return getattr(self, priv_attrname)[value]
            attr.__name__ = attrname

            setattr(self, attrname, attr)

        @_converters.converter(enum_displayname,
                               convertible_value_description=
                                   'one of the values {{{}}}'
                                    .format(', '.join(repr(value)
                                                      for value
                                                      in self.enum_values)))
        def converter_(value):

            if converter:
                canon_value = converter(value)
            else:
                canon_value = value

            if canon_value not in self.enum_values:
                exc = None
                if converter:
                    try:
                        converter_totype_displayname = \
                            converter.annotated_totype.displayname()
                    except (AttributeError, TypeError):
                        exc = ValueError('failed after converting {!r} to'
                                         ' {!r}'
                                          .format(value, canon_value))
                    else:
                        exc = ValueError\
                                  ('failed after converting {!r} to {} {!r}'
                                    .format(value,
                                            converter_totype_displayname,
                                            canon_value))

                if not exc:
                    exc = ValueError

                raise exc

            return canon_value
        self._converter_func_ = converter_

    def __call__(self, value):
        return self._converter_func(value)

    def __instancecheck__(self, value):
        try:
            self._converter_func(value)
        except ValueError:
            return False
        else:
            return True

    def __subclasscheck__(self, type):
        try:
            type_enum_values = type.enum_values
        except AttributeError:
            return False
        return set(type_enum_values) >= set(self.enum_values)

    def displayname(self, value):
        return self._displaynames[self(value)]

    @property
    def enum_displayname(self):
        return self._enum_displayname

    @property
    def enum_values(self):
        return self._enum_values

    def ord(self, value):
        return self._ord[self(value)]

    @property
    def _converter_func(self):
        return self._converter_func_


def namedflagset_classes(classname, frozenclassname=None, baseclassname=None,
                         doc=None, frozendoc=None):

    """Classes for sets of named flags.

    This method creates a class that defines a set of flags that are valid
    for its instances.  Objects of this class contain zero or more of these
    registered flags.  These objects support the full
    :class:`collections.MutableSet` API.

    """

    if baseclassname is None:
        baseclassname = classname + 'ABC'
    if frozenclassname is None:
        frozenclassname = 'Frozen' + classname

    __doc__suffix = \
        """

        .. seealso:: :func:`spruce.lang.namedflagset_classes
                            <spruce.lang._datatypes.namedflagset_classes>`

        :param flags:
            Flags.  A union (using ``|``) of zero or more of the flags
            registered via :meth:`register_flags`.
        :type flags: ~\ :obj:`int` or :obj:`None`

        :raise TypeError:
            Raised if non-null *flags* are given that are of a type that cannot
            be converted to an :obj:`int`.

        :raise ValueError:
            Raised if non-null *flags* are given that cannot be converted to an
            :obj:`int`.

        """
    __doc__suffix = _dedent(__doc__suffix)
    basedoc_shortdoc = \
        """A set of named flags.

        .. seealso:: :class:`{}`, :class:`{}`
        """\
         .format(classname, frozenclassname)
    baseclass__doc__ = _dedent(basedoc_shortdoc) + __doc__suffix

    __metaclass__ = _ABCMeta

    def __init__(self, flags=None):
        if not flags:
            flags = 0
        try:
            flags = int(flags)
        except TypeError:
            raise TypeError('invalid flags type {!r}; expecting one that is'
                             ' accepted by {!r}'
                             .format(flags.__class__, int))
        except ValueError:
            raise ValueError('invalid flags {!r}; expecting an integer'
                              .format(flags))
        self._flags = flags

    def __and__(self, other):
        return self.__class__(int(self) & int(other))

    def __contains__(self, item):
        return item <= self

    def __eq__(self, other):
        return int(self) == int(other)

    def __int__(self):
        return self._flags

    def __iter__(self):
        for flag in self.valid_flags():
            if self.__class__(flag) in self:
                yield flag

    def __le__(self, other):
        return (int(self) & int(other)) == int(self)

    def __len__(self):
        return sum(1 for flag in self.valid_flags()
                   if self.__class__(flag) in self)

    def __nonzero__(self):
        return bool(int(self))

    def __or__(self, other):
        return self.__class__(int(self) | int(other))

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__,
                               ' | '.join(self.flag_name(flag)
                                          for flag in self._repr_flags))

    def __sub__(self, other):
        return self.__class__(int(self) - int(other))

    def __str__(self):
        return '{{{}}}'.format(', '.join(self.flag_displayname(flag)
                                         for flag in self._repr_flags))

    def __xor__(self, other):
        return self.__class__(int(self) ^ int(other))

    def copy(self):
        return self.__class__(self)

    @classmethod
    def flag_displayname(cls, flag):
        try:
            return cls._flags_displaynames[flag]
        except KeyError:
            raise ValueError('invalid {} flag {!r}'.format(cls.__name__, flag))

    @classmethod
    def flag_name(cls, flag):
        try:
            return cls._flags_names[flag]
        except KeyError:
            raise ValueError('invalid {} flag {!r}'.format(cls.__name__, flag))

    @classmethod
    def register_flag(cls, name, displayname=None, implied=None):

        flag = cls._frozenclass(cls._reserve_next_flag_value())
        if implied:
            flag |= implied

        cls._flags_names[flag] = name

        if displayname is None:
            displayname = name
        cls._flags_displaynames[flag] = displayname

        return flag

    @classmethod
    def valid_flags(cls):
        return cls._flags_names.keys()

    _flags_displaynames = {}

    _flags_names = {}

    _next_flag_value = 1

    @property
    def _repr_flags(self):
        flags = []
        f = int(self)
        for flag in reversed(sorted(int(flag) for flag in self.valid_flags())):
            if flag & f == flag:
                flags.append(flag)
                f -= flag
        return reversed(flags)

    @classmethod
    def _reserve_next_flag_value(cls):
        value = cls._next_flag_value
        cls._next_flag_value <<= 1
        return value

    baseclass_attrs = {'__doc__': baseclass__doc__,
                       '__metaclass__': __metaclass__,
                       '__init__': __init__,
                       '__and__': __and__,
                       '__contains__': __contains__,
                       '__eq__': __eq__,
                       '__int__': __int__,
                       '__iter__': __iter__,
                       '__le__': __le__,
                       '__len__': __len__,
                       '__nonzero__': __nonzero__,
                       '__or__': __or__,
                       '__repr__': __repr__,
                       '__str__': __str__,
                       '__xor__': __xor__,
                       'copy': copy,
                       'flag_displayname': flag_displayname,
                       'flag_name': flag_name,
                       'register_flag': register_flag,
                       'valid_flags': valid_flags,
                       '_flags_displaynames': _flags_displaynames,
                       '_flags_names': _flags_names,
                       '_next_flag_value': _next_flag_value,
                       '_repr_flags': _repr_flags,
                       '_reserve_next_flag_value': _reserve_next_flag_value,
                       }

    baseclass = _total_ordering(type(baseclassname, (_Set,), baseclass_attrs))

    if frozendoc is None:
        frozendoc = basedoc_shortdoc
    frozenclass__doc__ = _dedent(frozendoc) + __doc__suffix

    def __hash__(self):
        return hash(self._flags)

    frozenclass_attrs = {'__doc__': frozenclass__doc__, '__hash__': __hash__}
    frozenclass = type(frozenclassname, (baseclass,), frozenclass_attrs)
    baseclass._frozenclass = frozenclass

    if doc is None:
        doc = basedoc_shortdoc
    mutableclass__doc__ = _dedent(doc) + __doc__suffix

    def __iand__(self, other):
        self._flags &= int(other)
        return self

    def __ior__(self, other):
        self._flags |= int(other)
        return self

    def __isub__(self, other):
        self._flags -= int(other)
        return self

    def __ixor__(self, other):
        self._flags ^= int(other)
        return self

    def add(self, item):
        self._flags |= int(item)

    def discard(self, item):
        self._flags &= ~int(item)

    mutableclass_attrs = {'__doc__': mutableclass__doc__, '__iand__': __iand__,
                          '__ior__': __ior__, '__ixor__': __ixor__, 'add': add,
                          'discard': discard}
    mutableclass = type(classname, (baseclass, _MutableSet),
                        mutableclass_attrs)
    baseclass._mutableclass = mutableclass

    return baseclass, mutableclass, frozenclass


# TODO: (Python 2.7.2)
#regex_class = _re.compile('').__class__
regex_class = type(_re.compile(''))
