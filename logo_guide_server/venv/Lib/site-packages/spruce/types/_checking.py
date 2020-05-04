"""Type checking"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import spruce.exc as _sexc


def require_isinstance(value, type, type_displayname=None,
                       inst_description=None):
    if not isinstance(value, type):
        type_displayname = type_displayname or _type_displayname(type)

        if inst_description is None:
            try:
                inst_description = type.convertible_value_description()
            except (AttributeError, TypeError):
                pass

        raise _sexc.ValueError(value, type_displayname, inst_description)


def require_issubclass(subtype, type, type_displayname=None,
                       type_description=None):
    if not issubclass(subtype, type):
        type_displayname = type_displayname or _type_displayname(type)

        if type_description is None:
            try:
                type_description = type.convertible_type_description()
            except (AttributeError, TypeError):
                pass

        raise _sexc.TypeError(subtype, type_displayname, type_description)


def _type_displayname(type):
    if isinstance(type, tuple):
        type_displayname_items = []
        for type_item in type:
            try:
                type_item_displayname = type_item.displayname()
            except (AttributeError, TypeError):
                type_item_displayname = str(type_item)
            type_displayname_items.append(type_item_displayname)

        return str(tuple(type_displayname_items))

    else:
        try:
            return type.displayname()
        except (AttributeError, TypeError):
            try:
                return type.__name__
            except AttributeError:
                return str(type)
