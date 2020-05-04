"""Sequence data types

A sequence is an ordered multiset.  A sequence data type is a container
in which the order of the items is significant and each item may appear
more than once.

Fixed-length sequences are also known as tuples; they are represented by
:obj:`tuple` and its derivations.  Variable-length sequences are also
known as lists; they are represented by :class:`collections.Sequence`
and its derivations.

Although a sequence is a multiset, a multiset is not a set of its
contents, so a sequence is also not a set of its contents.  Therefore
the sequence APIs (:obj:`tuple` and :class:`collections.Sequence`) do
not extend the API of :class:`collections.Set`.

Also, although a sequence can be interpreted as a mapping from integers
(the positions of its contents) to its contents, it is not fundamentally
defined so.  Therefore the sequence APIs do not extend the API of
:class:`collections.Mapping`.

"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"
