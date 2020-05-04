"""String converters"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from . import _core as _converters_core


@_converters_core.converter('hexadecimal integer')
def hex_int(value):
    return int(value, base=16)


@_converters_core.converter('string')
def string(value):
    return unicode(value)
