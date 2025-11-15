
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add the script's directory to the Python path to allow importing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts', 'lane_guard')))

from enforce_imports import main as enforce_imports_main


class TestEnforceImports(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.candidate_dir = os.path.join(self.test_dir, 'candidate')
        os.makedirs(self.candidate_dir)
        # We need to mock the CANDIDATE_DIR constant in the script
        self.candidate_dir_patcher = patch('enforce_imports.CANDIDATE_DIR', self.candidate_dir)
        self.candidate_dir_patcher.start()

    def tearDown(self):
        self.candidate_dir_patcher.stop()
        shutil.rmtree(self.test_dir)

    def _create_file(self, path, content):
        with open(os.path.join(self.candidate_dir, path), 'w') as f:
            f.write(content)

    @patch('sys.exit')
    @patch('sys.stdout')
    def test_no_forbidden_imports(self, mock_stdout, mock_exit):
        self._create_file("valid.py", "import os\nfrom sys import path")
        enforce_imports_main()
        mock_exit.assert_not_called()
        # Check that the success message is in the printed output
        self.assertTrue(any("No forbidden imports found." in call.args[0] for call in mock_stdout.write.call_args_list))


    @patch('sys.exit')
    @patch('sys.stdout')
    def test_forbidden_import(self, mock_stdout, mock_exit):
        self._create_file("invalid.py", "import lukhas.core")
        enforce_imports_main()
        mock_exit.assert_called_with(1)
        output = "".join(call.args[0] for call in mock_stdout.write.call_args_list)
        self.assertIn("Found forbidden import: lukhas.core", output)

    @patch('sys.exit')
    @patch('sys.stdout')
    def test_forbidden_import_from(self, mock_stdout, mock_exit):
        self._create_file("invalid_from.py", "from lukhas.utils import something")
        enforce_imports_main()
        mock_exit.assert_called_with(1)
        output = "".join(call.args[0] for call in mock_stdout.write.call_args_list)
        self.assertIn("Found forbidden import from: lukhas.utils", output)

    @patch('sys.exit')
    @patch('sys.stdout')
    def test_mixed_imports(self, mock_stdout, mock_exit):
        self._create_file("mixed.py", "import os\nimport lukhas\nfrom sys import path")
        enforce_imports_main()
        mock_exit.assert_called_with(1)
        output = "".join(call.args[0] for call in mock_stdout.write.call_args_list)
        self.assertIn("Found forbidden import: lukhas", output)

    @patch('sys.exit')
    @patch('sys.stdout')
    def test_syntax_error_file(self, mock_stdout, mock_exit):
        self._create_file("syntax_error.py", "import os\nthis is not valid python")
        enforce_imports_main()
        # The script should not exit with an error for a syntax error,
        # but it should print a message.
        mock_exit.assert_not_called()
        output = "".join(call.args[0] for call in mock_stdout.write.call_args_list)
        self.assertIn("Error parsing", output)
        self.assertIn("syntax_error.py", output)

if __name__ == '__main__':
    unittest.main()
