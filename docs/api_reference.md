# API Reference

This document provides a comprehensive reference for the Rectangle Packing Framework API.

## Core Classes

### PackingProblem

Defines a 2D rectangle packing problem.

```python
from src.core.problem import PackingProblem

problem = PackingProblem(
    container_w=40,
    container_h=48, 
    tile_w=10,
    tile_h=10,
    max_tiles=None,          # Optional: limit number of tiles
    allow_rotation=True,     # Allow tile rotation
    require_centering=True   # Prefer centered solutions
)
```

**Properties:**
- `container_area`: Total container area
- `tile_area`: Area of a single tile  
- `theoretical_max_tiles`: Maximum possible tiles based on area

### PackingSolution

Represents a solution to a packing problem.

```python
from src.core.solution import PackingSolution

solution = PackingSolution(
    tile_positions=[(x, y, w, h, orientation), ...],
    container_w=40,
    container_h=48,
    solve_time=1.5,
    solver_name="Hybrid",
    metadata={"method": "ilp"}
)
```

**Properties:**
- `num_tiles`: Number of tiles placed
- `efficiency`: Packing efficiency percentage
- `bounding_box`: (min_x, min_y, max_x, max_y) of placed tiles
- `is_centered`: Whether solution is centered

## Solvers

### MathematicalSolver

Finds perfect rectangular arrangements analytically.

```python
from src.solvers.mathematical_solver import MathematicalSolver

solver = MathematicalSolver()
solution = solver.solve(problem)
solutions = solver.solve_all_optimal(problem, max_solutions=10)
```

**Best for:** Problems with perfect grid solutions, very fast execution.

### GreedySolver

Fast heuristic solver with different strategies.

```python
from src.solvers.greedy_solver import GreedySolver

# Bottom-left strategy
solver = GreedySolver("bottom_left")

# Center-outward strategy  
solver = GreedySolver("center_out")

solution = solver.solve(problem)
```

**Best for:** Quick approximate solutions, large problems.

### BacktrackSolver

Exhaustive search for small to medium problems.

```python
from src.solvers.backtrack_solver import BacktrackSolver

solver = BacktrackSolver(
    max_solutions=50,
    time_limit=30.0
)

solution = solver.solve(problem)
solutions = solver.solve_all_optimal(problem, max_solutions=10)
```

**Best for:** Small problems where optimal solution is required.

### ILPSolver

Integer Linear Programming solver (requires OR-Tools).

```python
from src.solvers.ilp_solver import ILPSolver

solver = ILPSolver(
    time_limit=60.0,
    compactness_weight=0.1
)

solution = solver.solve(problem)
```

**Best for:** Medium problems, provably optimal solutions.

### HybridSolver

Multi-tier solver that tries different approaches.

```python
from src.solvers.hybrid_solver import HybridSolver

solver = HybridSolver(time_limit=60.0)

# Single best solution
solution = solver.solve(problem)

# All optimal solutions
solutions = solver.solve_all_optimal(problem, max_solutions=10)
```

**Best for:** General use, automatically selects best approach.

## Visualization

### Basic Plotting

```python
from src.visualization.plotter import visualize_solution, visualize_multiple_solutions

# Single solution
fig = visualize_solution(solution, problem, title="My Solution")

# Multiple solutions
fig = visualize_multiple_solutions(solutions, problem, max_cols=3)

# Quick plot
from src.visualization.plotter import quick_plot
quick_plot(solution, save_path="solution.png")
```

### Interactive Plots

```python
from src.visualization.interactive import create_interactive_solution_plot

# Create interactive plot (requires Plotly)
fig = create_interactive_solution_plot(solution, problem)
fig.show()
```

### Export Functions

```python
from src.visualization.export import (
    export_solution_to_json,
    export_solution_to_csv, 
    save_solution_as_image,
    create_solution_report
)

# Export solution data
export_solution_to_json(solution, "solution.json")
export_solution_to_csv(solution, "solution.csv")

# Export visualization
save_solution_as_image(solution, "solution.png", format="png", dpi=300)

# Create HTML report
create_solution_report(problem, solutions, "report.html")
```

## Utilities

### Validation

```python
from src.utils.validation import validate_solution, check_feasibility

# Validate solution
is_valid, errors = validate_solution(solution, problem)

# Check problem feasibility
is_feasible, warnings = check_feasibility(problem)
```

### Symmetry Detection

```python
from src.utils.symmetry import deduplicate_solutions, are_solutions_equivalent

# Remove duplicate solutions
unique_solutions = deduplicate_solutions(solutions, problem)

# Check if two solutions are equivalent
equivalent = are_solutions_equivalent(solution1, solution2)
```

### Geometric Operations

```python
from src.core.geometry import center_solution, rotate_solution_90

# Center a solution
centered_positions = center_solution(tile_positions, container_w, container_h)

# Rotate solution 90 degrees
rotated_positions = rotate_solution_90(tile_positions, container_w, container_h)
```

## Configuration

```python
from src.config.solver_config import SolverConfig, ProblemConfig

# Adjust solver settings
SolverConfig.ILP_TIME_LIMIT = 120
SolverConfig.COMPACTNESS_WEIGHT = 0.2

# Adjust problem defaults
ProblemConfig.ALLOW_ROTATION = False
ProblemConfig.REQUIRE_CENTER_ALIGNMENT = True
```

## Error Handling

All solvers handle errors gracefully and return empty solutions rather than throwing exceptions for invalid inputs. Use validation utilities to check inputs beforehand:

```python
# Check if problem is feasible
is_feasible, warnings = check_feasibility(problem)
if not is_feasible:
    print("Problem is not feasible!")

# Validate solution
is_valid, errors = validate_solution(solution, problem)
if not is_valid:
    print(f"Invalid solution: {errors}")
```

## Performance Tips

1. **Use HybridSolver** for general cases - it automatically selects the best approach
2. **Set time limits** for ILP and backtracking solvers to avoid long waits
3. **Use MathematicalSolver first** for problems that might have perfect grid solutions
4. **Enable rotation** when tile dimensions are different
5. **Use GreedySolver** for very large problems where speed is more important than optimality

## Type Hints

The framework uses type hints throughout. Key types:

```python
from typing import List, Tuple

# Tile position: (x, y, width, height, orientation)
TilePosition = Tuple[int, int, int, int, str]

# List of tile positions
TilePositions = List[TilePosition]
```
