"""
Abstract base class for all rectangle packing solvers.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import time

from ..core.problem import PackingProblem
from ..core.solution import PackingSolution

class BaseSolver(ABC):
    """Abstract base class for all rectangle packing solvers."""
    
    def __init__(self, name: str):
        self.name = name
        self.solve_time = 0.0
        
    @abstractmethod
    def solve(self, problem: PackingProblem) -> PackingSolution:
        """
        Solve a single packing problem and return the best solution found.
        
        Args:
            problem: The packing problem to solve
            
        Returns:
            The best solution found
        """
        pass
    
    def solve_all_optimal(self, problem: PackingProblem, max_solutions: int = 10) -> List[PackingSolution]:
        """
        Find all optimal solutions (or up to max_solutions).
        Default implementation just returns the single best solution.
        Override in subclasses that can find multiple solutions.
        
        Args:
            problem: The packing problem to solve
            max_solutions: Maximum number of solutions to return
            
        Returns:
            List of all optimal solutions found
        """
        solution = self.solve(problem)
        return [solution] if solution.num_tiles > 0 else []
    
    def _start_timing(self):
        """Start timing the solve operation."""
        self._start_time = time.time()
    
    def _end_timing(self):
        """End timing and return elapsed time."""
        self.solve_time = time.time() - self._start_time
        return self.solve_time
    
    def get_solver_info(self) -> dict:
        """Get information about this solver."""
        return {
            'name': self.name,
            'last_solve_time': self.solve_time,
            'supports_multiple_solutions': hasattr(self, 'solve_all_optimal')
        }
