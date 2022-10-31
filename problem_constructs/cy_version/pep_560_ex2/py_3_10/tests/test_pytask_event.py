# Copyright (c) 2012-2019 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
from ..pytask_event import EventBroadcaster, Subscription


class EventTester(object):
    def __init__(self):
        self.call_count = 0
        self.radio = EventBroadcaster()

    def method_1(self, param):
        if param == 3:
            self.call_count += 1

    def method_2(self, param):
        if param == 3:
            self.call_count += 2

    def method_3(self, param):
        if param == 3:
            self.call_count += 3


def test_add_subscription():
    tester = EventTester()
    tester.radio.add_handler(tester.method_1)
    tester.radio.add_handler(tester.method_2)
    tester.radio.emit(3)
    assert tester.call_count == 3


def test_remove_subscription():
    tester = EventTester()
    s1 = tester.radio.add_handler(tester.method_1)
    assert isinstance(s1, Subscription)

    s2 = tester.radio.add_handler(tester.method_2)
    tester.radio.emit(3)
    assert tester.call_count == 3
    tester.call_count = 0

    s3 = tester.radio.add_handler(tester.method_3)
    assert len(tester.radio._subscriptions) == 3

    s2.unsubscribe()
    tester.radio.emit(3)
    assert tester.call_count == 4
    tester.call_count = 0

    s2 = tester.radio.add_handler(tester.method_2)
    s1.unsubscribe()
    s3.unsubscribe()
    tester.radio.emit(3)
    assert tester.call_count == 2

    del tester.radio
    s2.unsubscribe()


def test_subscription_context_manager():
    radio = EventBroadcaster()

    with radio.add_handler(test_subscription_context_manager) as sub:
        assert isinstance(sub, Subscription)
        assert len(radio._subscriptions) == 1
        assert radio.is_subscribed()

    assert len(radio._subscriptions) == 0
    assert not radio.is_subscribed()
