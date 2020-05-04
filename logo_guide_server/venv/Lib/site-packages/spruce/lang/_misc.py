"""Python language extensions miscellany"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import re as _re


def safe_name(name, default_str='_'):
    """Convert a name to a safe object name

    The object name is "safe" in the sense that it consists only of
    characters that are allowed in object names in Python source code.
    Unallowed characters in the given *name* are replaced with
    *default_str*.

    :param str name:
        A name.

    :param str default_str:
        A string with which to replace unallowed characters.

    :rtype: str

    """
    safe_name_ = _re.sub(r'^[^\w]', default_str, name)
    safe_name_ = _re.sub(r'[^\d\w]', default_str, safe_name_)
    if not safe_name_:
        raise ValueError('cannot convert {!r} to a safe object name'
                          .format(name))
    return safe_name_


def safe_classname(name, default_str='_'):
    """Convert a name to a safe class name

    This function passes its arguments through :func:`safe_name` and
    converts the result to CamelCase.

    :rtype: str

    """
    classname = ''.join(word.title() for word in safe_name(name).split('_')
                        if word)
    if not classname:
        raise ValueError('cannot convert {!r} to a safe class name'
                          .format(name))
    return classname
