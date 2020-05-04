"""Annotated types"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod

import spruce.exc as _sexc


class AnnotatedType(object):

    __metaclass__ = _ABCMeta

    @classmethod
    def convertible_type_description(cls):
        return None

    @classmethod
    def convertible_value_description(cls):
        if cls.convertible_type_description():
            if any(cls.convertible_type_description().startswith(vowel)
                   for vowel in ('a', 'e', 'i', 'o', 'u')):
                article = 'an'
            else:
                article = 'a'

            return '{} {}'.format(article, cls.convertible_type_description())
        else:
            return None

    @classmethod
    def conversion_type_error(cls, type, message=None):
        return _sexc.ConversionTypeError(type, cls.displayname(),
                                         cls.convertible_type_description(),
                                         message)

    @classmethod
    def conversion_value_error(cls, value, message=None):
        return _sexc.ConversionValueError(value, cls.displayname(),
                                          cls.convertible_value_description(),
                                          message)

    @classmethod
    @_abstractmethod
    def displayname(cls):
        pass

    @classmethod
    def type_error(cls, type, message=None):
        return _sexc.TypeError(type, cls.displayname(),
                               cls.convertible_type_description(), message)

    @classmethod
    def value_error(cls, value, message=None):
        return _sexc.ValueError(value, cls.displayname(),
                                cls.convertible_value_description(), message)
