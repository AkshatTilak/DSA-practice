# 🧠 Technical Interview Preparation Vault

Welcome to the monolithic, localized Technical Interview Preparation Vault. This repository is built as a self-contained environment to master Data Structures & Algorithms (DSA), Data Science & Machine Learning (ML), Low-Level Design (LLD), and High-Level Design (HLD).

## 📂 Vault Directory Architecture

```text
interview-prep-vault/
│
├── 01_DSA/                   # Data Structures & Algorithms (Python / Java)
│   ├── arrays_and_hashing/
│   │   ├── README.md         # Core Concepts, Visual Flowcharts, Complexities
│   │   ├── q01_two_sum.py    # Multi-approach solutions (Brute Force vs Hash Map)
│   │   └── q01_test.py       # Pytest suite for validation
│
├── 02_Data_Science_ML/       # Data Science, ML, and AI Engineering
│   ├── architectures/        # Transformers, CNNs, GNNs
│   ├── classical_ml/         # Linear Regression, Tree models, Bias-Variance
│   └── systems_evaluation/   # Metrics (Precision/Recall, F1, ROC-AUC, MAPE)
│
├── 03_LLD/                   # Low-Level Design & Object-Oriented Programming
│   ├── design_patterns/      # Strategy, Factory, Singleton, Observer
│   └── case_studies/         # Design a Warehouse Inventory Management System
│
└── 04_HLD/                   # High-Level Design & System Architecture
    ├── system_components/    # Load Balancers, Caching, Message Queues (Kafka)
    └── real_world_cases/     # Design an Automated Vehicle Damage Auto-Penalty Pipeline
```

---

## 🏷️ Group-Based Categorization

Every challenge is tagged with one or more **groups** for cross-cutting filtering. You can filter by group on the dashboard to focus on a specific concept area.

### DSA Groups
| Group | Description | Example Challenges |
|-------|-------------|-------------------|
| **Array** | Array manipulation, traversal, prefix sums | Two Sum, Product of Array Except Self |
| **String** | String processing, character manipulation | Valid Anagram, Group Anagrams |
| **Hashing** | Hash maps, hash sets, frequency counting | Contains Duplicate, Longest Consecutive |
| **Two Pointers** | Converging/diverging pointer techniques | Valid Palindrome, 3Sum, Container With Most Water |
| **Sliding Window** | Variable/fixed-width window patterns | Best Time to Buy Stock, Min Window Substring |
| **Stack & Queue** | LIFO/FIFO structures, monotonic stacks | Valid Parentheses, Daily Temperatures |
| **Binary Search** | Divide-and-conquer on sorted data | Binary Search, Koko Eating Bananas |
| **Linked List** | Pointer-based sequential structures | Reverse Linked List, Detect Cycle |
| **Tree** | Binary trees, BSTs, traversals | Invert Tree, Validate BST, Level Order |
| **Heap / Priority Queue** | Min/max heaps, top-K problems | Kth Largest, Median from Stream |
| **Graph** | DFS, BFS, topological sort, union-find | Number of Islands, Course Schedule |
| **Dynamic Programming** | Optimal substructure, memoization | Climbing Stairs, Coin Change, LIS |
| **Backtracking** | Recursive exploration with pruning | Generate Parentheses |
| **Matrix** | 2D grid operations | Search 2D Matrix, Number of Islands |

### Data Science & ML Groups
| Group | Description |
|-------|-------------|
| **Classical ML** | Linear/Logistic Regression, Decision Trees, SVM, KNN |
| **Deep Learning** | Neural networks, backpropagation, architectures |
| **Transformers** | Self-attention, multi-head attention mechanisms |
| **Evaluation & Metrics** | Precision, Recall, F1, ROC-AUC, MSE, MAPE |
| **Computer Vision** | CNNs, convolution operations |
| **Sequence Models** | RNNs, LSTMs, temporal modeling |
| **Optimization** | Gradient descent, loss functions |

### LLD Groups
| Group | Description |
|-------|-------------|
| **Creational Patterns** | Singleton, Factory Method, Builder |
| **Structural Patterns** | Adapter, Decorator, Composite |
| **Behavioral Patterns** | Strategy, Observer, Command, Chain of Responsibility |
| **OOP Case Studies** | Parking Lot, Movie Booking, Elevator, Chess Game, etc. |
| **Concurrency** | Thread-safe designs, blocking queues, locks |
| **Caching & Storage** | LRU/LFU cache, key-value stores |
| **Game Design** | Tic-Tac-Toe, Snake & Ladder, Chess, Multiplayer Lobby |

### HLD Groups
| Group | Description |
|-------|-------------|
| **Distributed Systems** | Consistent hashing, sharding, replication |
| **Real-World Systems** | URL Shortener, Ride Sharing, Video Streaming, E-commerce |
| **Networking** | Load balancers, CDN, API gateways |
| **Databases** | Sharding, caching strategies, Redis |
| **Messaging** | Kafka, Pub-Sub, event streaming |
| **Data Pipelines** | Workflow orchestration, analytics platforms |

---

## 🚀 Interactive Learning Application

This repository features an interactive learning application built using Python and Streamlit. With it, you can:
1. **Browse & Filter by Group**: Click group cards on the dashboard to instantly filter challenges by category (e.g., Array, DP, Design Patterns).
2. **Browse Concepts**: Review visual mind-maps, definitions, and real-world system applications for each topic.
3. **Interactive Code Sandbox**: Implement solutions for each question directly inside a web-based code editor.
4. **Automated Verification**: Click a button to run the `pytest` suite in real time against your sandbox implementation.
5. **Compare Solutions**: View Naive vs. Optimal (Pythonic) vs. Java implementations with complexity tables.
6. **Context-Aware AI Assistant**: Chat with an AI agent powered by Gemini. The AI knows the exact challenge, your code draft, and test execution details to help you debug and learn.

### Getting Started

#### 1. Setup Environment
Ensure you have Python 3.11+ and Poetry installed. Set up dependencies by running:
```bash
poetry install
```

#### 2. Run the Interactive App
Start the Streamlit portal using the Poetry virtual environment:
```bash
poetry run streamlit run app.py
```
This opens the dashboard at `http://localhost:8501`.

#### 3. Run Automated Tests from CLI
You can also run all validation suites directly from the terminal:
```bash
poetry run pytest
```

---

## 🎯 Target Curriculums
- **DSA Top 100 GFG**: [GeeksforGeeks DSA Curriculum](https://www.geeksforgeeks.org/dsa/top-100-data-structure-and-algorithms-dsa-interview-questions-topic-wise/)
- **Data Science & ML GFG**: [GeeksforGeeks Data Science Interview Prep](https://www.geeksforgeeks.org/data-science/data-science-interview-questions-and-answers/)
- **LLD Sheet**: [AlgoSimplified LLD Sheet](https://algosimplified.in/lld-sheet/)
- **LeetCode Study Roadmap**: [LeetCode Top Interview 150](https://leetcode.com/studyplan/top-interview-150/)
