"""
Mathematical solver for perfect rectangular arrangements.
"""

from typing import List, Tuple
import math

from .base_solver import BaseSolver
from ..core.problem import PackingProblem
from ..core.solution import PackingSolution

class MathematicalSolver(BaseSolver):
    """Solver that finds perfect rectangular arrangements analytically."""
    
    def __init__(self):
        super().__init__("Mathematical")
    
    def solve(self, problem: PackingProblem) -> PackingSolution:
        """Find the best rectangular arrangement."""
        self._start_timing()
        
        arrangements = self._find_rectangular_arrangements(problem)
        
        if not arrangements:
            self._end_timing()
            return PackingSolution(
                tile_positions=[],
                container_w=problem.container_w,
                container_h=problem.container_h,
                solve_time=self.solve_time,
                solver_name=self.name
            )
        
        # Pick the arrangement with most tiles
        best_arrangement = max(arrangements, key=lambda x: x[4])  # x[4] is total_tiles
        rows, cols, start_x, start_y, total_tiles = best_arrangement
        
        # Generate tile positions
        positions = []
        for r in range(rows):
            for c in range(cols):
                x = start_x + c * problem.tile_w
                y = start_y + r * problem.tile_h
                positions.append((x, y, problem.tile_w, problem.tile_h, "original"))
        
        self._end_timing()
        
        return PackingSolution(
            tile_positions=positions,
            container_w=problem.container_w,
            container_h=problem.container_h,
            solve_time=self.solve_time,
            solver_name=self.name,
            metadata={'arrangement': 'rectangular', 'grid_size': f"{rows}x{cols}"}
        )
    
    def solve_all_optimal(self, problem: PackingProblem, max_solutions: int = 10) -> List[PackingSolution]:
        """Find all optimal rectangular arrangements."""
        self._start_timing()
        
        arrangements = self._find_rectangular_arrangements(problem)
        
        if not arrangements:
            self._end_timing()
            return []
        
        # Find maximum tiles
        max_tiles = max(arrangement[4] for arrangement in arrangements)
        optimal_arrangements = [arr for arr in arrangements if arr[4] == max_tiles]
        
        solutions = []
        for rows, cols, start_x, start_y, total_tiles in optimal_arrangements[:max_solutions]:
            positions = []
            for r in range(rows):
                for c in range(cols):
                    x = start_x + c * problem.tile_w
                    y = start_y + r * problem.tile_h
                    positions.append((x, y, problem.tile_w, problem.tile_h, "original"))
            
            solution = PackingSolution(
                tile_positions=positions,
                container_w=problem.container_w,
                container_h=problem.container_h,
                solve_time=0,  # Will be set after loop
                solver_name=self.name,
                metadata={'arrangement': 'rectangular', 'grid_size': f"{rows}x{cols}"}
            )
            solutions.append(solution)
        
        # Set solve time for all solutions
        self._end_timing()
        for solution in solutions:
            solution.solve_time = self.solve_time
            
        return solutions
    
    def _find_rectangular_arrangements(self, problem: PackingProblem) -> List[Tuple[int, int, int, int, int]]:
        """Find all possible rectangular arrangements."""
        arrangements = []
        max_tiles = problem.max_tiles or problem.theoretical_max_tiles
        
        # Try all possible rectangular grids
        for rows in range(1, max_tiles + 1):
            for cols in range(1, max_tiles // rows + 1):
                if rows * cols <= max_tiles:
                    total_w = cols * problem.tile_w
                    total_h = rows * problem.tile_h
                    
                    # Check if fits in container
                    if total_w <= problem.container_w and total_h <= problem.container_h:
                        # Calculate centering position
                        start_x = (problem.container_w - total_w) // 2
                        start_y = (problem.container_h - total_h) // 2
                        total_tiles = rows * cols
                        arrangements.append((rows, cols, start_x, start_y, total_tiles))
        
        # Sort by number of tiles (descending)
        arrangements.sort(key=lambda x: x[4], reverse=True)
        return arrangements
