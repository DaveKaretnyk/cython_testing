Type hint specification wrong
=============================

**Description**
What happens in the type hint is wrong? E.g. indicates that a parameter should
be a str but it is called with an int.

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
