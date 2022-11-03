TypeError: 'ABCMeta' object is not subscriptable
================================================

**Description**
Python code runs OK, 3.6 and 3.10.

Cython code transpiles but does not run (3.6 and 3.10) if Iterable is imported
from 'collections.abc' instead 'typing':
    TypeError: 'ABCMeta' object is not subscriptable

* Importing from 'collections.abc' should be equivalent to importing from
  'typing' and it seems to work ok when running Python code. But not when
  running Cython code.
* Running mypy does not reveal any violations.
* Big delta between the typing module of 3.6 and 3.10. Including the some
  alias classes in 3.10 which are used to alias types in 'typing' back to
  'collections.abc'.
* General rule: using the typing Iterable for type annotations, and the
  collections iterable for use as a superclass.
    * https://stackoverflow.com/questions/52827463/collections-iterable-vs-typing-iterable-in-type-annotation-and-checking-for-iter
    * https://peps.python.org/pep-0585/
