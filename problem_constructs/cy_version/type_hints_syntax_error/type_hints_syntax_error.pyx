
from typing import Tuple


# Type hint specification is wrong -> Python code still runs OK ...
# But analyze the code, e.g. via mypy, then syntax error is flagged.
# PyCharm type hint checking in editor does not flag it as a syntax error:
# lightweight checks only that can be done live in the editor? I.e. no
# 'computationally expensive' checks?
#
# Cython code does not compile.
def get_sum_bad_type_hint(my_list: (int, int, int)):
    return sum(my_list)


# type hint specification is wrong -> code still runs OK
def get_sum_good_type_hint(my_list: Tuple[int, int, int]):
    return sum(my_list)
