import os
import sys
import inspect

# Ensure local directory is in path for resolving local imports temporarily
dir_path = os.path.dirname(os.path.abspath(__file__))
if dir_path not in sys.path:
    sys.path.insert(0, dir_path)

try:
    # Try importing from the sandbox file first (created by Streamlit code runner)
    from q01_two_sum_sandbox import two_sum
except ImportError:
    # Fallback to standard solution
    from q01_two_sum import two_sum
    try:
        # If the user has not written a solution yet, run tests on optimal solution for validation
        source = inspect.getsource(two_sum)
        if "pass" in source:
            from q01_two_sum import two_sum_optimal as two_sum
    except Exception:
        pass

# Clean up path immediately to prevent polluting other test namespaces
if sys.path[0] == dir_path:
    sys.path.pop(0)

def test_two_sum_basic():
    assert sorted(two_sum([2, 7, 11, 15], 9)) == [0, 1]

def test_two_sum_duplicate():
    assert sorted(two_sum([3, 3], 6)) == [0, 1]

def test_two_sum_negative():
    assert sorted(two_sum([-1, -3, 4, 2], -1)) == [1, 3]

def test_two_sum_large():
    assert sorted(two_sum([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 19)) == [8, 9]

def test_two_sum_no_match():
    # If no match exists, return empty list
    assert two_sum([1, 2, 3], 10) == []
