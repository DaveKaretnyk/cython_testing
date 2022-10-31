Generic types and type hints
============================

**Description**
Use of some generic types in type hints causing issues with Cython code.

Python code runs OK: 3.6 and 3.10.

Cython code runs OK: 3.6 but not in 3.10.

Modify the code so that classes do not inherit from parameterized Generic ->
Cython code runs OK. See files i_pyinteractivetask.pyx, interactive_task.pyx,
pyinteractivetask_base.pyx and pytask_event.pyx.

But does not always fail, see file column_mode.py in AutoStar_Common code?

TypeError: 'type' object is not subscriptable.
TypeError: 'ABCMeta' object is not subscriptable.

https://thermofisher-asg.atlassian.net/browse/APITS-260

https://github.com/cython/cython/issues/2753

https://peps.python.org/pep-0560/
