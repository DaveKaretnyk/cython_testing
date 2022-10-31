# Copyright (c) 2012-2019 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.

from threading import Thread
from time import sleep

import unittest
import pytest

from ..pytask_exceptions import PyTaskAbortedException, PyTaskInvalidStateException
from ..pytask_state import PyTaskState
from ..pytask_state_machine import TaskStateMachine


class TestButton(unittest.TestCase):
    def setUp(self):
        self.returned_state = PyTaskState.Idle

    def _handler(self, state):
        self.returned_state = state

    def test_state_change_emit(self):
        sm = TaskStateMachine()
        sm.subscribe_state_change(self._handler)
        sm.handle_execute_request()
        assert sm._state == PyTaskState.Running
        assert self.returned_state == PyTaskState.Running

        sm.handle_task_failed()
        assert sm._state == PyTaskState.Failed
        assert self.returned_state == PyTaskState.Failed

    def test_correct_transitions(self):
        sm = TaskStateMachine()

        sm.handle_execute_request()
        sm.handle_pause_request()
        assert sm._state == PyTaskState.Pausing

        sm.handle_task_paused()
        assert sm._state == PyTaskState.Paused

        sm.handle_resume_request()
        assert sm._state == PyTaskState.Running

        sm.handle_task_completed()
        assert sm._state == PyTaskState.Completed

        sm.handle_execute_request()
        sm.handle_task_failed()
        assert sm._state == PyTaskState.Failed

        sm.handle_execute_request()
        sm.handle_abort_request()
        assert sm._state == PyTaskState.Aborting

        sm.handle_task_aborted()
        assert sm._state == PyTaskState.Aborted

    def test_incorrect_transitions(self):
        sm = TaskStateMachine()

        with pytest.raises(PyTaskInvalidStateException):
            sm.handle_task_completed()

        with pytest.raises(PyTaskInvalidStateException):
            sm.handle_task_aborted()

        with pytest.raises(PyTaskInvalidStateException):
            sm.handle_task_failed()

        with pytest.raises(PyTaskInvalidStateException):
            sm.handle_task_paused()

        sm.handle_execute_request()

        with pytest.raises(PyTaskInvalidStateException):
            sm.handle_execute_request()

        with pytest.raises(PyTaskInvalidStateException):
            sm.handle_resume_request()

        sm.handle_task_completed()

        with pytest.raises(PyTaskInvalidStateException):
            sm.handle_task_completed()

        with pytest.raises(PyTaskInvalidStateException):
            sm.handle_task_paused()

    def test_wait_has_started(self):
        sm = TaskStateMachine()

        def work():
            sleep(1)
            sm.handle_execute_request()

        t = Thread(target=work)
        t.start()
        sm.wait_has_started()

    def test_wait_inactive(self):
        sm = TaskStateMachine()

        def work():
            sleep(1)
            sm.handle_task_completed()

        sm.handle_execute_request()
        t = Thread(target=work)
        t.start()
        sm.wait_inactive()

    def test_interruptable_delay_complete(self):
        sm = TaskStateMachine()

        def work():
            sm.handle_execute_request()
            sm.interruptable_delay(2000)
            sm.handle_task_completed()

        t = Thread(target=work)
        t.start()
        sm.wait_has_started()
        sm.wait_inactive()
        assert sm._state == PyTaskState.Completed

    def test_interruptable_delay_abort(self):
        sm = TaskStateMachine()

        def work():
            sm.handle_execute_request()
            with pytest.raises(PyTaskAbortedException):
                sm.interruptable_delay(2000)

        t = Thread(target=work)
        t.start()
        sm.wait_has_started()
        sleep(0.5)
        sm.handle_abort_request()
        t.join()
        sm.handle_task_aborted()

        assert sm._state == PyTaskState.Aborted

    def test_interruptable_delay_pause_resume_after(self):
        sm = TaskStateMachine()

        def work():
            sm.handle_execute_request()
            sm.interruptable_delay(1000)
            sm.handle_task_completed()

        t = Thread(target=work)
        t.start()
        sm.wait_has_started()
        sm.handle_pause_request()
        sleep(2)
        sm.handle_resume_request()
        t.join()
        assert sm._state == PyTaskState.Completed
