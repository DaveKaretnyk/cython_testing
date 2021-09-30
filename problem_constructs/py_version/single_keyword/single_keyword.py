
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
    welcome = say_hello_to(name="Wilma")
    print(f"{welcome}")


def welcome_fred():
    welcome = say_hello_to("Fred")
    print(f"{welcome}")


def welcome_barney():
    welcome = say_hello_to_keyword("Barney")
    print(f"{welcome}")


def welcome_dino():
    bedrock_city = BedrockCity()
    welcome = bedrock_city.say_hello_to_instance(name="Dino")
    print(f"{welcome} ... from BedrockCity instance method")

    welcome = BedrockCity.say_hello_to_class(name="Dino")
    print(f"{welcome} ... from BedrockCity class method")

    welcome = BedrockCity.say_hello_to_static(name="Dino")
    print(f"{welcome} ... from BedrockCity static method")
