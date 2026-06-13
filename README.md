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

## 🚀 Interactive Learning Application

This repository features an interactive learning application built using Python and Streamlit. With it, you can:
1. **Browse Concepts**: Review visual mind-maps, definitions, and real-world system applications for each topic.
2. **Interactive Code Sandbox**: Implement solutions for each question directly inside a web-based code editor.
3. **Automated Verification**: Click a button to run the `pytest` suite in real time against your sandbox implementation.
4. **Compare Solutions**: View Naive vs. Optimal (Pythonic) vs. Java implementations with complexity tables.
5. **Context-Aware AI Assistant**: Chat with an AI agent powered by Gemini. The AI knows the exact challenge, your code draft, and test execution details to help you debug and learn.

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
- **LeetCode Study Roadmap**: [LeetCode Top Interview 150](https://leetcode.com/studyplan/top-interview-150/)
