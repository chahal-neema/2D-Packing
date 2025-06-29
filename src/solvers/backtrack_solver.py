"""
Backtracking solver for exhaustive search of rectangle packing solutions.
"""

from typing import List, Set, Tuple, Optional
import time
from copy import deepcopy

from .base_solver import BaseSolver
from ..core.problem import PackingProblem
from ..core.solution import PackingSolution, TilePosition

class BacktrackSolver(BaseSolver):
    """Exhaustive backtracking solver for finding all optimal solutions."""
    
    def __init__(self, max_solutions: int = 50, time_limit: float = 30.0):
        super().__init__("Backtrack")
        self.max_solutions = max_solutions
        self.time_limit = time_limit
        
    def solve(self, problem: PackingProblem) -> PackingSolution:
        """Find the best solution using backtracking."""
        solutions = self.solve_all_optimal(problem, max_solutions=1)
        return solutions[0] if solutions else PackingSolution(
            tile_positions=[],
            container_w=problem.container_w,
            container_h=problem.container_h,
            solve_time=self.solve_time,
            solver_name=self.name
        )
    
    def solve_all_optimal(self, problem: PackingProblem, max_solutions: int = None) -> List[PackingSolution]:
        """Find all optimal solutions using backtracking."""
        self._start_timing()
        
        if max_solutions is None:
            max_solutions = self.max_solutions
            
        # Initialize grid and search state
        grid = [[0 for _ in range(problem.container_w)] for _ in range(problem.container_h)]
        solutions_list = []
        max_tiles = problem.max_tiles or problem.theoretical_max_tiles
        
        # Start recursive search
        self._backtrack_solve(
            grid, max_tiles, 1, solutions_list, problem, max_solutions
        )
        
        self._end_timing()
        
        if not solutions_list:
            return []
        
        # Find maximum tiles achieved
        max_tiles_found = max(len(sol) for sol in solutions_list)
        optimal_solutions = [sol for sol in solutions_list if len(sol) == max_tiles_found]
        
        # Convert to PackingSolution objects
        result_solutions = []
        for positions in optimal_solutions[:max_solutions]:
            solution = PackingSolution(
                tile_positions=positions,
                container_w=problem.container_w,
                container_h=problem.container_h,
                solve_time=self.solve_time,
                solver_name=self.name,
                metadata={'method': 'backtrack', 'total_found': len(optimal_solutions)}
            )
            result_solutions.append(solution)
        
        return result_solutions
    
    def _backtrack_solve(self, grid: List[List[int]], tiles_left: int, tile_id: int,
                        solutions: List[List[TilePosition]], problem: PackingProblem,
                        max_solutions: int):
        """Recursive backtracking function."""
        # Time limit check
        if time.time() - self._start_time > self.time_limit:
            return
            
        # Stop if we've found enough solutions
        if len(solutions) >= max_solutions:
            return
        
        # Find first empty cell
        first_empty = self._find_first_empty(grid)
        
        if first_empty is None:
            # No more empty space - record solution
            solution = self._extract_solution(grid, problem)
            solutions.append(solution)
            return
        
        if tiles_left == 0:
            # No more tiles to place - record solution
            solution = self._extract_solution(grid, problem)
            solutions.append(solution)
            return
        
        row, col = first_empty
        
        # Try placing tile with original orientation
        if self._can_place(grid, row, col, problem.tile_h, problem.tile_w):
            self._place_tile(grid, row, col, problem.tile_h, problem.tile_w, tile_id)
            self._backtrack_solve(grid, tiles_left - 1, tile_id + 1, solutions, problem, max_solutions)
            self._remove_tile(grid, row, col, problem.tile_h, problem.tile_w)
        
        # Try placing tile with rotated orientation (if rotation allowed and different)
        if (problem.allow_rotation and problem.tile_w != problem.tile_h and 
            self._can_place(grid, row, col, problem.tile_w, problem.tile_h)):
            self._place_tile(grid, row, col, problem.tile_w, problem.tile_h, tile_id)
            self._backtrack_solve(grid, tiles_left - 1, tile_id + 1, solutions, problem, max_solutions)
            self._remove_tile(grid, row, col, problem.tile_w, problem.tile_h)
    
    def _find_first_empty(self, grid: List[List[int]]) -> Optional[Tuple[int, int]]:
        """Find first empty cell (top-left scan)."""
        for row in range(len(grid)):
            for col in range(len(grid[0])):
                if grid[row][col] == 0:
                    return (row, col)
        return None
    
    def _can_place(self, grid: List[List[int]], r: int, c: int, h: int, w: int) -> bool:
        """Check if a tile can be placed at position (r,c)."""
        # Check bounds
        if r + h > len(grid) or c + w > len(grid[0]):
            return False
        
        # Check for overlaps
        for i in range(r, r + h):
            for j in range(c, c + w):
                if grid[i][j] != 0:
                    return False
        return True
    
    def _place_tile(self, grid: List[List[int]], r: int, c: int, h: int, w: int, tile_id: int):
        """Place a tile on the grid."""
        for i in range(r, r + h):
            for j in range(c, c + w):
                grid[i][j] = tile_id
    
    def _remove_tile(self, grid: List[List[int]], r: int, c: int, h: int, w: int):
        """Remove a tile from the grid."""
        for i in range(r, r + h):
            for j in range(c, c + w):
                grid[i][j] = 0
    
    def _extract_solution(self, grid: List[List[int]], problem: PackingProblem) -> List[TilePosition]:
        """Extract tile positions from grid."""
        tiles = {}
        height, width = len(grid), len(grid[0])
        
        for r in range(height):
            for c in range(width):
                tile_id = grid[r][c]
                if tile_id != 0 and tile_id not in tiles:
                    # Find extent of this tile
                    w, h = 1, 1
                    # Find width
                    while c + w < width and grid[r][c + w] == tile_id:
                        w += 1
                    # Find height  
                    while r + h < height and grid[r + h][c] == tile_id:
                        h += 1
                    
                    # Determine orientation
                    orientation = "rotated" if (w == problem.tile_h and h == problem.tile_w) else "original"
                    tiles[tile_id] = (c, r, w, h, orientation)  # (x, y, width, height, orientation)
        
        # Return sorted by tile_id
        return [tiles[tid] for tid in sorted(tiles.keys())]
