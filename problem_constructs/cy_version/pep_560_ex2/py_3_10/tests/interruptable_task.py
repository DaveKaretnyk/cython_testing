# Copyright (c) 2018 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
import time

from ..i_pytask_callback import IPyTaskCallback
from ..pytask_base import PyTaskBase


class InterruptableTask(PyTaskBase):
    """ Task gets the common task behavior from PyTaskBase.

    * Just implements the required functionality via the 'on_execute' method.
    """

    def __init__(self):
        super(InterruptableTask, self).__init__('Interruptable Task')

    def on_execute(self):
        # -------------------------------------------------
        self.report_message('InterruptableTask: executing step 1...')
        time.sleep(2)
        self.report_message('InterruptableTask: step 1 done')
        self.report_progress(30.0)
        self.handle_interruption_request()

        # -------------------------------------------------
        self.report_message('InterruptableTask: executing step 2...')
        time.sleep(2)
        self.report_message('InterruptableTask: step 2 done')
        self.report_progress(60.0)
        self.handle_interruption_request()

        # -------------------------------------------------
        self.report_message('InterruptableTask: executing last step...')
        time.sleep(1)
        self.report_message('InterruptableTask: last step done')


class TaskWithInterruptableDelay(PyTaskBase):
    """ Task that contains an interruptible delay
    """

    def __init__(self, delay_ms):
        super(TaskWithInterruptableDelay, self).__init__("InterruptableDelay Task")
        self.delay = delay_ms

    def on_execute(self):
        self.interruptable_delay(self.delay)


class InterruptableTaskWithCallbacksSink(IPyTaskCallback):
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
        print('InterruptableTask callback: %age completion (progress): ', percentage)

    def message_callback(self, message):
        self.message_callbacks.append(message)
        # E.g. for a real app, this value would be passed to the UI thread asynchronously.
        print('InterruptableTask callback: message: ', message)

    def state_change_callback(self, task_state):
        self.state_change_callbacks.append(task_state)
        # E.g. for a real app, this value would be passed to the UI thread asynchronously.
        msg = 'InterruptableTask callback: state change: {0}; type: {1}'
        print(msg.format(task_state.name, type(task_state)))
