Use of Typing NamedTuple
========================

Creating an instance of a class derived from typing.NamedTuple results in:
    TypeError: __new__() got an unexpected keyword argument '[argument name]' or TypeError: __new__() takes 1 positional argument but 3 were given
Workaround: use attrs instead for data containers.

More information:
* https://docs.python.org/3/library/typing.html#typing.NamedTuple
* https://www.attrs.org/en/stable/
* https://github.com/cython/cython/issues/2649
* https://github.com/cython/cython/issues/2917
* https://github.com/cython/cython/issues/2552 ... seems solved in Cython 3.0

TODO??? Example of problem in this directory.
