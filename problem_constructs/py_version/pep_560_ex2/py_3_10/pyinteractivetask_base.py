# Copyright (c) 2022 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.

import logging
from abc import ABC
from threading import Condition, Lock
from typing import Callable, List, Optional, TypeVar

from .i_pyinteractivetask import IPyInteractiveTask
from .pytask_base import PyTaskBase
from .pytask_event import EventBroadcaster, Subscription
from .pytask_exceptions import PyTaskFailedException

logger = logging.getLogger(__name__)

Request_type = TypeVar("Request_type")
Response_type = TypeVar("Response_type")


class PyInteractiveTaskBase(PyTaskBase,
                            IPyInteractiveTask[Request_type, Response_type], ABC):
    """ Implements common base behavior of the IPyInteractiveTask interface.
        Supplements automated task functionality provided by PyTaskBase with interactive behaviour
        A task that needs interactive behaviour should derive from PyInteractiveTaskBase
    """
    def __init__(self, task_name: str):
        """ Initializer.

        :param task_name: Name of the task (e.g. for display purposes).
        """
        super().__init__(task_name)
        self.__user_response_requested_broadcaster = EventBroadcaster()
        self.__lock = Lock()
        self.__condition_variable = Condition(self.__lock)
        self.__waiting_for_user_response = False
        self.__user_response_received: Optional[Response_type] = None
        self.__valid_user_actions: List[Response_type] = []

    def subscribe_user_response_requested(self, user_response_requested_handler:
                                          Callable[[Request_type], None]) -> Subscription:
        logger.info('Client subscribed to "user response requested callback"')
        return self.__user_response_requested_broadcaster.add_handler(
            user_response_requested_handler)

    def provide_user_response(self, user_response: Response_type) -> None:
        self.__user_response_received = user_response
        self.__reset_valid_user_actions()
        self.__end_wait_for_user_response()

    def request_user_response(self, user_instruction: Request_type) -> Response_type:
        if not self.__user_response_requested_broadcaster.is_subscribed():
            raise PyTaskFailedException('Client not subscribed to "user response '
                                        'requested callback". Potential task hangup possible')
        self.__report_user_instruction(user_instruction)
        self.__wait_for_user_response()
        super().handle_interruption_request()
        if self.__user_response_received is None:
            raise PyTaskFailedException('No user response received by the interactive task')
        return self.__user_response_received

    def get_valid_user_actions(self) -> List[Response_type]:
        return self.__valid_user_actions

    def set_valid_user_actions(self, actions: List[Response_type]) -> None:
        self.__valid_user_actions = actions[:]

    def pause(self) -> None:
        if not self.__is_waiting_for_user_response():
            super().pause()

    def abort(self) -> None:
        super().abort()
        if self.__is_waiting_for_user_response():
            self.__end_wait_for_user_response()

    def __is_waiting_for_user_response(self) -> bool:
        with self.__condition_variable:
            return self.__waiting_for_user_response

    def __report_user_instruction(self, message: Request_type) -> None:
        self.__user_response_requested_broadcaster.emit(message)

    def __reset_valid_user_actions(self) -> None:
        self.__valid_user_actions.clear()

    def __wait_for_user_response(self):
        with self.__condition_variable:
            self.__waiting_for_user_response = True
            self.__condition_variable.wait()

    def __end_wait_for_user_response(self):
        with self.__condition_variable:
            self.__condition_variable.notify_all()
            self.__waiting_for_user_response = False
