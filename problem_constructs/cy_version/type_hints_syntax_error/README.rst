Type hint syntax error
======================

**Description**
What happens if the type hint is syntactically wrong?

Python code runs OK. mypy flags the error, PyCharm editor does not.

The Cython code does not compile.

**Solutions / Workarounds**
* Python code might still run OK even if the type hint is syntactically wrong.
* If using Cython then type hints must be correct.

**More information**
Python code runs OK.

Running mypy on the file shows a syntax error:
    type_hints_syntax_error.py:10: error: Syntax error in type annotation
    type_hints_syntax_error.py:10: note: Suggestion: Use Tuple[T1, ..., Tn] instead of (T1, ..., Tn)

PyCharm checking in editor does not flag any errors.

Cython code does not compile:
    type_hints_syntax_error/type_hints_syntax_error.pyx(13): error C2065: '__pyx_ctuple_int__and_int__and_int': undeclared identifier
    type_hints_syntax_error/type_hints_syntax_error.pyx(13): error C2146: syntax error: missing ';' before identifier '__pyx_v_my_list'
    type_hints_syntax_error/type_hints_syntax_error.pyx(12): error C2065: '__pyx_v_my_list': undeclared identifier
    type_hints_syntax_error/type_hints_syntax_error.pyx(12): error C2065: '__pyx_v_my_list': undeclared identifier
    type_hints_syntax_error/type_hints_syntax_error.pyx(12): warning C4013: '__pyx_convert__from_py___pyx_ctuple_int__and_int__and_int' undefined; assuming extern returning int
    type_hints_syntax_error/type_hints_syntax_error.pyx(12): warning C4013: '__pyx_pf_23type_hints_syntax_error_23type_hints_syntax_error_get_sum_bad_type_hint' undefined; assuming extern returning int
    type_hints_syntax_error/type_hints_syntax_error.pyx(12): error C2065: '__pyx_ctuple_int__and_int__and_int': undeclared identifier
    type_hints_syntax_error/type_hints_syntax_error.pyx(12): error C2146: syntax error: missing ')' before identifier '__pyx_v_my_list'
    type_hints_syntax_error/type_hints_syntax_error.pyx(12): error C2059: syntax error: ')'
    type_hints_syntax_error/type_hints_syntax_error.pyx(12): error C2146: syntax error: missing ')' before identifier '__pyx_v_my_list'
    type_hints_syntax_error/type_hints_syntax_error.pyx(12): error C2081: '__pyx_ctuple_int__and_int__and_int': name in formal parameter list illegal
    type_hints_syntax_error/type_hints_syntax_error.pyx(12): error C2061: syntax error: identifier '__pyx_v_my_list'
    type_hints_syntax_error/type_hints_syntax_error.pyx(12): error C2059: syntax error: ';'
    type_hints_syntax_error/type_hints_syntax_error.pyx(12): error C2059: syntax error: ')'
    type_hints_syntax_error/type_hints_syntax_error.pyx(12): error C2449: found '{' at file scope (missing function header?)
    type_hints_syntax_error/type_hints_syntax_error.pyx(12): error C2059: syntax error: '}'
    type_hints_syntax_error/type_hints_syntax_error.pyx(17): error C2065: '__pyx_pw_23type_hints_syntax_error_23type_hints_syntax_error_3get_sum_good_type_hint': undeclared identifier
    type_hints_syntax_error/type_hints_syntax_error.pyx(17): warning C4312: 'type cast': conversion from 'int' to 'PyCFunction' of greater size
    type_hints_syntax_error/type_hints_syntax_error.pyx(17): error C2099: initializer is not a constant
    type_hints_syntax_error/type_hints_syntax_error.pyx(17): warning C4047: 'initializing': 'PyCFunction' differs in levels of indirection from 'int'
