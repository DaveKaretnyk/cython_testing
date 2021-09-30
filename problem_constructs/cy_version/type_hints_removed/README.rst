Type hints 'removed'?
=====================

Type annotations information is lost. In Python it is possible on runtime to
retrieve the type annotations and use this information. Cythonization removes
this meta data, which means that code that depend on it no longer works.
Workaround: For classes defined by the attr library it is possible to move the
type inside the attrib call instead of using a type annotation. For example,
change:
    x: int = attrib() to x = attrib(type=int).
Then attr.fields method can be used to get the type info for the fields.

More information:
* ???

TODO??? Example of problem in this directory.
