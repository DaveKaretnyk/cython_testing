# Copyright (c) 2018 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
from abc import ABCMeta, abstractmethod


class IPyTask(metaclass=ABCMeta):
    """ Counterpart to the C++ ITask interface.

    Marking methods with the @abstractmethod decorator means any sub-class
    that does not implement that method will raise a TypeError when the
    class is constructed. I.e. not required to provide a default
    implementation  such as:
        raise NotImplementedError('method not implemented')
    """

    def __init__(self):
        pass

    @abstractmethod
    def get_name(self):
        """ Get the name of the task.

        This is the display name of the task.

        :return: str
        """

    @abstractmethod
    def execute(self):
        """ Execute the task.

        This a (synchronous) blocking call; this method returns only after the
        task has completed, or throws an exception when it has failed or has
        been aborted.

        :raises
        Any exception that occured during the execution of the task.
        PyTaskFailedException, task did not complete due to an error.
        PyTaskAbortedException, task has been aborted.
        PyTaskInvalidStateException, task cannot be started in the current state.
        """

    @abstractmethod
    def pause(self):
        """  Request task to pause.

        The task will pause at the next interruption point (if any). The pause
        request is ignored when the task is in the PyTaskState::Completed or
        PyTaskState::Failed state.

        This is an asynchronous method that returns immediately.

        :raises
        PyTaskInvalidStateException, task cannot be paused in current state.
        """

    @abstractmethod
    def resume(self):
        """ Request task to resume from the paused state.

        The resume request is ignored when the task is in the
        PyTaskState::Completed or PyTaskState::Failed state.

        This is an asynchronous method that returns immediately.

        :raises
        PyTaskInvalidStateException, task cannot be resumed in the current
        state.
        """

    @abstractmethod
    def abort(self):
        """ Request task to abort execution.

        The abort request is ignored when the task is in the
        PyTaskState::Completed or PyTaskState::Failed state.

        This is an asynchronous method that returns immediately.
        """

    @abstractmethod
    def wait_inactive(self):
        """ Wait for the task to become inactive.

        Specifically wait until the task enters the PyTaskState::Completed,
        PyTaskState::Failed, PyTaskState::Aborted or PyTaskState::Paused
        state.
        """

    @abstractmethod
    def wait_has_started(self):
        """ Wait for task to have left the PyTaskState::Idle state.

        Since the execute() method is typically called from a different thread
        than the pause() and abort() methods, this method can be used to make
        sure that these methods are not called before the task has left the
        PyTaskState::Idle state.
        """

    @abstractmethod
    def can_pause(self):
        """ Returns true if task can be paused, else return false.
            Specific tasks should override this method to change value.

        :return: boolean
        """

    @abstractmethod
    def can_abort(self):
        """ Returns true if task can be aborted, else return false.
            Specific tasks should override this method to change value.

        :return: boolean
        """

    @abstractmethod
    def get_state(self):
        """ Retrieve the current task state.

        :return: PyTaskState
        """

    @abstractmethod
    def subscribe_progress(self, progress_callback):
        """ Setup a task progress callback.

        The callback will be called on the same thread as the execute method.
        It is the client's responsibility to de-couple if appropriate.

        * Signature of callback defined by method IPyTaskCallback
          'progress_callback'.
        * Unsubscribe by calling the unsubscribe() method of the returned object. The returned
          Subscription object can be used as a context manager to unsubscribe.

        :param progress_callback IPyTaskCallback.progress_callback
        :return: Subscription object used to unsubscribe the current callback handler
        """

    @abstractmethod
    def subscribe_message(self, message_callback):
        """ Setup a task message callback.

        The callback will be called on the same thread as the execute method.
        It is the client's responsibility to de-couple if appropriate.

        * Signature of callback defined by method IPyTaskCallback
          'message_callback'.
        * Unsubscribe by calling the unsubscribe() method of the returned object. The returned
          Subscription object can be used as a context manager to unsubscribe.

        :param message_callback IPyTaskCallback.message_callback
        :return: Subscription object used to unsubscribe the current callback handler
        """

    @abstractmethod
    def subscribe_state_change(self, state_change_callback):
        """ Setup a task state change callback.

        The callback will be called on the same thread as the execute method.
        It is the client's responsibility to de-couple if appropriate.

        * Signature of callback defined by method IPyTaskCallback
          'state_change_callback'.
        * Unsubscribe by calling the unsubscribe() method of the returned object. The returned
          Subscription object can be used as a context manager to unsubscribe.

        :param state_change_callback IPyTaskCallback.state_change_callback
        :return: Subscription object used to unsubscribe the current callback handler
        """
