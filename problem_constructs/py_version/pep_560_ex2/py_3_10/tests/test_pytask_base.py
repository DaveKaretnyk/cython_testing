# Copyright (c) 2018 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
import threading
import time
from pprint import pprint

import pytest

from ..pytask_exceptions import PyTaskException, PyTaskFailedException
from ..pytask_state import PyTaskState
from .failing_task import TaskFailsWithPyTaskFailedException
from .interruptable_task import (
            InterruptableTask,
            InterruptableTaskWithCallbacksSink,
            TaskWithInterruptableDelay)
from .simple_task import SimpleTask
from .simple_task_with_callback import SimpleTaskWithCallbacks, SimpleTaskWithCallbacksSink
from .task_with_cleanup import TaskWithCleanup

diagnostics_print = True


# Simplest possible task.
def test_simple_task():
    task = SimpleTask()

    name = task.get_name()
    if diagnostics_print:
        print('in test code, task name: {0}; type: {1}'.format(name, type(name)))
    assert name == u'Simple Task'
    assert isinstance(name, str)

    state = task.get_state()
    if diagnostics_print:
        print('\nstate before execution: {0}, type: {1}'.format(state.name, type(state)))
    assert state == PyTaskState.Idle

    task.execute()
    state = task.get_state()
    if diagnostics_print:
        print('state after execution: {0}, type: {1}'.format(state.name, type(state)))
    assert state == PyTaskState.Completed


# Simple task with subscription to callbacks
def test_simple_task_with_callbacks():
    task = SimpleTaskWithCallbacks()

    task_sink = SimpleTaskWithCallbacksSink()
    task.subscribe_state_change(task_sink.state_change_callback)
    task.subscribe_progress(task_sink.progress_callback)
    task.subscribe_message(task_sink.message_callback)

    task.execute()

    if diagnostics_print:
        print('\nstate change callbacks:')
        pprint(task_sink.state_change_callbacks)
        print('\nprogress callbacks:')
        pprint(task_sink.progress_callbacks)
        print('\nmessage callbacks:')
        pprint(task_sink.message_callbacks)
    assert task_sink.progress_callbacks == [0.0, 23.0, 52.0, 69.0, 87.0, 100.0]
    assert PyTaskState.Running in task_sink.state_change_callbacks
    assert PyTaskState.Completed in task_sink.state_change_callbacks
    assert len(task_sink.message_callbacks) == 6


def test_simple_task_with_callbacks_unsubscribe():
    task = SimpleTaskWithCallbacks()

    task_sink = SimpleTaskWithCallbacksSink()
    sub1 = task.subscribe_state_change(task_sink.state_change_callback)
    sub2 = task.subscribe_progress(task_sink.progress_callback)
    sub3 = task.subscribe_message(task_sink.message_callback)

    sub1.unsubscribe()
    sub2.unsubscribe()
    sub3.unsubscribe()

    task.execute()

    if diagnostics_print:
        print('\nstate change callbacks:')
        pprint(task_sink.state_change_callbacks)
        print('\nprogress callbacks:')
        pprint(task_sink.progress_callbacks)
        print('\nmessage callbacks:')
        pprint(task_sink.message_callbacks)
    assert not task_sink.progress_callbacks
    assert not task_sink.state_change_callbacks
    assert not task_sink.message_callbacks


def test_simple_task_with_callbacks_context_manager():
    task = SimpleTaskWithCallbacks()
    task_sink = SimpleTaskWithCallbacksSink()

    with task.subscribe_message(task_sink.message_callback), \
            task.subscribe_progress(task_sink.progress_callback), \
            task.subscribe_state_change(task_sink.state_change_callback):
        task.execute()

    assert task_sink.progress_callbacks == [0.0, 23.0, 52.0, 69.0, 87.0, 100.0]
    assert PyTaskState.Running in task_sink.state_change_callbacks
    assert PyTaskState.Completed in task_sink.state_change_callbacks
    assert len(task_sink.message_callbacks) == 6
    assert not task._message_broadcaster._subscriptions
    assert not task._progress_broadcaster._subscriptions
    assert not task._task_state_machine.state_broadcaster._subscriptions


def test_multiple_subscribe():
    task = SimpleTaskWithCallbacks()

    task_sink = SimpleTaskWithCallbacksSink()
    sub1 = task.subscribe_message(task_sink.message_callback)
    sub2 = task.subscribe_message(task_sink.message_callback2)
    sub3 = task.subscribe_message(task_sink.message_callback3)

    task.execute()
    assert len(task_sink.message_callbacks) == 18

    sub1.unsubscribe()
    sub2.unsubscribe()
    sub3.unsubscribe()

    task.execute()
    assert len(task_sink.message_callbacks) == 18


def test_interruptable_task_completed():
    task = InterruptableTask()

    thread = threading.Thread(target=task.execute)
    thread.start()
    time.sleep(1)

    print('Tell task to pause...')
    task.pause()
    task.wait_inactive()
    assert task.get_state() == PyTaskState.Paused

    time.sleep(2)

    print('Tell task to resume...')
    task.resume()

    task.wait_has_started()
    assert task.get_state() == PyTaskState.Running

    task.wait_inactive()
    assert task.get_state() == PyTaskState.Completed


def test_resume_from_pausing_state_completed():
    task = SimpleTask()

    thread = threading.Thread(target=task.execute)
    thread.start()
    task.wait_has_started()
    task.pause()
    assert task.get_state() == PyTaskState.Pausing

    task.resume()
    assert task.get_state() == PyTaskState.Running

    task.wait_inactive()
    assert task.get_state() == PyTaskState.Completed


def test_interruptable_task_aborted():
    task = InterruptableTask()

    task_sink = InterruptableTaskWithCallbacksSink()
    task.subscribe_state_change(task_sink.state_change_callback)
    task.subscribe_progress(task_sink.progress_callback)
    task.subscribe_message(task_sink.message_callback)

    def task_execute():
        print('\nExecute thread of task started...')

        try:
            task.execute()
        except PyTaskException as e:
            print('exception raised: {0}'.format(e))

    thread = threading.Thread(target=task_execute)
    thread.start()

    time.sleep(1)

    print('Tell task to pause...')
    task.pause()
    task.wait_inactive()
    assert task.get_state() == PyTaskState.Paused

    time.sleep(2)

    print('Tell task to resume...')
    task.resume()

    time.sleep(1)

    print('Tell task to abort...')
    task.abort()
    task.wait_inactive()
    assert task.get_state() == PyTaskState.Aborted

    thread.join()

    if diagnostics_print:
        print('\nstate change callbacks:')
        pprint(task_sink.state_change_callbacks)
        print('\nprogress callbacks:')
        pprint(task_sink.progress_callbacks)
        print('\nmessage callbacks:')
        pprint(task_sink.message_callbacks)
    expected_state_changes = [
        PyTaskState.Running,
        PyTaskState.Pausing,
        PyTaskState.Paused,
        PyTaskState.Running,
        PyTaskState.Aborting,
        PyTaskState.Aborted,
    ]
    assert task_sink.state_change_callbacks == expected_state_changes
    assert task_sink.progress_callbacks == [0.0, 30.0, 60.0]
    assert len(task_sink.message_callbacks) == 4


def test_aborted_from_completed_state():
    task = SimpleTask()
    task.execute()
    assert task.get_state() == PyTaskState.Completed
    task.abort()
    task.pause()
    assert task.get_state() == PyTaskState.Completed


def test_aborted_from_failed_state():
    task = TaskFailsWithPyTaskFailedException("Failing Task")

    with pytest.raises(PyTaskFailedException):
        task.execute()

    assert task.get_state() == PyTaskState.Failed
    task.abort()
    task.pause()
    assert task.get_state() == PyTaskState.Failed


def test_task_with_cleanup():
    task = TaskWithCleanup()
    task.execute()


def test_interruptable_delay_aborted():
    task = TaskWithInterruptableDelay(10000)  # 10 seconds delay, doesn't affect test duration
    thread = threading.Thread(target=task.execute)
    thread.start()

    task.wait_has_started()
    task.abort()
    task.wait_inactive()

    assert task.get_state() == PyTaskState.Aborted


def test_interruptable_delay_paused():
    task = TaskWithInterruptableDelay(2000)
    thread = threading.Thread(target=task.execute)
    thread.start()

    task.wait_has_started()
    task.pause()
    task.wait_inactive()
    assert task.get_state() == PyTaskState.Paused

    time.sleep(0.5)
    task.resume()
    task.wait_inactive()

    assert task.get_state() == PyTaskState.Completed


def test_parallel_run():
    def show_progress(percentage):
        thread_name = threading.current_thread().name
        if diagnostics_print:
            print("{0} progress: {1}%".format(str(thread_name), percentage))

    task1 = SimpleTask()
    task2 = SimpleTask()
    task3 = SimpleTask()

    task1.subscribe_progress(show_progress)
    task2.subscribe_progress(show_progress)
    task3.subscribe_progress(show_progress)

    t1 = threading.Thread(target=task1.execute)
    t2 = threading.Thread(target=task2.execute)
    t3 = threading.Thread(target=task3.execute)

    t1.start()
    time.sleep(0.2)
    t2.start()
    time.sleep(0.2)
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    assert task1.get_state() == PyTaskState.Completed
    assert task2.get_state() == PyTaskState.Completed
    assert task3.get_state() == PyTaskState.Completed
