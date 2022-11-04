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

