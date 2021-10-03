
from typing import Tuple


def get_powers_(abc) -> Tuple[int, int, int]:
    return abc ** 2, abc ** 3, abc ** 4


# Python code runs OK.
# PyCharm type checking in the editor does flag this as an error:
#   Expected type 'int', got 'str' instead
#   Same warning given where function is called.
def get_powers(xyz: str) -> Tuple[int, int, int]:
    return xyz ** 2, xyz ** 3, xyz ** 4
