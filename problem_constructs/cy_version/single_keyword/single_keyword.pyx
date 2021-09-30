
def say_hello_to(name):
    return f"hello {name}"


def say_hello_to_keyword(name="betty"):
    return f"hello {name}"


class BedrockCity:
    def say_hello_to_instance(self, name):
        return f"hello {name}"

    @classmethod
    def say_hello_to_class(cls, name):
        return f"hello {name}"

    @staticmethod
    def say_hello_to_static(name):
        return f"hello {name}"


def welcome_wilma():
    # Calling a function that defines a single positional parameter with a keyword parameter
    # requires the 'always_allow_keywords' Cython directive. Otherwise exception raised:
    #       TypeError: say_hello_to() takes no keyword arguments
    # This option will be on by default from Cython 3.0 onwards!
    welcome = say_hello_to(name="Wilma")
    print(f"{welcome}")


def welcome_fred():
    # This is OK, i.e. passing a single positional parameter to a function that expects a single
    # positional parameter.
    welcome = say_hello_to("Fred")
    print(f"{welcome}")


def welcome_barney():
    # This is OK without the 'always_allow_keywords' directive because the function called has
    # been defined to take a single keyword parameter, not a single positional parameter.
    welcome = say_hello_to_keyword("Barney")
    print(f"{welcome}")


def welcome_dino():
    bedrock_city = BedrockCity()
    # This is OK without the 'always_allow_keywords' directive because the Python runtime passes
    # the instance of the class, self, as the first parameter implicitly.
    welcome = bedrock_city.say_hello_to_instance(name="Dino")
    print(f"{welcome} ... from BedrockCity instance method")

    # This is OK without the 'always_allow_keywords' directive because the Python runtime passes
    # the class object, cls, as the first parameter implicitly.
    welcome = BedrockCity.say_hello_to_class(name="Dino")
    print(f"{welcome} ... from BedrockCity class method")

    # This is not OK without the 'always_allow_keywords' directive because just tne name parameter
    # is passed, i.e. no additional implicit parameters are passed.
    welcome = BedrockCity.say_hello_to_static(name="Dino")
    print(f"{welcome} ... from BedrockCity static method")
