"""Container data types

This is an extension of :mod:`collections` and the built-in mapping_,
sequence_, and set_ data types.


.. _mapping: \
    http://docs.python.org/2/library/stdtypes.html#mapping-types-dict

.. _sequence: \
    http://docs.python.org/2/library/stdtypes.html#sequence-types-str-unicode-list-tuple-bytearray-buffer-xrange

.. _set: \
    http://docs.python.org/2/library/stdtypes.html#set-types-set-frozenset

"""

__version__ = "0.2.3"
__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__credits__ = ["Ivan D Vasin"]
__maintainer__ = "Ivan D Vasin"
__email__ = "nisavid@gmail.com"
__docformat__ = "restructuredtext"

from ._exc import *
from ._mappings import *
from ._sequences import *
from ._sets import *
