# Copyright (c) 2022 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.

import pytest
import threading

from unittest.mock import Mock

from ..pytask_state import PyTaskState
from ..pytask_exceptions import PyTaskAbortedException, PyTaskFailedException
from .interactive_task import InteractiveTask
from .simple_task_with_callback import SimpleTaskWithCallbacksSink
from .exception_raising_thread import ExceptionRaisingThread


@pytest.fixture
def event():
    """
    Provides a threading event
    :return: Instance of a threading event
    """
    event = threading.Event()
    event.clear()
    return event


@pytest.fixture
def interactive_task(event):
    """
    Provides an interactive task
    :return: Instance of an interactive task
    """
    task = InteractiveTask()

    def handle_user_response_requested(_):
        event.set()

    task.subscribe_user_response_requested(handle_user_response_requested)
    return task


def test_interactive_task_name():
    task_name = 'Sample interactive task'
    task = InteractiveTask(task_name)
    name = task.get_name()
    assert name == task_name
    assert isinstance(name, str)


def test_pause_with_interactive_task(interactive_task, event):
    thread = ExceptionRaisingThread(target=interactive_task.execute)

    thread.start()
    interactive_task.wait_has_started()

    state = interactive_task.get_state()
    assert state == PyTaskState.Running

    assert event.wait(timeout=5)

    interactive_task.pause()  # Call has no effect when the task is waiting for user response
    assert interactive_task.get_state() == PyTaskState.Running

    interactive_task.provide_user_response(user_response='Repeat')
    interactive_task.pause()  # Pause has the desired effect of pausing the task
    assert interactive_task.get_state() == PyTaskState.Pausing

    interactive_task.resume()
    assert interactive_task.get_state() == PyTaskState.Running

    interactive_task.wait_inactive()
    assert interactive_task.get_state() == PyTaskState.Completed

    thread.join()


def test_abort_while_waiting_for_user_response(interactive_task, event):
    error_message = 'Task has been aborted'

    def task_execute():
        with pytest.raises(PyTaskAbortedException) as e:
            interactive_task.execute()
        assert error_message in str(e)

    thread = ExceptionRaisingThread(target=task_execute)

    thread.start()
    interactive_task.wait_has_started()

    assert event.wait(timeout=5)
    interactive_task.abort()  # Task should abort while waiting for user response
    interactive_task.wait_inactive()
    assert interactive_task.get_state() == PyTaskState.Aborted

    thread.join()


def test_interactive_task_throws_exception(interactive_task, event, monkeypatch):
    error_message = 'Interactive task threw an exception'

    def task_execute():
        with pytest.raises(RuntimeError) as e:
            interactive_task.execute()
        assert error_message in str(e)

    monkeypatch.setattr(InteractiveTask, 'on_execute',
                        Mock(side_effect=RuntimeError(error_message)))

    thread = ExceptionRaisingThread(target=task_execute)
    thread.start()
    interactive_task.wait_has_started()
    interactive_task.wait_inactive()
    assert interactive_task.get_state() == PyTaskState.Failed

    thread.join()


def test_user_response_requested_subscription(interactive_task, event):
    user_response_requested_callbacks = []
    expected_user_instruction = ['Instruction for the user']

    def handle_user_response_requested(actual_instruction):
        user_response_requested_callbacks.append(actual_instruction)
        event.set()

    interactive_task.subscribe_user_response_requested(handle_user_response_requested)
    thread = ExceptionRaisingThread(target=interactive_task.execute)

    thread.start()
    interactive_task.wait_has_started()

    assert event.wait(timeout=5)
    interactive_task.provide_user_response(user_response='Skip')
    interactive_task.wait_inactive()
    assert interactive_task.get_state() == PyTaskState.Completed

    assert len(user_response_requested_callbacks) == 1
    assert user_response_requested_callbacks == expected_user_instruction

    thread.join()


def test_with_user_response_requested_callback_unsubscribe(event):
    interactive_task = InteractiveTask()
    error_message = 'Client not subscribed to "user response requested callback"'
    user_response_requested_callbacks = []

    def task_execute():
        with pytest.raises(PyTaskFailedException) as e:
            interactive_task.execute()
        assert error_message in str(e)

    def handle_user_response_requested(actual_instruction):
        user_response_requested_callbacks.append(actual_instruction)
        event.set()

    user_response_sub = interactive_task.subscribe_user_response_requested(
        handle_user_response_requested)
    thread = ExceptionRaisingThread(target=task_execute)
    user_response_sub.unsubscribe()
    thread.start()
    interactive_task.wait_has_started()
    interactive_task.wait_inactive()
    assert interactive_task.get_state() == PyTaskState.Failed
    assert not user_response_requested_callbacks

    thread.join()


@pytest.mark.parametrize('user_response', ['Accept', 'Repeat'])
def test_user_response_received(interactive_task, event, user_response):
    thread = ExceptionRaisingThread(target=interactive_task.execute)

    thread.start()
    interactive_task.wait_has_started()

    state = interactive_task.get_state()
    assert state == PyTaskState.Running

    assert event.wait(timeout=5)

    interactive_task.provide_user_response(user_response=user_response)
    interactive_task.wait_inactive()
    assert interactive_task.get_user_response_received() == user_response

    thread.join()


def test_no_user_response_received(interactive_task, event):
    error_message = 'No user response received by the interactive task'

    def task_execute():
        with pytest.raises(PyTaskFailedException) as e:
            interactive_task.execute()
        assert error_message in str(e)

    thread = ExceptionRaisingThread(target=task_execute)

    thread.start()
    interactive_task.wait_has_started()

    state = interactive_task.get_state()
    assert state == PyTaskState.Running

    assert event.wait(timeout=5)

    interactive_task.provide_user_response(user_response=None)
    interactive_task.wait_inactive()
    assert interactive_task.get_state() == PyTaskState.Failed

    thread.join()


def test_task_subscriptions_with_interactive_task(interactive_task, event):
    task_sink = SimpleTaskWithCallbacksSink()

    interactive_task.subscribe_progress(task_sink.progress_callback)
    interactive_task.subscribe_state_change(task_sink.state_change_callback)
    interactive_task.subscribe_message(task_sink.message_callback)

    state = interactive_task.get_state()
    assert state == PyTaskState.Idle

    thread = ExceptionRaisingThread(target=interactive_task.execute)

    thread.start()
    interactive_task.wait_has_started()

    state = interactive_task.get_state()
    assert state == PyTaskState.Running

    assert event.wait(timeout=5)

    interactive_task.provide_user_response('Accept')
    interactive_task.wait_inactive()

    assert interactive_task.get_state() == PyTaskState.Completed

    assert task_sink.progress_callbacks == [0.0, 10.0, 33.0, 66.0, 100.0]
    assert task_sink.state_change_callbacks == [PyTaskState.Running, PyTaskState.Completed]
    assert len(task_sink.message_callbacks) == 4

    thread.join()


@pytest.mark.parametrize('user_response', ['Accept', 'Repeat'])
def test_valid_users_responses(interactive_task, event, user_response):
    valid_users_actions = ['Accept', 'Repeat']

    thread = ExceptionRaisingThread(target=interactive_task.execute)

    thread.start()
    interactive_task.wait_has_started()

    state = interactive_task.get_state()
    assert state == PyTaskState.Running

    assert event.wait(timeout=5)

    interactive_task.set_valid_user_actions(valid_users_actions)
    assert valid_users_actions == interactive_task.get_valid_user_actions()

    interactive_task.provide_user_response(user_response=user_response)
    interactive_task.wait_inactive()

    assert [] == interactive_task.get_valid_user_actions()

    thread.join()
