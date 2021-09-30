Mock instantiation
==================

Instantiating a mock class that overrides abstract methods by assigning the
mock function at class level like this
    some_method = create_autospec(SomeAbstractClass.some_method)
fails with:
    TypeError: Can't instantiate abstract class [class name] with abstract methods [method names]

Workaround: implement a function that overrides the abstract method which in
turn calls the mock function.

More information:
* ???

TODO??? Example of problem in this directory.
