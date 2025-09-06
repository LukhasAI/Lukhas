

def test_function(x, y):
    """Test function with poor formatting."""
    result = x + y
    return result


class TestClass:
    def __init__(self, name: str):
        self.name = name

    def method(self) -> str:
        return f"Hello {self.name}"


if __name__ == "__main__":
    test = TestClass("World")
    print(test.method())
