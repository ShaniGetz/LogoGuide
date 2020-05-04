"""Numeric converters"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import __builtin__

from . import _core as _converters_core


# float variants --------------------------------------------------------------


@_converters_core.converter('floating point number')
def float(value):
    return __builtin__.float(value)


@_converters_core.converter('negative floating point number')
def neg_float(value):
    value = __builtin__.float(value)
    if value >= 0:
        raise ValueError
    return value


@_converters_core.converter('non-negative floating point number')
def nonneg_float(value):
    value = __builtin__.float(value)
    if value < 0:
        raise ValueError
    return value


@_converters_core.converter('non-positive floating point number')
def nonpos_float(value):
    value = __builtin__.float(value)
    if value > 0:
        raise ValueError
    return value


@_converters_core.converter('positive floating point number')
def pos_float(value):
    value = __builtin__.float(value)
    if value <= 0:
        raise ValueError
    return value


# int variants ----------------------------------------------------------------


@_converters_core.converter('integer')
def int(value):
    return __builtin__.int(value)


@_converters_core.converter('negative integer')
def neg_int(value):
    value = __builtin__.int(value)
    if value >= 0:
        raise ValueError
    return value


@_converters_core.converter('non-negative integer')
def nonneg_int(value):
    value = __builtin__.int(value)
    if value < 0:
        raise ValueError
    return value


@_converters_core.converter('non-positive integer')
def nonpos_int(value):
    value = __builtin__.int(value)
    if value > 0:
        raise ValueError
    return value


@_converters_core.converter('positive integer')
def pos_int(value):
    value = __builtin__.int(value)
    if value <= 0:
        raise ValueError
    return value
