Type hint specification wrong
=============================

**Description**
What happens if the type hint is wrong? E.g. hint indicates that a parameter
should be a str but it is called with an int.

Type hints are used by Cython. That is, what is specified in the type hint
should match what actually happens at runtime. This is somewhat logical since
it is consistent with how Python code is normally augmented to allow
performance improvements using Cython. E.g.:

    def integrate_f(double a, double b, int N):
        cdef int i
        cdef double s
        cdef double dx
        s = 0
        dx = (b - a) / N
        for i in range(N):
            s += f(a + i * dx)
        return s * dx

Python code runs OK. Error flagged, e.g., by both mypy and PyCharm editor.

The Cython code compiles but does not run.

**More information**
Python cod runs OK.

Running mypy on the files shows a syntax error:
    type_hints_spec_wrong.py:14: error: Unsupported operand types for ** ("str" and "int")

PyCharm checking in editor does flag an error:
    Expected type 'int', got 'str' instead
Same warning given where function is called.

Cython code compiles, but does not run:
    Traceback (most recent call last):
        File ".\type_hints_spec_wrong\run_examples.py", line 9, in <module>
        my_results = get_powers(2)
        TypeError: Argument 'xyz' has incorrect type (expected str, got int)
