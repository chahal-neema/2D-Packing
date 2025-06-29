"""
Integer Linear Programming solver for rectangle packing.
"""

from typing import List, Optional
import time

try:
    from ortools.linear_solver import pywraplp
    ORTOOLS_AVAILABLE = True
except ImportError:
    ORTOOLS_AVAILABLE = False

from .base_solver import BaseSolver
from ..core.problem import PackingProblem
from ..core.solution import PackingSolution

class ILPSolver(BaseSolver):
    """Integer Linear Programming solver using OR-Tools."""
    
    def __init__(self, time_limit: float = 60.0, compactness_weight: float = 0.1):
        super().__init__("ILP")
        self.time_limit = time_limit
        self.compactness_weight = compactness_weight
        
        if not ORTOOLS_AVAILABLE:
            raise ImportError("OR-Tools is required for ILP solver. Install with: pip install ortools")
    
    def solve(self, problem: PackingProblem) -> PackingSolution:
        """Solve using Integer Linear Programming."""
        self._start_timing()
        
        # Create solver
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            raise RuntimeError("Could not create SCIP solver")
        
        solver.SetTimeLimit(int(self.time_limit * 1000))  # Convert to milliseconds
        
        # Calculate bounds
        max_tiles = problem.max_tiles or problem.theoretical_max_tiles
        center_x = problem.container_w / 2
        center_y = problem.container_h / 2
        
        # Variables: x[i,j,k,o] = 1 if tile i is placed at (j,k) with orientation o
        orientations = [(problem.tile_w, problem.tile_h)]
        if problem.allow_rotation and problem.tile_w != problem.tile_h:
            orientations.append((problem.tile_h, problem.tile_w))
        
        x = {}
        for i in range(max_tiles):
            for j in range(problem.container_w):
                for k in range(problem.container_h):
                    for o, (w, h) in enumerate(orientations):
                        if j + w <= problem.container_w and k + h <= problem.container_h:
                            x[i, j, k, o] = solver.IntVar(0, 1, f"x_{i}_{j}_{k}_{o}")
        
        # Constraints: Each tile placed at most once
        for i in range(max_tiles):
            constraint = solver.Constraint(0, 1, f"place_tile_{i}")
            for j in range(problem.container_w):
                for k in range(problem.container_h):
                    for o in range(len(orientations)):
                        if (i, j, k, o) in x:
                            constraint.SetCoefficient(x[i, j, k, o], 1)
        
        # Constraints: No overlapping
        for cell_x in range(problem.container_w):
            for cell_y in range(problem.container_h):
                constraint = solver.Constraint(0, 1, f"cell_{cell_x}_{cell_y}")
                for i in range(max_tiles):
                    for j in range(problem.container_w):
                        for k in range(problem.container_h):
                            for o, (w, h) in enumerate(orientations):
                                if (i, j, k, o) in x:
                                    if (j <= cell_x < j + w) and (k <= cell_y < k + h):
                                        constraint.SetCoefficient(x[i, j, k, o], 1)
        
        # Objective: Maximize tiles with compactness bonus
        objective = solver.Objective()
        for i in range(max_tiles):
            for j in range(problem.container_w):
                for k in range(problem.container_h):
                    for o in range(len(orientations)):
                        if (i, j, k, o) in x:
                            # Base reward for placing tile
                            base_reward = 1000
                            
                            # Compactness bonus
                            w, h = orientations[o]
                            tile_center_x = j + w / 2
                            tile_center_y = k + h / 2
                            distance = abs(tile_center_x - center_x) + abs(tile_center_y - center_y)
                            compactness_bonus = self.compactness_weight * (50 - distance)
                            
                            coefficient = base_reward + compactness_bonus
                            objective.SetCoefficient(x[i, j, k, o], coefficient)
        
        objective.SetMaximization()
        
        # Solve
        status = solver.Solve()
        self._end_timing()
        
        # Extract solution
        if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
            tile_positions = []
            for i in range(max_tiles):
                for j in range(problem.container_w):
                    for k in range(problem.container_h):
                        for o, (w, h) in enumerate(orientations):
                            if (i, j, k, o) in x and x[i, j, k, o].solution_value() > 0.5:
                                orientation_desc = "rotated" if o == 1 else "original"
                                tile_positions.append((j, k, w, h, orientation_desc))
            
            return PackingSolution(
                tile_positions=tile_positions,
                container_w=problem.container_w,
                container_h=problem.container_h,
                solve_time=self.solve_time,
                solver_name=self.name,
                metadata={
                    'status': 'optimal' if status == pywraplp.Solver.OPTIMAL else 'feasible',
                    'objective_value': solver.Objective().Value(),
                    'variables': len(x),
                    'compactness_weight': self.compactness_weight
                }
            )
        else:
            return PackingSolution(
                tile_positions=[],
                container_w=problem.container_w,
                container_h=problem.container_h,
                solve_time=self.solve_time,
                solver_name=self.name,
                metadata={'status': 'no_solution'}
            )
