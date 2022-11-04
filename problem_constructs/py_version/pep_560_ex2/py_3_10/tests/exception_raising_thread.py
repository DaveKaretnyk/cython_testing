# Copyright (c) 2022 by FEI Company
# All rights reserved. This file includes confidential and proprietary
# information of FEI Company.

import threading
from typing import Any, Callable, Optional


class ExceptionRaisingThread(threading.Thread):
    """
    Wrapper around Thread class to propagate exceptions to the calling thread.
    """
    def __init__(self, target: Callable[..., Any]):
        super().__init__(target=target)
        self.exception: Optional[Exception] = None

    def run(self) -> None:
        """
        Method to invoke the callable object that is passed to the constructor as target argument.
        Method will catch assertion errors raised while running the callable object.

        Calling thread should invoke start() method to start running the callable object.
        Start method internally invokes object's run method.
        :return:
        """
        try:
            super().run()
        except Exception as e:
            self.exception = e

    def join(self, timeout=None) -> None:
        """
        Waits until the thread terminates and raises exceptions caught to the calling thread
        :return:
        """
        super().join(timeout=timeout)
        if self.exception:
            raise self.exception
