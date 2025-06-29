# 2D-Packing

A modular framework for solving 2D rectangle packing problems - packing identical m × n rectangular tiles into a larger p × q rectangle to maximize the tile count.

## Features

- **Multiple solving algorithms**: Mathematical, Greedy, Backtracking, ILP (OR-Tools)
- **Interactive Streamlit GUI** with enhanced visualizations
- **Symmetry detection** and duplicate elimination
- **Multiple optimal solutions** discovery with deduplication
- **Rich visualization** and export capabilities
- **Performance optimizations** (5000x+ speedup for optimal cases)
- **Comprehensive testing** and benchmarking
- **Extensible architecture** with modular solver design

## Quick Start

### Using the Interactive GUI
```bash
pip install -r requirements.txt
streamlit run streamlit_app_fixed.py
```

### Using the Framework Programmatically
```python
from src.core.problem import PackingProblem
from src.solvers.hybrid_solver import HybridSolver

# Define problem
problem = PackingProblem(
    container_w=40, container_h=48,
    tile_w=10, tile_h=10,
    allow_rotation=True
)

# Solve
solver = HybridSolver()
solution = solver.solve(problem)

print(f"Packed {solution.num_tiles} tiles ({solution.efficiency:.1f}% efficiency)")
```

## Key Achievements

- **Pinwheel pattern detection**: 40×40 with 24×16 → 4/4 tiles (96% efficiency)
- **Optimal rectangular packing**: 40×48 with 12×16 → 10/10 tiles (100% efficiency)  
- **Multiple orientations**: 40×48 with 8×10 → Both 4×6 and 5×4 grids found
- **Sub-second solving** for most common packing problems

## Installation

```bash
pip install -r requirements.txt
```

## Documentation

- See `RUN_GUI.md` for detailed GUI usage instructions
- See `PERFORMANCE_NOTES.md` for optimization details
- See `MULTIPLE_SOLUTIONS_FEATURE.md` for multi-solution capabilities
- See the `docs/` folder for API reference
