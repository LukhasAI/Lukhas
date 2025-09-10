import random


class DreamSeed:
    """
    A simple class to generate a dream symbol from a seed value.
    """

    def __init__(self, value):
        self.value = value
        random.seed(value)

    def generate_symbol(self):
        """
        Generates a random symbol.
        """
        return chr(random.randint(33, 126))