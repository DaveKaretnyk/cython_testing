# Copyright (c) 2012-2019 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.

from abc import abstractmethod
import logging
from typing import Callable

from .i_pytask import IPyTask
from .pytask_event import EventBroadcaster, Subscription
from .pytask_exceptions import PyTaskAbortedException
from .pytask_state import PyTaskState
from .pytask_state_machine import TaskStateMachine


class PyTaskBase(IPyTask):
    """ Implements common base behavior of the IPyTask interface.
    """

    def __init__(self, task_name: str):
        """ Initializer.

        :param task_name: Name of the task (e.g. for display purposes).
        """
        super().__init__()
        self._logger = logging.getLogger(self.__class__.__name__)

        self._task_state_machine = TaskStateMachine()
        self._last_reported_progress = -1.0
        self._progress_broadcaster = EventBroadcaster()
        self._message_broadcaster = EventBroadcaster()
        self.task_name = task_name

    @abstractmethod
    def on_execute(self) -> None:
        """ This MUST be overridden in the specialization that implements the
        actual functionality.
        """

    def can_pause(self) -> bool:
        """ Task will only attempt a pause request if this value is True. Default is True.

        The specialization of PyTaskBase can override this method to change the value
        """
        return True

    def can_abort(self) -> bool:
        """ Task will only attempt an abort request if this value is True. Default is True.

        The specialization of PyTaskBase can override this method to change the value
        """
        return True

    def report_message(self, message: str) -> None:
        """ Provide an arbitrary message update to the client regarding the
        execution of the task.

        The specialization of PyTaskBase calls this method to update clients
        (assuming they have subscribed).

        :param message: message to broadcast
        """
        self._message_broadcaster.emit(message)

    def report_progress(self, percentage: float) -> None:
        """ Provide progress update to the client regarding the execution of
        the task.

        The specialization of PyTaskBase calls this method to update clients
        (assuming they have subscribed).

        The parameter can be any float value, though it is expected to be a
        percentage value indicating the current progress.

        :param percentage: New progress, expected to be between 0. and 100.
        """
        if self._last_reported_progress != percentage:
            self._last_reported_progress = percentage
            self._progress_broadcaster.emit(percentage)

    def handle_interruption_request(self) -> None:
        """ Handle a request to interrupt the task.

        The specialization of PyTaskBase calls this method at a appropriate
        time when the interrupt can be handled.
        """
        self._task_state_machine.handle_interruption_request()

    def interruptable_delay(self, delay_ms: float) -> None:
        """ Wait for the specified amount of time to pass. Interruptible
        """
        self._task_state_machine.interruptable_delay(delay_ms)

    def get_name(self) -> str:
        """ Returned the name of the task

        :return: str, Name of the task
        """
        return self.task_name

    def execute(self) -> None:
        """ Start the execution of the task
        """
        self._task_state_machine.handle_execute_request()

        try:
            self.report_progress(0.0)
            self.on_execute()
            self.report_progress(100.0)

            self._task_state_machine.handle_task_completed()

        except PyTaskAbortedException:
            self._task_state_machine.handle_task_aborted()
            raise

        except Exception:
            self._task_state_machine.handle_task_failed()
            raise

    def pause(self) -> None:
        if self.can_pause:
            self._task_state_machine.handle_pause_request()

    def resume(self) -> None:
        self._task_state_machine.handle_resume_request()

    def abort(self) -> None:
        if self.can_abort:
            self._task_state_machine.handle_abort_request()

    def wait_inactive(self) -> PyTaskState:
        return self._task_state_machine.wait_inactive()

    def wait_has_started(self) -> None:
        return self._task_state_machine.wait_has_started()

    def get_state(self) -> PyTaskState:
        return self._task_state_machine._state

    def subscribe_progress(self, progress_callback: Callable[[float], None]) -> Subscription:
        self._logger.info('client subscribed to "progress callbacks"')
        return self._progress_broadcaster.add_handler(progress_callback)

    def subscribe_message(self, message_callback: Callable[[str], None]) -> Subscription:
        self._logger.info('client subscribed to "message callbacks"')
        return self._message_broadcaster.add_handler(message_callback)

    def subscribe_state_change(self,
                               state_change_callback: Callable[[PyTaskState], None],
                               ) -> Subscription:
        self._logger.info('client subscribed to "state change callbacks"')
        return self._task_state_machine.subscribe_state_change(state_change_callback)
