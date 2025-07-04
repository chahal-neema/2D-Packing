# Rectangle Packing Framework

A modular framework for solving 2D rectangle packing problems with multiple algorithms and visualization tools.

This project provides a complete library for experimenting with and comparing
different packing strategies.  The repository contains the core data structures
(`PackingProblem` and `PackingSolution`), several solver implementations and a
small visualisation toolkit.  An interactive Streamlit application makes it easy
to try out various scenarios.

## Features

- Multiple solving algorithms (Mathematical, Greedy, Backtracking, ILP)
- Symmetry detection and duplicate elimination
- Rich visualization and export capabilities
- Comprehensive testing and benchmarking
- Extensible architecture

### Repository Layout

- **src/core** – basic problem and solution classes
- **src/solvers** – several solver implementations including a hybrid solver
- **src/visualization** – utilities for plotting packing results
- **examples** – simple usage samples
- **tests** – unit tests for solvers and helpers
- **streamlit_app.py** – interactive Streamlit interface

## Quick Start

```python
from src.core.problem import PackingProblem
from src.solvers.hybrid_solver import HybridSolver
from src.visualization.plotter import visualize_solutions

# Define problem
problem = PackingProblem(
    container_w=40, container_h=48,
    tile_w=10, tile_h=10,
    allow_rotation=True
)

# Solve
solver = HybridSolver()
solutions = solver.solve_all_optimal(problem)

# Visualize
visualize_solutions(problem, solutions)
```

### Running the Streamlit Interface

You can experiment with the solvers visually using the Streamlit app:

```bash
streamlit run streamlit_app.py
```

Open the provided URL in your browser and adjust the parameters to see the
different algorithms in action.

## Installation

```bash
pip install -r requirements.txt
```

## Documentation

See the `docs/` folder for detailed documentation.

## Why Rectangle Packing is Challenging

Packing rectangles optimally is deceptively hard.  The formal problem of tiling
a `p×q` container with as many `m×n` tiles as possible is a variant of the
two‑dimensional bin packing problem.  This decision problem is known to be
strongly NP‑hard via a reduction from 3‑Partition, which means the search space
grows exponentially with the instance size.  There is no known polynomial time
algorithm that is guaranteed to find the optimal layout for all inputs.

Optimal solutions often require **non‑guillotine** or “interlocking” patterns
that cannot be produced by a sequence of straight edge‑to‑edge cuts.  Many fast
heuristics only generate guillotine‑cuttable layouts and therefore miss these
arrangements entirely.  Allowing tile rotation further enlarges the space of
valid placements that must be explored.

The solvers in this repository illustrate several approaches.  The exhaustive
backtracking solver searches every legal placement while applying symmetry
breaking and pruning rules to keep the computation tractable.  The ILP solver
recasts the problem as an exact cover instance and relies on a mathematical
optimizer.  For larger scenarios where exhaustive search is impractical,
heuristic methods such as Skyline or MaxRects provide high‑quality solutions
quickly, though without a guarantee of optimality.
