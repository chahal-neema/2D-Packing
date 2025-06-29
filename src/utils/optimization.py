"""
Performance optimization utilities for rectangle packing algorithms.
"""

import time
import functools
from typing import List, Callable, Any, Dict
from ..core.solution import PackingSolution, TilePosition
from ..core.problem import PackingProblem

def timeit(func: Callable) -> Callable:
    """Decorator to time function execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"⏱️  {func.__name__} took {end_time - start_time:.3f}s")
        return result
    return wrapper

def profile_solver(solver_func: Callable, problem: PackingProblem, runs: int = 5) -> Dict[str, Any]:
    """Profile a solver function over multiple runs."""
    times = []
    results = []
    
    for i in range(runs):
        start_time = time.time()
        result = solver_func(problem)
        end_time = time.time()
        
        times.append(end_time - start_time)
        results.append(result)
    
    # Calculate statistics
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    # Check result consistency
    tile_counts = [r.num_tiles if hasattr(r, 'num_tiles') else len(r) for r in results]
    consistent_results = len(set(tile_counts)) == 1
    
    return {
        'avg_time': avg_time,
        'min_time': min_time,
        'max_time': max_time,
        'total_time': sum(times),
        'runs': runs,
        'consistent_results': consistent_results,
        'tile_counts': tile_counts,
        'best_result': max(results, key=lambda r: r.num_tiles if hasattr(r, 'num_tiles') else len(r))
    }

class EarlyTermination:
    """Helper class for implementing early termination in algorithms."""
    
    def __init__(self, time_limit: float = None, target_tiles: int = None, 
                 target_efficiency: float = None):
        self.time_limit = time_limit
        self.target_tiles = target_tiles
        self.target_efficiency = target_efficiency
        self.start_time = time.time()
    
    def should_terminate(self, current_solution: PackingSolution = None) -> bool:
        """Check if algorithm should terminate early."""
        # Time limit check
        if self.time_limit and (time.time() - self.start_time) > self.time_limit:
            return True
        
        # Target tiles check
        if (self.target_tiles and current_solution and 
            current_solution.num_tiles >= self.target_tiles):
            return True
        
        # Target efficiency check
        if (self.target_efficiency and current_solution and 
            current_solution.efficiency >= self.target_efficiency):
            return True
        
        return False
    
    def remaining_time(self) -> float:
        """Get remaining time until time limit."""
        if not self.time_limit:
            return float('inf')
        return max(0, self.time_limit - (time.time() - self.start_time))

def area_based_pruning(current_tiles: int, remaining_area: int, 
                      tile_area: int, current_best: int) -> bool:
    """
    Check if current branch can be pruned based on area constraints.
    
    Returns True if this branch cannot possibly beat the current best.
    """
    max_additional_tiles = remaining_area // tile_area
    upper_bound = current_tiles + max_additional_tiles
    return upper_bound <= current_best

def calculate_lower_bound(container_area: int, tile_area: int, 
                         placed_tiles: int = 0, used_area: int = 0) -> int:
    """Calculate lower bound for number of tiles that can be placed."""
    remaining_area = container_area - used_area
    return placed_tiles + (remaining_area // tile_area)

def calculate_upper_bound(problem: PackingProblem, placed_tiles: List[TilePosition] = None) -> int:
    """
    Calculate upper bound for number of tiles using more sophisticated methods.
    """
    if placed_tiles is None:
        # Simple area-based bound
        return problem.theoretical_max_tiles
    
    # Calculate remaining area after placed tiles
    used_area = sum(w * h for _, _, w, h, _ in placed_tiles)
    remaining_area = problem.container_area - used_area
    
    # Area-based bound
    area_bound = len(placed_tiles) + (remaining_area // problem.tile_area)
    
    # TODO: Add more sophisticated bounds based on remaining rectangle shapes
    
    return area_bound

class ProgressTracker:
    """Track and report progress of long-running algorithms."""
    
    def __init__(self, total_work: int = 100, report_interval: float = 5.0):
        self.total_work = total_work
        self.current_work = 0
        self.start_time = time.time()
        self.last_report = self.start_time
        self.report_interval = report_interval
    
    def update(self, work_done: int = 1, message: str = None):
        """Update progress and optionally print status."""
        self.current_work += work_done
        current_time = time.time()
        
        if current_time - self.last_report >= self.report_interval:
            self._print_progress(message)
            self.last_report = current_time
    
    def _print_progress(self, message: str = None):
        """Print current progress status."""
        elapsed = time.time() - self.start_time
        progress = min(100, (self.current_work / self.total_work) * 100)
        
        if progress > 0:
            eta = (elapsed / progress) * (100 - progress)
            print(f"📊 Progress: {progress:.1f}% ({self.current_work}/{self.total_work}) "
                  f"- Elapsed: {elapsed:.1f}s - ETA: {eta:.1f}s"
                  + (f" - {message}" if message else ""))
        else:
            print(f"📊 Progress: {progress:.1f}% - Elapsed: {elapsed:.1f}s"
                  + (f" - {message}" if message else ""))

def memory_efficient_search(search_function: Callable, *args, **kwargs) -> Any:
    """
    Wrapper for search functions to use memory more efficiently.
    Implements techniques like garbage collection hints.
    """
    import gc
    
    # Force garbage collection before starting
    gc.collect()
    
    try:
        result = search_function(*args, **kwargs)
        return result
    finally:
        # Clean up after search
        gc.collect()

def adaptive_time_allocation(solvers: List[Callable], total_time: float, 
                           problem: PackingProblem) -> Dict[str, float]:
    """
    Allocate time budget across different solvers based on problem characteristics.
    """
    allocations = {}
    
    # Base allocation percentages
    if problem.theoretical_max_tiles <= 5:
        # Small problems - favor exhaustive search
        allocations = {
            'mathematical': 0.1,
            'greedy': 0.1,
            'backtrack': 0.6,
            'ilp': 0.2
        }
    elif problem.theoretical_max_tiles <= 20:
        # Medium problems - balanced approach
        allocations = {
            'mathematical': 0.1,
            'greedy': 0.2,
            'backtrack': 0.4,
            'ilp': 0.3
        }
    else:
        # Large problems - favor heuristics
        allocations = {
            'mathematical': 0.1,
            'greedy': 0.3,
            'backtrack': 0.2,
            'ilp': 0.4
        }
    
    # Convert percentages to actual time
    time_allocations = {solver: total_time * pct for solver, pct in allocations.items()}
    
    return time_allocations

def optimize_search_order(problem: PackingProblem) -> List[str]:
    """
    Determine optimal order to try different solving approaches based on problem characteristics.
    """
    order = []
    
    # Always start with mathematical for rectangular arrangements
    order.append('mathematical')
    
    # For small problems, try exhaustive search early
    if problem.theoretical_max_tiles <= 10:
        order.extend(['backtrack', 'greedy', 'ilp'])
    else:
        order.extend(['greedy', 'ilp', 'backtrack'])
    
    return order
