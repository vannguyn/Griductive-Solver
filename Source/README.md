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
pytest -q
```

## Validate a Puzzle

The validator checks the schema, uniqueness, and whether the public deduction
agent solves the puzzle without guessing:

```bash
cd Source
python main.py --validate --puzzle puzzles/3x3/p01.json
```

## Run the Benchmark Suite

This evaluates every JSON puzzle under `puzzles/` and writes CSV, LaTeX, and
runtime-chart outputs to `results/`:

```bash
cd Source
python main.py --benchmark
```

Implement the modules in dependency order: `domain`, `clues`, `sat`,
`encoding`, `reasoning`, `agent`, `engine`, `app`, `gui`, and `experiments`.
