"""Exceptions"""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import exceptions as _py_exc


class Exception(_py_exc.Exception):
    pass


class Error(RuntimeError, Exception):
    pass


class UnsupportedUniversalSetOperation(Error):

    """
    A finite set operation was attempted on a universal set

    :param operation:
        The attempted operation.
    :type operation: :obj:`str`

    :param message:
        A message that describes the error.
    :type message: :obj:`str` or null

    """

    def __init__(self, operation, set, message=None, *args):
        super(UnsupportedUniversalSetOperation, self)\
         .__init__(operation, set, message, *args)
        self._message = message
        self._operation = operation
        self._set = set

    def __str__(self):
        message = '{} is unsupported by the universal set {!r}'\
                   .format(self.operation, self.set)
        if self.message:
            message += ': ' + self.message
        return message

    @property
    def message(self):
        return self._message

    @property
    def operation(self):
        return self._operation

    @property
    def set(self):
        return self._set
