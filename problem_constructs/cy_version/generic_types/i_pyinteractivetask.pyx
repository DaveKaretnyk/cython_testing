# Copyright (c) 2022 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.

from abc import ABC, abstractmethod
from typing import Callable, Generic, TypeVar
from .pytask_event import Subscription

Request_type = TypeVar("Request_type")
Response_type = TypeVar("Response_type")


class IPyInteractiveTask(ABC, Generic[Request_type, Response_type]):
    """ Python interactive task interface to develop semi-automated tasks

    Marking methods with the @abstractmethod decorator means any sub-class
    that does not implement that method will raise a TypeError when the
    class is constructed. I.e. not required to provide a default
    implementation such as:
        raise NotImplementedError('method not implemented')
    """
    def __init__(self):
        pass

    @abstractmethod
    def subscribe_user_response_requested(
            self,
            user_response_requested_callback: Callable[[Request_type], None]) -> Subscription:
        """ Setup an interactive task user input requested callback.

        The callback will be called on the same thread as the execute method.
        It is the client's responsibility to de-couple if appropriate.

        * Unsubscribe by calling the unsubscribe() method of the returned object. The returned
          Subscription object can be used as a context manager to unsubscribe.

        :param user_response_requested_callback
        :return: Subscription object used to unsubscribe the current callback handler
        """

    @abstractmethod
    def request_user_response(self, user_instruction: Request_type) -> Response_type:
        """
        Method to request user response based on the instruction provided. This is a blocking
        call until the user response is provided via 'provide_user_response' method. This method
        is to be used from within a task and not to be called by users of the task.

        :param: user_instruction: Instruction for the user to perform an action. e.g.
        change some optical settings, review an image
        :return: User response to the provided instruction
        """

    @abstractmethod
    def provide_user_response(self, user_response: Response_type) -> None:
        """
        Method to provide user response.

        It is the client's responsibility to call this method on a separate thread from the one used
        to execute a task. This method should be called AFTER a request for user response has been
        received via user_response_requested_callback. This call will unblock the
        'request_user_response' method. Method has no effect if called before calling
        'request_user_response' method.

        :param: user_response: Response that the user provided
        """
