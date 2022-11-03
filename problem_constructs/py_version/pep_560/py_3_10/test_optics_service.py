from .optics_service import OpticsService
from .normalization import Normalization


def test_sanity_check_1():
    optics_service = OpticsService()
    assert optics_service is not None

    optics_service.execute_normalizations(Normalization.Spotsize)


def test_sanity_check_2():
    optics_service = OpticsService()
    optics_service.stigmator_set_condenser(1.2, 1.3)
    optics_service.stigmator_set_condenser((1.21, 1.31))


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
