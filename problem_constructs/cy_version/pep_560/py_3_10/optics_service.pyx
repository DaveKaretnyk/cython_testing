# Copyright(c) 2021 by Thermo Fisher Scientific
# All rights reserved. This file includes confidential and proprietary information
# of Thermo Fisher Scientific

# Depending on the Python version, importing from collections.abc is not an alias for importing
# from typing! Python < 3.9? But even in 3.10 importing from collections.abc causes issues
# # for Cython.
from typing import Iterable
# from collections.abc import Iterable

from .normalization import Normalization


class OpticsService:
    """ Provide access to Optics related parameters of the microscope.
    """

    def __init__(self) -> None:
        pass

    # Cython issue: APITS-260, causes:
    #   TypeError: 'ABCMeta' object is not subscriptable
    def execute_normalizations(self, normalizations: Iterable[Normalization]) -> None:
        """ Perform normalization of the specified sub systems.
        This method is synchronous. It typically takes several seconds to
        complete on a real system depending on number of normalizations executed.
        """
        print(f"calling execute_normalization with: {normalizations}")
