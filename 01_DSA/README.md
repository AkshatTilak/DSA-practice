# 01. Data Structures & Algorithms (DSA)

This section of the vault is dedicated to mastering standard Data Structures and Algorithms tested in technical interviews (LeetCode, GeeksforGeeks, etc.).

## 📂 Subdirectories
- `arrays_and_hashing/`: Array manipulation, hash map lookups, sliding window primitives, and tracking collections.
- *(Extendable to)* `two_pointers/`, `sliding_window/`, `stack/`, `binary_search/`, `trees/`, `graphs/`, `dynamic_programming/`.

## ⚙️ Module Structure Guidelines
For every topic subdirectory, we maintain:
1. `README.md`: Concepts definitions, visual ASCII flowcharts, complexities, and real-world system applications.
2. `qXX_[name].py`: Problem specification + plural implementations (Naive vs. Optimal vs. Java).
3. `qXX_test.py`: Standard `pytest` validation suite targeting the algorithms.

## 🧪 Running DSA Tests
To run tests specifically for this module, execute:
```bash
poetry run pytest 01_DSA/
```
