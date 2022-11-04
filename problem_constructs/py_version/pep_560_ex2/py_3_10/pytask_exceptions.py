# Copyright (c) 2012-2018 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.


class PyTaskException(Exception):
    """ General Task Exception.

    Base class for all exceptions thrown by the PyTask module.
    """
    pass


class PyTaskAbortedException(PyTaskException):
    """ Task has been aborted due to an external request.
    """
    pass


class PyTaskFailedException(PyTaskException):
    """ Task has failed for some reason.

    More information should be supplied in the exception message.
    """
    pass


class PyTaskInvalidStateException(PyTaskException):
    """ Task state invalid.

    More information should be supplied in the exception message. E.g. task
    execute cannot be started in the current state.
    """
    pass


class PyTaskNotSupportedException(PyTaskException):
    """ Feature associated with task is not supported.

    There can be multiple reasons: there is no valid license available for the
    task; the task is not supported by the running TEM server version or the
    system configuration is not supported by the task.
    """
    pass
