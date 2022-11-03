# Depending on the Python version, importing from collections.abc is not an alias for importing
# from typing! Python < 3.9? But even in 3.10 importing from collections.abc causes issues
# # for Cython.
from typing import Iterable
from collections.abc import Iterable as abc_Iterable

from .normalization import Normalization


class OpticsService:
    """ Provide access to Optics related parameters of the microscope.
    """

    def __init__(self) -> None:
        pass

    # Cython issue:
    #   TypeError: 'ABCMeta' object is not subscriptable
    def execute_normalizations(self, normalizations: Iterable[Normalization]) -> None:
        """ Perform normalization of the specified sub systems.
        This method is synchronous. It typically takes several seconds to
        complete on a real system depending on number of normalizations executed.
        """
        print(f"calling execute_normalization with: {normalizations}")

    def stigmator_set_condenser(self, x, y=None):
        self._perform_tuple_function(self._impl_set_condenser_stigmator, x, y)

    def _perform_tuple_function(self, function, x, y):
        if y is None and isinstance(x, abc_Iterable) and len(x) == 2:
            function(*x)
        else:
            function(x, y)

    def _impl_set_condenser_stigmator(self, x, y):
        # server call... self._condenser_stigmator.set_input_value(vector_value)
        print(f"set condenser stig to: {(x, y)}")
