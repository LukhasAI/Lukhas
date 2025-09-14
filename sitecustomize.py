import os
import sys

root = os.path.abspath(os.getcwd())
if root in sys.path:
    sys.path.remove(root)
sys.path.insert(0, root)
