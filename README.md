# Rectangle Packing Framework

A modular framework for solving 2D rectangle packing problems with multiple algorithms and visualization tools.

## Features

- Multiple solving algorithms (Mathematical, Greedy, Backtracking, ILP)
- Symmetry detection and duplicate elimination
- Rich visualization and export capabilities
- Comprehensive testing and benchmarking
- Extensible architecture

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

## Installation

```bash
pip install -r requirements.txt
```

## Documentation

See the `docs/` folder for detailed documentation.
