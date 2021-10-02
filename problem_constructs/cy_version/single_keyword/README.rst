Single keyword calls
====================

**Description**
Calling a function (or static method of a class) wth a single keyword
parameter when the function is defined to take a single positional parameter
does not work by default in Cython versions earlier than 3.0.

The Cython directive 'always_allow_keywords' can be used to solve the problem.
This option will be switched on by default in Cython version 3.0 and later.

However switching this directive on might cause problems for transpiled Python
code that interfaces to the C++ Qt library bindings, e.g. PyQt5.X. The
AutoStar Sherpa application has instances of this problem. See examples in
'single_keyword_qt'.

**Solutions / Workarounds**
* Change the call to the function to supply a single positional parameter
  rather than keyword parameter.
* Change the function definition to expect a single keyword parameter rather
  then a single positional parameter. **But take possible future changes into
  account. E.g. positional parameters cannot be added to the function
  definition without also changing all calls.**

**More information**
* https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html?highlight=always_allow_keywords#compiler-directives
* https://github.com/cython/cython/issues/2881
* https://github.com/cython/cython/issues/3090
* Thermo Fisher AutoStar: https://thermofisher-asg.atlassian.net/browse/ASP-1430
