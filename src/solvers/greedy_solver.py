"""
Fast greedy heuristic solvers for rectangle packing.
"""

from typing import List, Set, Tuple, Optional
from .base_solver import BaseSolver
from ..core.problem import PackingProblem
from ..core.solution import PackingSolution

class GreedySolver(BaseSolver):
    """Fast greedy heuristic solver."""
    
    def __init__(self, strategy: str = "bottom_left"):
        super().__init__("Greedy")
        self.strategy = strategy
        
    def solve(self, problem: PackingProblem) -> PackingSolution:
        """Solve using greedy heuristic."""
        self._start_timing()
        
        if self.strategy == "bottom_left":
            positions = self._solve_bottom_left(problem)
        elif self.strategy == "center_out":
            positions = self._solve_center_out(problem)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")
        
        self._end_timing()
        
        return PackingSolution(
            tile_positions=positions,
            container_w=problem.container_w,
            container_h=problem.container_h,
            solve_time=self.solve_time,
            solver_name=f"{self.name}_{self.strategy}",
            metadata={'strategy': self.strategy}
        )
    
    def _solve_bottom_left(self, problem: PackingProblem) -> List[Tuple[int, int, int, int, str]]:
        """Greedy bottom-left fill algorithm."""
        placed_tiles = []
        occupied = set()
        max_tiles = problem.max_tiles or problem.theoretical_max_tiles
        
        # Try to place tiles greedily
        for _ in range(max_tiles):
            best_position = self._find_best_bottom_left_position(
                problem, occupied
            )
            
            if best_position is None:
                break
                
            x, y, w, h = best_position
            
            # Mark cells as occupied
            for fill_x in range(x, x + w):
                for fill_y in range(y, y + h):
                    occupied.add((fill_x, fill_y))
            
            placed_tiles.append((x, y, w, h, "original"))
        
        return placed_tiles
    
    def _solve_center_out(self, problem: PackingProblem) -> List[Tuple[int, int, int, int, str]]:
        """Greedy center-outward placement algorithm."""
        placed_tiles = []
        occupied = set()
        max_tiles = problem.max_tiles or problem.theoretical_max_tiles
        
        # Generate positions sorted by distance from center
        center_x = problem.container_w // 2
        center_y = problem.container_h // 2
        
        positions = []
        for x in range(problem.container_w):
            for y in range(problem.container_h):
                if (x + problem.tile_w <= problem.container_w and 
                    y + problem.tile_h <= problem.container_h):
                    tile_center_x = x + problem.tile_w // 2
                    tile_center_y = y + problem.tile_h // 2
                    distance = abs(tile_center_x - center_x) + abs(tile_center_y - center_y)
                    positions.append((distance, x, y))
        
        positions.sort()  # Sort by distance from center
        
        for distance, x, y in positions:
            if len(placed_tiles) >= max_tiles:
                break
                
            # Check if position is free
            if self._can_place_at(x, y, problem.tile_w, problem.tile_h, occupied):
                # Place tile
                for fill_x in range(x, x + problem.tile_w):
                    for fill_y in range(y, y + problem.tile_h):
                        occupied.add((fill_x, fill_y))
                placed_tiles.append((x, y, problem.tile_w, problem.tile_h, "original"))
        
        return placed_tiles
    
    def _find_best_bottom_left_position(self, problem: PackingProblem, 
                                       occupied: Set[Tuple[int, int]]) -> Optional[Tuple[int, int, int, int]]:
        """Find the best bottom-left position to place a tile."""
        # Try positions from bottom-left
        for y in range(problem.container_h - problem.tile_h + 1):
            for x in range(problem.container_w - problem.tile_w + 1):
                if self._can_place_at(x, y, problem.tile_w, problem.tile_h, occupied):
                    return (x, y, problem.tile_w, problem.tile_h)
        return None
    
    def _can_place_at(self, x: int, y: int, w: int, h: int, 
                     occupied: Set[Tuple[int, int]]) -> bool:
        """Check if a tile can be placed at given position."""
        for check_x in range(x, x + w):
            for check_y in range(y, y + h):
                if (check_x, check_y) in occupied:
                    return False
        return True
