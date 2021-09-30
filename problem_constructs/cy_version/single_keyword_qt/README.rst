Single keyword calls and Qt
===========================
Calling a function, or class static method, wth a single keyword parameter
when the function is defined to take a single positional parameter does not
work by default in Cython versions earlier than 3.0.

The Cython directive 'always_allow_keywords' can be used to solve the problem.
This option will be switched on by default in Cython version 3.0 and later.

However switching this directive on might cause problems for transpiled Python
code that interfaces to the C++ Qt library bindings, e.g. PyQt5.X.

More information:
* https://thermofisher-asg.atlassian.net/browse/ASP-1430

TODO??? Example of problem in this directory.
