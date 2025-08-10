import os
import sys
import unittest

if __name__ == "__main__":
    # Add the root directory to the sys.path
    os.environ["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    sys.path.insert(0, os.environ["PYTHONPATH"])

    # Discover and run the tests
    loader = unittest.TestLoader()
    suite = loader.discover("tests")
    runner = unittest.TextTestRunner()
    result = runner.run(suite)

    # Exit with a non-zero status code if the tests failed
    if not result.wasSuccessful():
        sys.exit(1)
