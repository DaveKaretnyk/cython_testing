# Copyright (c) 2012-2019 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.

import time
from threading import Condition, Lock

from .pytask_event import EventBroadcaster
from .pytask_exceptions import PyTaskAbortedException, PyTaskInvalidStateException
from .pytask_state import PyTaskState


class TaskStateMachine(object):
    """ This class implements the state machine for PyTask derived classes.

    This class handles the state transitions and verifies preconditions.
    Precondition violations result in a TaskInvalidStateException.

    This class is thread safe.
    """

    def __init__(self):
        self._lock = Lock()
        self._status_changed = Condition(self._lock)

        self._internal_state = PyTaskState.Idle
        self.state_broadcaster = EventBroadcaster()

    @property
    def _state(self):
        return self._internal_state

    @_state.setter
    def _state(self, new_state):
        """ If the task state changes, save the new state, notify all subscribers and
            notify all threads waiting on the _status_changed condition.
            Must be called with lock held.
        """
        if new_state != self._internal_state:
            self._internal_state = new_state
            self.state_broadcaster.emit(self._internal_state)
            self._status_changed.notify_all()

    def handle_execute_request(self):
        with self._lock:
            if self._state in [PyTaskState.Idle, PyTaskState.Completed,
                               PyTaskState.Failed, PyTaskState.Aborted]:
                self._state = PyTaskState.Running
            else:
                raise PyTaskInvalidStateException('Cannot transition from {0} to {1}'.format(
                    str(self._state), str(PyTaskState.Running)))

    def handle_pause_request(self):
        with self._lock:
            if self._state == PyTaskState.Running:
                self._state = PyTaskState.Pausing
            elif self._state in [PyTaskState.Pausing, PyTaskState.Paused,
                                 PyTaskState.Completed, PyTaskState.Failed]:
                return
            else:
                raise PyTaskInvalidStateException('Cannot transition from {0} to {1}'.format(
                    str(self._state), str(PyTaskState.Pausing)))

    def handle_resume_request(self):
        with self._lock:
            if self._state in [PyTaskState.Paused, PyTaskState.Pausing]:
                self._state = PyTaskState.Running
            elif self._state in [PyTaskState.Completed, PyTaskState.Failed]:
                return
            else:
                raise PyTaskInvalidStateException('Cannot transition from {0} to {1}'.format(
                    str(self._state), str(PyTaskState.Running)))

    def handle_abort_request(self):
        with self._lock:
            if self._state in [PyTaskState.Running, PyTaskState.Pausing, PyTaskState.Paused]:
                self._state = PyTaskState.Aborting
            elif self._state in [PyTaskState.Aborting, PyTaskState.Aborted,
                                 PyTaskState.Completed, PyTaskState.Failed]:
                return
            else:
                raise PyTaskInvalidStateException('Cannot transition from {0} to {1}'.format(
                    str(self._state), str(PyTaskState.Aborting)))

    def handle_task_completed(self):
        with self._lock:
            if self._state in [PyTaskState.Running, PyTaskState.Pausing, PyTaskState.Aborting]:
                self._state = PyTaskState.Completed
            else:
                raise PyTaskInvalidStateException('Cannot transition from {0} to {1}'.format(
                    str(self._state), str(PyTaskState.Completed)))

    def handle_task_failed(self):
        with self._lock:
            if self._state in [PyTaskState.Running, PyTaskState.Pausing, PyTaskState.Aborting]:
                self._state = PyTaskState.Failed
            else:
                raise PyTaskInvalidStateException('Cannot transition from {0} to {1}'.format(
                    str(self._state), str(PyTaskState.Failed)))

    def handle_task_aborted(self):
        with self._lock:
            if self._state == PyTaskState.Aborting:
                self._state = PyTaskState.Aborted
            else:
                raise PyTaskInvalidStateException('Cannot transition from {0} to {1}'.format(
                    str(self._state), str(PyTaskState.Aborted)))

    def handle_task_paused(self):
        with self._lock:
            if self._state == PyTaskState.Pausing:
                self._state = PyTaskState.Paused
            else:
                raise PyTaskInvalidStateException('Cannot transition from {0} to {1}'.format(
                    str(self._state), str(PyTaskState.Paused)))

    def handle_interruption_request(self):
        """ Handle pause and abort requests from the client:

            Blocks the current thread when pause has been requested until the
            task is requested to resume.
            Throws a PyTaskAbortedException when abort has been requested.
            If no pause or abort has been requested this method returns immediately.
        """
        with self._lock:
            if self._state == PyTaskState.Pausing:
                self._state = PyTaskState.Paused

            while self._state == PyTaskState.Paused:
                self._status_changed.wait()

            if self._state == PyTaskState.Aborting:
                raise PyTaskAbortedException('Task has been aborted')

    def interruptable_delay(self, delay_ms):
        """ Wait for the specified amount of time to pass.

            If a pause request is received this method will block until a resume request is
            received. If the resume request is received before the delay period has passed this
            method will wait for the remaining amount of time to pass. If the delay period has
            passed while paused, a resume request will cause this method to return immediately.

            If an abort request is received this method will throw a TaskAbortedException
        """
        if self._state not in [PyTaskState.Running, PyTaskState.Pausing, PyTaskState.Aborting]:
            raise RuntimeError("This function may only be called while in the 'Running', "
                               "'Aborting' or 'Pausing' state.")

        deadline = time.monotonic() + delay_ms / 1000

        while time.monotonic() < deadline:
            with self._lock:
                time_left = deadline - time.monotonic()
                self._status_changed.wait(time_left / 1000)

            self.handle_interruption_request()

    def subscribe_state_change(self, handler):
        with self._lock:
            return self.state_broadcaster.add_handler(handler)

    def wait_inactive(self):
        """ Block until an inactive state has been reached.
        """
        with self._lock:
            while self._state in [PyTaskState.Running, PyTaskState.Pausing, PyTaskState.Aborting]:
                self._status_changed.wait()

        return self._state

    def wait_has_started(self):
        """ Block until the task has left the PyTaskState::Idle state.
        """
        with self._lock:
            while self._state == PyTaskState.Idle:
                self._status_changed.wait()
