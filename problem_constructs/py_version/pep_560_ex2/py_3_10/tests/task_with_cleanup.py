# Copyright (c) 2018 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
import time

from ..pytask_base import PyTaskBase


class TaskWithCleanup(PyTaskBase):
    """ Task gets the common task behavior from PyTaskBase.

    * The task writer implements this class.
    * The specialization just implements what is needed via the 'on_execute'
    method.
    """

    def __init__(self):
        super(TaskWithCleanup, self).__init__('Task with cleanup')

    def on_execute(self):
        try:
            print('TaskWithCleanup: starting execution...')
            time.sleep(2)
            print('TaskWithCleanup: finished execution')
        finally:
            # Code in this block is always executed when 'on_execute' completes, whether by normal
            # method return or when exception occurs.
            print('TaskWithCleanup: cleanup')
