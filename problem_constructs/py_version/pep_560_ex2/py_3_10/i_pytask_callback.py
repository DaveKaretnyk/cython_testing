# Copyright (c) 2018 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
from abc import ABC, abstractmethod


class IPyTaskCallback(ABC):
    """ The optional callback methods making up the IPyTask interface.

    Marking methods with the @abstractmethod decorator means any sub-class
    that does not implement that method will raise a TypeError when the
    class is constructed. I.e. not required to provide a default
    implementation such as:
        raise NotImplementedError('method not implemented')
    """

    @abstractmethod
    def progress_callback(self, percentage):
        """ Provide a float value indicating the overall progress of the task
        during execution.

        The callback will be called on the same thread as the execute method.
        It is the client's responsibility to de-couple if appropriate.

        * The value is a percentage, i.e. a float value between 0.0 and 100.0.
        * Clients subscribe to these progress updates via the IPyTask method
          'subscribe_progress'.
        * The frequency with which this method is called is entirely dependent
          on the implementation of the specific task.

        :param percentage float
        """

    @abstractmethod
    def message_callback(self, message):
        """ Provide progress message during task execution.

        The callback will be called on the same thread as the execute method.
        It is the client's responsibility to de-couple if appropriate.

        * The value is a string.
        * Clients subscribe to these messages via the IPyTask method
          'subscribe_message'.
        * The frequency with which this method is called is entirely dependent
          on the implementation of the specific task.

        :param message basestring
        """

    @abstractmethod
    def state_change_callback(self, task_state):
        """ Provide task state change information during task execution.

        The callback will be called on the same thread as the execute method.
        It is the client's responsibility to de-couple if appropriate.

        * The value is a PyTaskState.
        * Clients subscribe to these state changes via the IPyTask method
          'subscribe_message'.
        * The frequency with which this method is called is entirely dependent
          on the implementation of the specific task.

        :param task_state PyTaskState enum
        """
