"""Converters core"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from collections import Callable as _Callable
from functools import wraps as _wraps
import sys as _sys
import types as _types

from spruce.lang import safe_name as _safe_name

from .._annotated import AnnotatedType as _AnnotatedType


def converter(totype, convertible_type_description=None,
              convertible_value_description=None):
    """Define a converter function

    This decorator wraps a function that converts input values to values of
    some type.  The resulting function behaves exactly like the wrapped
    function unless the latter indicates an invalid input by raising a
    :exc:`TypeError` or :exc:`ValueError`.  On invalid inputs, the resulting
    function raises a descriptive exception that uses the given annotations.

    The *totype* may be a class or a descriptive name.  In either case, it
    is used by the converter's exceptions to describe the intended output.

    The *convertible_type_description* and *convertible_value_description*
    are used by the converter's exceptions to describe the allowed input
    types and values.  Their default values are the corresponding properties
    of the given *totype* if it is an
    :class:`~spruce.lang._datatypes._annotated.AnnotatedType` subclass.  If
    a *convertible_type_description* is defined but a
    *convertible_value_description* is not, then the latter takes the form
    of the former with a preceding indefinite article.

    :param totype:
        The type to which values are converted.
    :type totype: :obj:`str` or :obj:`type`

    :param convertible_type_description:
        A noun phrase (without any leading article) that describes the types
        of input values that can be converted.
    :type convertible_type_description: :obj:`str` or null

    :param convertible_value_description:
        A noun phrase (with a leading article, if appropriate) that
        describes the input values that can be converted.
    :type convertible_value_description: :obj:`str` or null

    """
    def decorate_func(func):
        return _wraps(func)(Converter(func,
                                      totype=totype,
                                      convertible_type_description=
                                          convertible_type_description,
                                      convertible_value_description=
                                          convertible_value_description))
    return decorate_func


class Converter(object):

    """A converter function

    .. seealso:: :func:`converter`

    """

    def __init__(self, func, totype, convertible_type_description=None,
                 convertible_value_description=None):

        self._func = func

        if isinstance(totype, (_types.TypeType, _types.ClassType)):
            self._totype = totype
        else:
            self._totype = None

        custom_annotated_totype = False
        if any(arg is not None for arg in (convertible_type_description,
                                           convertible_value_description)):
            custom_annotated_totype = True
        else:
            for methodname in ('convertible_type_description',
                               'convertible_value_description', 'displayname',
                               'type_error', 'value_error'):
                try:
                    method = getattr(totype, methodname)
                except AttributeError:
                    custom_annotated_totype = True
                    break
                else:
                    if not isinstance(method, _Callable):
                        custom_annotated_totype = True
                        break

        if custom_annotated_totype:
            try:
                totype_displayname = totype.displayname()
            except (AttributeError, TypeError):
                try:
                    totype_displayname = totype.__name__
                except (AttributeError, TypeError):
                    totype_displayname = str(totype)

            try:
                totype_name = totype.__name__
            except AttributeError:
                totype_name = _safe_name(totype_displayname)

            annotated_totype_name = 'ConverterAnnotated_' + totype_name

            annotated_totype_bases = []
            if self.totype:
                annotated_totype_bases.append(self.totype)
            annotated_totype_bases.append(_AnnotatedType)
            annotated_totype_bases = tuple(annotated_totype_bases)

            @classmethod
            def displayname(cls):
                return totype_displayname

            convertible_type_description_ = convertible_type_description
            @classmethod
            def convertible_type_description(cls):
                return convertible_type_description_

            convertible_value_description_ = convertible_value_description
            @classmethod
            def convertible_value_description(cls):
                return convertible_value_description_

            annotated_totype_attrs = {'displayname': displayname}
            if convertible_type_description_ is not None:
                annotated_totype_attrs['convertible_type_description'] = \
                    convertible_type_description
            if convertible_value_description_ is not None:
                annotated_totype_attrs['convertible_value_description'] = \
                    convertible_value_description

            self._annotated_totype = \
                type(annotated_totype_name, annotated_totype_bases,
                     annotated_totype_attrs)

        else:
            self._annotated_totype = totype

    def __call__(self, value, *args, **kwargs):

        try:
            return self.func(value, *args, **kwargs)

        except (TypeError, ValueError) as exc:
            if isinstance(exc, TypeError):
                # TODO: (Python 3)
                #type_ = value.__class__
                type_ = type(value)
                message = str(exc)
                if not message or message == repr(type_):
                    message = None

                exc = self.type_error(type_, message)

            elif isinstance(exc, ValueError):
                message = str(exc)
                if not message or message == repr(value):
                    message = None

                exc = self.value_error(value, message)

            raise exc, None, _sys.exc_info()[2]

    @property
    def annotated_totype(self):
        return self._annotated_totype

    @property
    def func(self):
        return self._func

    @property
    def totype(self):
        return self._totype

    def type_error(self, type, message=None):
        return self.annotated_totype.conversion_type_error(type, message)

    def value_error(self, value, message=None):
        return self.annotated_totype.conversion_value_error(value, message)
