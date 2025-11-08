
import builtins
import sys
import unittest
from unittest.mock import patch


class TestAuthSecurity(unittest.TestCase):
    def test_import_error_without_jwt(self):
        original_import = builtins.__import__

        def import_mock(name, *args, **kwargs):
            if name == 'jwt':
                raise ImportError("Mocked ImportError for jwt")
            return original_import(name, *args, **kwargs)

        # Unload the module if it was already imported
        if 'labs.core.security.auth' in sys.modules:
            del sys.modules['labs.core.security.auth']

        with patch('builtins.__import__', side_effect=import_mock):
            with self.assertRaises(ImportError) as cm:
                # The import needs to be reloaded to trigger the mock
                from importlib import reload

                from labs.core.security import auth
                reload(auth)

        self.assertIn("The 'PyJWT' package is required for authentication but is not installed.", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
