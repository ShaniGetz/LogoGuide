"""Miscellaneous mapping data types"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from collections \
    import Mapping as _Mapping, MutableMapping as _MutableMapping, \
           OrderedDict as _OrderedDict
from functools import reduce as _reduce
from operator import xor as _xor

import multimap as _multimap
from spruce.types import require_isinstance as _require_isinstance


class _mdict_base(_multimap.MultiMap):

    def __init__(self, mapping_or_items=None):
        if mapping_or_items is None:
            super(_mdict_base, self).__init__(())
        elif hasattr(mapping_or_items, 'allitems'):
            super(_mdict_base, self).__init__(mapping_or_items.allitems())
        else:
            super(_mdict_base, self).__init__(mapping_or_items)

    def __repr__(self):
        # FIXME: make printed representations behave similarly to those of
        #   :obj:`list` and :obj:`dict`, converting the delimiters of long
        #   containers from ', ' to ',\n'
        return '{}({!r})'.format(self.__class__.__name__, self.allitems())

    def __str__(self):
        # FIXME: make printed representations behave similarly to those of
        #   :obj:`list` and :obj:`dict`, converting the delimiters of long
        #   containers from ', ' to ',\n'
        return '+{{{}}}'.format(', '.join('{}: {}'.format(key, value)
                                          for key, value in self.allitems()))


class _odict_base(_OrderedDict):

    def __repr__(self):
        # FIXME: make printed representations behave similarly to those of
        #   :obj:`list` and :obj:`dict`, converting the delimiters of long
        #   containers from ', ' to ',\n'
        return '{}({!r})'.format(self.__class__.__name__, self.items())

    def __str__(self):
        # FIXME: make printed representations behave similarly to those of
        #   :obj:`list` and :obj:`dict`, converting the delimiters of long
        #   containers from ', ' to ',\n'
        return '>{{{}}}'.format(', '.join('{}: {}'.format(key, value)
                                          for key, value in self.items()))


class _omdict_base(_mdict_base):
    # NOTE: this is nearly identical to :class:`_mdict_base` because that
    #   class's underlying implementation happens to be ordered
    def __str__(self):
        return '>' + super(_omdict_base, self).__str__()


class _typeddict_base(_Mapping):

    def __init__(self, mapping_or_items=None, keytype=None, key_converter=None,
                 valuetype=None, value_converter=None):

        if not keytype:
            raise TypeError('missing key type')

        if not valuetype:
            raise TypeError('missing value type')

        self._key_converter = key_converter if key_converter is not None \
                                            else keytype
        self._keytype = keytype
        self._value_converter = value_converter \
                                    if value_converter is not None \
                                    else valuetype
        self._valuetype = valuetype

        if mapping_or_items:
            if isinstance(mapping_or_items, typeddict) \
                   and issubclass(mapping_or_items.keytype, self.keytype) \
                   and issubclass(mapping_or_items.valuetype, self.valuetype):
                self._dict = self._dicttype()(mapping_or_items._dict)
            else:
                self._dict = self._dicttype()()
                if isinstance(mapping_or_items, _Mapping):
                    items = mapping_or_items.items()
                else:
                    items = mapping_or_items
                for key, value in items:
                    self._setitem(key, value)
        else:
            self._dict = self._dicttype()()

    def __getitem__(self, key):
        return self._dict[key]

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        # FIXME: make printed representations behave similarly to those of
        #   :obj:`list` and :obj:`dict`, converting the delimiters of long
        #   containers from ', ' to ',\n'
        return '{}({!r}, keytype={!r}, valuetype={!r})'\
                .format(self.__class__.__name__, self._dict, self.keytype,
                        self.valuetype)

    def __str__(self):
        # FIXME: make printed representations behave similarly to those of
        #   :obj:`list` and :obj:`dict`, converting the delimiters of long
        #   containers from ', ' to ',\n'
        return '{{{}}}'.format(', '.join('{}: {}'.format(key, value)
                                         for key, value in self.items()))

    @property
    def key_converter(self):
        return self._key_converter

    @property
    def keytype(self):
        return self._keytype

    @property
    def value_converter(self):
        return self._value_converter

    @property
    def valuetype(self):
        return self._valuetype

    @classmethod
    def _dicttype(cls):
        return dict

    def _normalized_key(self, key):
        try:
            _require_isinstance(key, self.keytype)
        except ValueError:
            if self.key_converter:
                return self.key_converter(key)
            else:
                raise
        else:
            return key

    def _normalized_value(self, value):
        try:
            _require_isinstance(value, self.valuetype)
        except ValueError:
            if self.value_converter:
                return self.value_converter(value)
            else:
                raise
        else:
            return value

    def _setitem(self, key, value):
        self._dict[self._normalized_key(key)] = self._normalized_value(value)


class defaultmapping(_MutableMapping):

    def __init__(self, mapping, default_factory):
        self._default_factory = default_factory
        self._mapping = mapping

    def __delitem__(self, key):
        del self.mapping[key]

    def __getitem__(self, key):
        try:
            return self.mapping[key]
        except KeyError:
            value = self.default_factory()
            self.mapping[key] = value
            return value

    def __iter__(self):
        return iter(self.mapping)

    def __len__(self):
        return len(self.mapping)

    def __repr__(self):
        return '{}({!r}, {!r})'.format(self.__class__.__name__, self.mapping,
                                       self.default_factory)

    def __setitem__(self, key, value):
        self.mapping[key] = value

    def __str__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.mapping,
                                   self.default_factory)

    @property
    def default_factory(self):
        return self._default_factory

    @property
    def mapping(self):
        return self._mapping


class frozendict(_Mapping):

    """An immutable mapping"""

    def __init__(self, *args, **kwargs):
        self._dict = dict(*args, **kwargs)
        self._hash = None

    def __getitem__(self, key):
        return self._dict[key]

    def __hash__(self):
        if self._hash is None:
            self._hash = _reduce(_xor,
                                 (hash(pair) for pair in self.iteritems()))
        return self._hash

    def __iter__(self):
        return iter(self._dict)

    def __len__(self):
        return len(self._dict)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.items())

    def __str__(self):
        return str(self._dict)


class frozenmdict(_mdict_base):

    """An immutable multimap

    .. seealso:: :class:`multimap.MultiMap` from :pypi:`multimap`

    :param mapping_or_items:
        A mapping or a sequence of *(key, value)* items.
    :type mapping_or_items: ~+{:obj:`object`: :obj:`object`} or null

    """

    def __init__(self, mapping_or_items=None):
        super(frozenmdict, self).__init__(mapping_or_items)
        self._hash = None

    def __hash__(self):
        if self._hash is None:
            self._hash = _reduce(_xor,
                                 (hash(pair) for pair in self.iterallitems()))
        return self._hash

    def __str__(self):
        return '=' + super(frozenmdict, self).__str__()


class frozenodict(_Mapping):

    """An immutable ordered mapping

    .. seealso:: :class:`odict`

    """

    def __init__(self, *args, **kwargs):
        self._hash = None
        self._odict = odict(*args, **kwargs)

    def __getitem__(self, key):
        return self._odict[key]

    def __hash__(self):
        if self._hash is None:
            self._hash = _reduce(_xor,
                                 (hash(pair) for pair in self.iteritems()))
        return self._hash

    def __iter__(self):
        return iter(self._odict)

    def __len__(self):
        return len(self._odict)

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, self.items())

    def __str__(self):
        return '=' + str(self._odict)


class frozenomdict(_omdict_base):

    """An immutable ordered multimap

    .. seealso:: :class:`multimap.MultiMap` from :pypi:`multimap`

    :param mapping_or_items:
        A mapping or a sequence of *(key, value)* items.
    :type mapping_or_items: ~+{:obj:`object`: :obj:`object`} or null

    """

    def __init__(self, mapping_or_items=None):
        super(frozenomdict, self).__init__(mapping_or_items)
        self._hash = None

    def __hash__(self):
        if self._hash is None:
            self._hash = _reduce(_xor,
                                 (hash(pair) for pair in self.iterallitems()))
        return self._hash

    def __str__(self):
        return '=' + super(frozenomdict, self).__str__()


class frozentypeddict(_typeddict_base):

    """An immutable typed mapping

    .. seealso:: :class:`typeddict`

    """

    def __init__(self, mapping_or_items=None, keytype=None, key_converter=None,
                 valuetype=None, value_converter=None):
        super(frozentypeddict, self)\
         .__init__(mapping_or_items, keytype=keytype,
                   key_converter=key_converter, valuetype=valuetype,
                   value_converter=value_converter)
        self._hash = None

    def __hash__(self):
        if self._hash is None:
            self._hash = _reduce(_xor,
                                 (hash(pair) for pair in self.iteritems()),
                                 hash(self._dicttype()))
        return self._hash

    def __str__(self):
        return '=' + super(frozentypeddict, self).__str__()


class frozentypedmdict(frozentypeddict):
    """An immutable typed multimap

    .. seealso:: :class:`frozentypeddict`, :class:`frozenmdict`

    .. note:: **TODO:**
        support the full API of :class:`frozenmdict`

    """
    @classmethod
    def _dicttype(cls):
        return frozenmdict


class frozentypedodict(frozentypeddict):
    """An immutable typed ordered mapping

    .. seealso:: :class:`frozentypeddict`, :class:`frozenodict`

    """
    @classmethod
    def _dicttype(cls):
        return frozenodict


class frozentypedomdict(frozentypeddict):
    """An immutable typed ordered multimap

    .. seealso:: :class:`frozentypeddict`, :class:`frozenomdict`

    .. note:: **TODO:**
        support the full API of :class:`frozenomdict`

    """
    @classmethod
    def _dicttype(cls):
        return frozenomdict


class mdict(_mdict_base, _multimap.MutableMultiMap):
    """A multimap

    If a *mapping_or_items* is given, then the multimap is initialized with
    the items in it.  If the *mapping_or_items* is a multimap (that is, if
    it has a method :meth:`!allitems` that, when called, returns a sequence
    of all *(key, value)* items), then the new multimap is initialized with
    all of the items in *mapping_or_items*.  This is different from the
    behavior of :class:`multimap.MultiMap`, which treats all mappings the
    same.

    .. seealso:: :class:`multimap.MutableMultiMap` from :pypi:`multimap`

    :param mapping_or_items:
        A mapping or a sequence of *(key, value)* items.
    :type mapping_or_items: ~+{:obj:`object`: :obj:`object`} or null

    """
    pass


class odict(_odict_base):
    """An ordered mapping

    .. seealso:: :class:`collections.OrderedDict`

    """
    pass


class omdict(_omdict_base, _multimap.MutableMultiMap):
    """An ordered multimap

    .. seealso:: :class:`mdict`

    """
    pass


class typeddict(_typeddict_base, _MutableMapping):

    """A typed mapping

    This is a mapping from keys of a particular type to values of a
    particular type.  In addition to the basic mapping functionality, it
    validates its keys and values.

    The keys and values assigned to this mapping are validated using
    :func:`spruce.lang.require_isinstance()
    <spruce.lang._datatypes._checking.require_isinstance>`.  It is
    recommended to specify *keytype* and *valuetype* as subclasses of
    :class:`spruce.lang.AnnotatedType
    <spruce.lang._datatypes._annotated.AnnotatedType>` to ensure good error
    messages in case validation fails and normalization is not available.

    If validation fails for a key or value, then it is optionally normalized
    before being added.  This happens for keys as follows (values are
    handled similarly using the corresponding arguments).  If a key *K* is
    assigned for which :samp:`isinstance({K}, {keytype})`
    returns false, then the following operation takes place:

      * If *key_converter* is neither null nor false, then the assigned key
        is :samp:`{key_converter}({K})`.

      * If *key_converter* is null, then the assigned key is
        :samp:`{keytype}({K})`.

      * If *key_converter* is not null but false, then an error is raised as
        by :samp:`spruce.lang.require_isinstance({K}, {keytype})`.

    :param mapping_or_items:
        A mapping or item sequence of initial items.
    :type mapping_or_items:
        ~{(~\ *keytype* or ~\ *key_converter*): \
              (~\ *valuetype* or ~\ *value_converter*)}
        or null

    :param type keytype:
        The key type.

    :param type valuetype:
        The value type.

    :param key_converter:
        A callable that normalizes invalid keys.
    :type key_converter: :obj:`object` -> :obj:`object`

    :param value_converter:
        A callable that normalizes invalid values.
    :type value_converter: :obj:`object` -> :obj:`object`

    :raise TypeError:
        Raised if:

          * one or more of the keys of *mapping_or_items* is not an
            instance of *keytype* and *key_converter* is false but not
            null; or

          * one or more of the values of *mapping_or_items* is not an
            instance of *valuetype* and *value_converter* is false but not
            null.

    :raise:
        Other exceptions may be raised by *key_converter*, *keytype*,
        *value_converter*, or *valuetype* if they are called by the
        normalization behavior described above.

    """

    def __delitem__(self, key):
        del self._dict[key]

    def __setitem__(self, key, value):
        self._setitem(key, value)


class typedmdict(typeddict):
    """A typed multimap

    .. seealso:: :class:`typeddict`, :class:`mdict`

    .. note:: **TODO:**
        support the full API of :class:`mdict`

    """
    @classmethod
    def _dicttype(cls):
        return mdict


class typedodict(typeddict):
    """A typed ordered mapping

    .. seealso:: :class:`typeddict`, :class:`odict`

    """
    @classmethod
    def _dicttype(cls):
        return odict


class typedomdict(typeddict):
    """A typed ordered multimap

    .. seealso:: :class:`typeddict`, :class:`omdict`

    .. note:: **TODO:**
        support the full API of :class:`omdict`

    """
    @classmethod
    def _dicttype(cls):
        return omdict
