# Copyright (c) 2018 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
import pytest

from ..pytask_base import PyTaskBase
from ..pytask_exceptions import (
    PyTaskAbortedException, PyTaskException, PyTaskFailedException, PyTaskInvalidStateException)
from .failing_task import (
    TaskFailsWithPyTaskAbortedException, TaskFailsWithPyTaskException,
    TaskFailsWithPyTaskFailedException,
    TaskFailsWithPyTaskInvalidStateException, TaskFailsWithPythonException)
from .simple_task import SimpleTask


diagnostics_print = True


# Can only pause a task from certain states.
def test_invalid_pause_call():
    task = SimpleTask()
    with pytest.raises(PyTaskInvalidStateException) as exception_info:
        task.pause()
    if diagnostics_print:
        print('exception raised: {0}'.format(exception_info))


# Can only resume a task from certain states.
def test_invalid_resume_call():
    task = SimpleTask()
    with pytest.raises(PyTaskInvalidStateException) as exception_info:
        task.resume()
    if diagnostics_print:
        print('exception raised: {0}'.format(exception_info))


# Can only pause a task from certain states.
def test_invalid_abort_call():
    task = SimpleTask()
    with pytest.raises(PyTaskInvalidStateException) as exception_info:
        task.abort()
    if diagnostics_print:
        print('exception raised: {0}'.format(exception_info))


# At least the 'on_execute' must be implemented by the sub-class of PyTaskBase.
def test_no_on_execute_defined():
    class BadTask(PyTaskBase):
        def __init__(self):
            super(BadTask, self).__init__('Bad Task')

    with pytest.raises(TypeError) as exception_info:
        _ = BadTask()  # noqa F841
    if diagnostics_print:
        print('exception raised: {0}'.format(exception_info))


# Python PyTaskFailedException raised in 'execute' call.
def test_failing_task_pytask_base_exception():
    task = TaskFailsWithPyTaskFailedException('Task raises PyTaskFailedException')

    with pytest.raises(PyTaskFailedException) as exception_info:
        task.execute()
    if diagnostics_print:
        print('exception raised: {0}'.format(exception_info))


# Python ZeroDivisionError raised in 'execute' call.
def test_failing_task_python_exception():
    task = TaskFailsWithPythonException('Task raises Python exception: ZeroDivisionError')

    with pytest.raises(ZeroDivisionError) as exception_info:
        task.execute()
    if diagnostics_print:
        print('exception raised: {0}'.format(exception_info))


# PyTaskAbortedException raised in 'execute' call.
def test_failing_task_py_task_aborted_exception():
    task = TaskFailsWithPyTaskAbortedException('Task raises PyTaskAbortedException')

    with pytest.raises(PyTaskAbortedException) as exception_info:
        task.execute()
    if diagnostics_print:
        print('exception raised: {0}'.format(exception_info))


# PyTaskInvalidStateException raised in 'execute' call.
def test_failing_task_Py_task_invalid_state_exception():
    name = 'Task raises PyTaskInvalidStateException'
    task = TaskFailsWithPyTaskInvalidStateException(name)

    with pytest.raises(PyTaskInvalidStateException) as exception_info:
        task.execute()
    if diagnostics_print:
        print('exception raised: {0}'.format(exception_info))


# PyTaskException raised in 'execute' call.
def test_failing_task_py_task_exception():
    task = TaskFailsWithPyTaskException('Task raises PyTaskException')

    with pytest.raises(PyTaskException) as exception_info:
        task.execute()
    if diagnostics_print:
        print('exception raised: {0}'.format(exception_info))
