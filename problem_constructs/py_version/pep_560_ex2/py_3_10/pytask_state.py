# Copyright (c) 2012-2018 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
import logging
from enum import IntEnum, unique

logger = logging.getLogger(__name__)


@unique
class PyTaskState(IntEnum):
    """ Codifies the basic state model of a task.

    This is the Python counterpart of teh C++ TaskState enumeration.

    Idle:       Task ready to be run.
    Running:    task running.
    Pausing:    task requested to pause but still executing.
    Aborting:   task requested to abort but still executing.
    Paused:     task paused.
    Completed:  task completed successfully.
    Failed:     task ran into an error.
    Aborted:    task completed because of external stop request.
    """

    # __order__ = 'Idle, Running, Paused, Completed, Failed, Aborted'  # define order for iterators
    Idle = 1
    Running = 2
    Pausing = 3
    Aborting = 4
    Paused = 5
    Completed = 6
    Failed = 7
    Aborted = 8

    @classmethod
    def to_int(cls, enum_value):
        """ Convert enumeration value to the equivalent int value.

        :param enum_value:
        :return: int.
        """
        return enum_value.value

    @classmethod
    def to_enum(cls, int_value):
        """ Convert int value to the equivalent enumeration value.

        :param int_value:
        :return: TaskState.
        """
        return PyTaskState(int_value)
