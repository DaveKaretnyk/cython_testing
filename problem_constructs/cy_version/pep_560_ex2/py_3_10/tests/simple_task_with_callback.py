# Copyright (c) 2018 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
import time

from ..i_pytask_callback import IPyTaskCallback
from ..pytask_base import PyTaskBase


class SimpleTaskWithCallbacks(PyTaskBase):
    """ Task gets the common task behavior from PyTaskBase.

    * The task writer implements this class.
    * The specialization just implements what is needed via the 'on_execute'
    method.
    """

    def __init__(self):
        super(SimpleTaskWithCallbacks, self).__init__('Simple Task With Callbacks')

    def on_execute(self):
        self.report_message('\nstarting execution...')

        time.sleep(0.5)
        self.report_message('...busy executing SimpleTaskWithCallbacks...')
        self.report_progress(23.0)

        time.sleep(0.5)
        self.report_message('...still busy executing SimpleTaskWithCallbacks...')
        self.report_progress(52.0)

        time.sleep(0.5)
        self.report_message('...still busy executing SimpleTaskWithCallbacks...')
        self.report_progress(69.0)

        time.sleep(0.5)
        self.report_message('...still busy executing SimpleTaskWithCallbacks, nearly done...')
        self.report_progress(87.0)

        time.sleep(0.5)

        self.report_message('finished execution')


class SimpleTaskWithCallbacksSink(IPyTaskCallback):
    """ Sink class implementing the callback part of the IPyTask interface.

    * The client of the task (optionally) implements this class.
    * Client implements the IPyTaskCallback interface to handle the callbacks
      setup via the corresponding IPyTask methods: subscribe_progress;
      subscribe_message; and subscribe_state_change.
    * If no callbacks are needed, simply do not subscribe and this sink is
      not required at all.
    """

    def __init__(self):
        self.state_change_callbacks = []
        self.progress_callbacks = []
        self.message_callbacks = []

    def progress_callback(self, percentage):
        self.progress_callbacks.append(percentage)

        # E.g. for a real app, this value would be passed to the UI thread asynchronously.
        print('SimpleTask callback: %age completion (progress): ', percentage)

    def message_callback(self, message):
        self.message_callbacks.append(message)
        # E.g. for a real app, this value would be passed to the UI thread asynchronously.
        print('SimpleTask callback: message: ', message)

    def message_callback2(self, message):
        self.message_callbacks.append(message)
        # E.g. for a real app, this value would be passed to the UI thread asynchronously.
        print('SimpleTask callback2: message: ', message)

    def message_callback3(self, message):
        self.message_callbacks.append(message)
        # E.g. for a real app, this value would be passed to the UI thread asynchronously.
        print('SimpleTask callback3: message: ', message)

    def state_change_callback(self, task_state):
        self.state_change_callbacks.append(task_state)
        # E.g. for a real app, this value would be passed to the UI thread asynchronously.
        print('SimpleTask callback: state change: {0}; type: {1}'.format(str(task_state),
                                                                         type(task_state)))
