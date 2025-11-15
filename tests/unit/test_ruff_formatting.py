def test_function(x, y):
    """Test function with poor formatting."""
    result = x + y
    return result


class SampleClass:
    def __init__(self, name: str):
        self.name = name

    def method(self) -> str:
        return f"Hello {self.name}"


if __name__ == "__main__":
    test = SampleClass("World")
    print(test.method())
