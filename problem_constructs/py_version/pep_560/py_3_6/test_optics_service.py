# Copyright(c) 2021 by Thermo Fisher Scientific
# All rights reserved. This file includes confidential and proprietary information
# of Thermo Fisher Scientific

from .optics_service import OpticsService
from .normalization import Normalization


def test_sanity_check_1():
    optics_service = OpticsService()
    assert optics_service is not None

    optics_service.execute_normalizations(Normalization.Spotsize)
