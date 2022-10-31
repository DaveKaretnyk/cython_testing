# Copyright (c) 2018 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
import time

from ..pytask_base import PyTaskBase


class SimpleTask(PyTaskBase):
    """ Task gets the common task behavior from PyTaskBase.

    * The task writer implements this class.
    * The specialization just implements what is needed via the 'on_execute'
    method.
    """

    def __init__(self):
        super(SimpleTask, self).__init__('Simple Task')

    def on_execute(self):
        # Execution of task can report progress, messages, and state: these will only be received
        # by the client if subscription has been made.

        self.report_message('\nSimpleTask: starting execution...')

        time.sleep(0.5)
        self.report_message('...busy executing SimpleTask...')
        self.report_progress(33.0)

        time.sleep(0.5)
        self.report_message('...still busy executing SimpleTask...')
        self.report_progress(66.0)

        time.sleep(0.5)
        self.report_message('SimpleTask: finished execution')
