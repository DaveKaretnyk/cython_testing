# Copyright (c) 2012-2019 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.
from typing import Callable, Generic, Set, TypeVar, cast

H = TypeVar('H', bound=Callable)


class Subscription:
    """ Represents a subscription to the event. Its only purpose is to provide
        an unsubscribe mechanism for the EventBroadcaster.

        An instance of this class is returned when adding a new handler.
    """

    def __init__(self, handler: Callable, container: Set['Subscription']):
        self.handler = handler
        self._container = container

    def unsubscribe(self) -> None:
        """ Removes the associated handler from the event distribution list.
        """
        self._container.discard(self)

    def __enter__(self) -> 'Subscription':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unsubscribe()


# Do not inherit from parameterized Generic -> Cython code runs OK.
class EventBroadcaster(Generic[H]):
# class EventBroadcaster:
    """ Class that manages a set of subscribers and broadcasts messages to them. """

    def __init__(self) -> None:
        self._subscriptions: Set[Subscription] = set()

    # TODO: Once we are on Python >= 3.10, we can properly annotate `emit` using ParamSpec.
    def emit(self, *args, **kwargs) -> None:
        """ Notify all subscribers by calling the registered callback functions.
            All positional and keyword arguments are forwarded as-is
        """
        for subscription in self._subscriptions:
            # The type of the handler got erased in Subscription, so use cast to help
            # mypy or other type checkers see its true type.
            handler = cast(H, subscription.handler)
            handler(*args, **kwargs)

    def add_handler(self, handler: H) -> Subscription:
        """ Add a new subscription to the broadcast list.
            It will be notified when the event is fired.

            :param handler: method to be called when event is fired
        """
        new_sub = Subscription(handler, self._subscriptions)
        self._subscriptions.add(new_sub)
        return new_sub

    def is_subscribed(self) -> bool:
        """
        Check whether any events have subscribed to this event broadcaster
        :return: True, if any event has subscribed
                 False, otherwise
        """
        return len(self._subscriptions) > 0
