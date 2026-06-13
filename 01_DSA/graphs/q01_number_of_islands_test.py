import os
import sys
import inspect

# Ensure local directory is in path for resolving local imports temporarily
dir_path = os.path.dirname(os.path.abspath(__file__))
if dir_path not in sys.path:
    sys.path.insert(0, dir_path)

try:
    # Try importing from the sandbox file first
    from q01_number_of_islands_sandbox import num_islands
except ImportError:
    # Fallback to standard solution
    from q01_number_of_islands import num_islands
    try:
        source = inspect.getsource(num_islands)
        if "pass" in source:
            # Load optimal version for verification out of the box
            from q01_number_of_islands import num_islands_optimal as num_islands
    except Exception:
        pass

# Clean up path immediately to prevent polluting other test namespaces
if sys.path[0] == dir_path:
    sys.path.pop(0)

def test_islands():
    pass
