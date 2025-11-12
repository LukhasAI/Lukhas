import json
import subprocess
import sys
from unittest.mock import MagicMock

# Mock lukhas modules if they are not installed
try:
    import lukhas
except ImportError:
    sys.modules['lukhas'] = MagicMock()
    sys.modules['lukhas.core'] = MagicMock()
    sys.modules['lukhas.core.logging'] = MagicMock()

def check_licenses():
    """
    Checks for GPL-licensed packages and allows MIT, Apache, and BSD licenses.
    """
    allowed_licenses = ['MIT', 'Apache Software License', 'BSD License']
    blocked_licenses = ['GPL', 'LGPL']

    try:
        # Get the license information for all installed packages
        result = subprocess.run(
            ['pip-licenses', '--format=json'],
            capture_output=True,
            text=True,
            check=True
        )
        packages = json.loads(result.stdout)

        # Check the license of each package
        has_blocked_license = False
        for package in packages:
            license_str = package.get('License', 'Unknown')
            if any(blocked in license_str for blocked in blocked_licenses):
                print(f"ERROR: Found blocked license '{license_str}' for package '{package.get('Name', 'Unknown')}'")
                has_blocked_license = True
            elif any(allowed in license_str for allowed in allowed_licenses):
                print(f"SUCCESS: Found allowed license '{license_str}' for package '{package.get('Name', 'Unknown')}'")
            else:
                print(f"WARNING: Found license '{license_str}' for package '{package.get('Name', 'Unknown')}' that is not explicitly allowed or blocked")

        if has_blocked_license:
            sys.exit(1)

    except FileNotFoundError:
        print("ERROR: 'pip-licenses' is not installed. Please install it with 'pip install pip-licenses'")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: 'pip-licenses' failed to run: {e}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("ERROR: Failed to parse the output of 'pip-licenses'.")
        sys.exit(1)

if __name__ == '__main__':
    check_licenses()
