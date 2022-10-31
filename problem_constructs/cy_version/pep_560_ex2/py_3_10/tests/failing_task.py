# Copyright (c) 2018 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
from ..pytask_base import PyTaskBase
from ..pytask_exceptions import (
    PyTaskAbortedException, PyTaskException, PyTaskFailedException,
    PyTaskInvalidStateException)


class TaskFailsWithPyTaskFailedException(PyTaskBase):
    def __init__(self, task_name):
        super(TaskFailsWithPyTaskFailedException, self).__init__(task_name)

    def on_execute(self):
        print('\nstarting execution...')
        raise PyTaskFailedException('task failed with Python PyTaskFailedException')


class TaskFailsWithPythonException(PyTaskBase):
    def __init__(self, task_name):
        super(TaskFailsWithPythonException, self).__init__(task_name)

    def on_execute(self):
        print('\nstarting execution...')
        raise ZeroDivisionError('task failed with Python ZeroDivisionError')


class TaskFailsWithPyTaskAbortedException(PyTaskBase):
    def __init__(self, task_name):
        super(TaskFailsWithPyTaskAbortedException, self).__init__(task_name)

    def on_execute(self):
        print('\nstarting execution...')
        self.abort()
        raise PyTaskAbortedException('task failed with PyTaskAbortedException')


class TaskFailsWithPyTaskInvalidStateException(PyTaskBase):
    def __init__(self, task_name):
        super(TaskFailsWithPyTaskInvalidStateException, self).__init__(task_name)

    def on_execute(self):
        print('\nstarting execution...')
        raise PyTaskInvalidStateException('task failed with PyTaskInvalidStateException')


class TaskFailsWithPyTaskException(PyTaskBase):
    def __init__(self, task_name):
        super(TaskFailsWithPyTaskException, self).__init__(task_name)

    def on_execute(self):
        print('\nstarting execution...')
        raise PyTaskException('task failed with PyTaskException')
