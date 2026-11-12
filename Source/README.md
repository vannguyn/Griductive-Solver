# Griductive Solver - Source

This directory contains the application source code, puzzles, experiment results,
and unit tests for Griductive Solver.

## Setup & Run

```bash
cd Source
python -m venv .venv
# Activate .venv, then:
pip install -r requirements.txt
python main.py
```

## Run Tests

```bash
cd Source
pytest
```

Implement the modules in dependency order: `domain`, `clues`, `sat`,
`encoding`, `reasoning`, `agent`, `engine`, `app`, `gui`, and `experiments`.
