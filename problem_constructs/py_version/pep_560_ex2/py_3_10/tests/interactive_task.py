# Copyright (c) 2022 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
import time

from ..pyinteractivetask_base import PyInteractiveTaskBase


class InteractiveTask(PyInteractiveTaskBase[str, str]):
    """ Task gets the common interactive task behavior from PyInteractiveTaskBase.
    This class is implemented for use in unit tests only.

    * The task writer implements this class.
    * The specialization just implements what is needed via the 'on_execute'
    method.
    """

    def __init__(self, task_name=None):
        super(InteractiveTask, self).__init__(task_name or 'Interactive Task')
        self._user_response = None

    def on_execute(self):
        # Execution of task can report progress, messages, and state: these will only be received
        # by the client if subscription has been made.

        self.report_message('\nInteractiveTask: starting execution...')
        self.report_progress(10.0)

        self._user_response = self.request_user_response('Instruction for the user')
        self.report_message('...busy executing InteractiveTask...')
        self.report_progress(33.0)

        time.sleep(0.5)
        self.report_message('...still busy executing InteractiveTask...')
        self.report_progress(66.0)

        time.sleep(0.5)
        self.report_message('InteractiveTask: finished execution')

    def get_user_response_received(self):
        return self._user_response
