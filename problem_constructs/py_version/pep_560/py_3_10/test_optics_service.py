# Copyright(c) 2021 by Thermo Fisher Scientific
# All rights reserved. This file includes confidential and proprietary information
# of Thermo Fisher Scientific

from .optics_service import OpticsService
from .normalization import Normalization


def test_sanity_check_1():
    optics_service = OpticsService()
    assert optics_service is not None

    optics_service.execute_normalizations(Normalization.Spotsize)


def test_aliases():
    from collections.abc import Iterable as Iterable_from_abc
    from typing import Iterable as Iterable_from_typing

    print()
    print(f"identity of Iterable from collections.abc: {Iterable_from_abc}")
    print(f"                                     type: {type(Iterable_from_abc)}")
    print(f"         identity of Iterable from typing: {Iterable_from_typing}")
    print(f"                                     type: {type(Iterable_from_typing)}")

    # See typing.py: importing from typing and collections.abc is not quite the same thing, a
    # more complicated 'alias' done via a conversion class?
    assert Iterable_from_abc is not Iterable_from_typing
