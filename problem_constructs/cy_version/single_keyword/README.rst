Single keyword calls
====================
Calling a function, or class static method, wth a single keyword parameter
when the function is defined to take a single positional parameter does not
work by default in Cython versions earlier than 3.0.

The Cython directive 'always_allow_keywords' can be used to solve the problem.
This option will be switched on by default in Cython version 3.0 and later.

More information:
* https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html?highlight=always_allow_keywords#compiler-directives
* https://github.com/cython/cython/issues/2881
* https://github.com/cython/cython/issues/3090
* https://thermofisher-asg.atlassian.net/browse/ASP-1430

However switching this directive on might cause problems for transpiled Python
code that interfaces to the C++ Qt library bindings, e.g. PyQt5.X. See
examples in 'single_keyword_qt'.
