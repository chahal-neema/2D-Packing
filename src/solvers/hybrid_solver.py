"""
Hybrid solver that orchestrates multiple solving strategies.
"""

from typing import List, Optional
import time

from .base_solver import BaseSolver
from .mathematical_solver import MathematicalSolver
from .greedy_solver import GreedySolver
from .backtrack_solver import BacktrackSolver
from .ilp_solver import ILPSolver, ORTOOLS_AVAILABLE
from ..core.problem import PackingProblem
from ..core.solution import PackingSolution
from ..utils.symmetry import deduplicate_solutions
from ..core.geometry import center_solution

class HybridSolver(BaseSolver):
    """Multi-tier solver that tries different approaches in order of speed."""
    
    def __init__(self, time_limit: float = 60.0):
        super().__init__("Hybrid")
        self.time_limit = time_limit
        self.solvers = []
        self._initialize_solvers()
    
    def _initialize_solvers(self):
        """Initialize available solvers in order of preference."""
        # Tier 1: Mathematical (instant)
        self.mathematical_solver = MathematicalSolver()
        
        # Tier 2: Greedy (fast)
        self.greedy_solver = GreedySolver(strategy="center_out")
        
        # Tier 3: Backtracking (moderate)
        self.backtrack_solver = BacktrackSolver(max_solutions=10, time_limit=10.0)
        
        # Tier 4: ILP (slow but optimal)
        if ORTOOLS_AVAILABLE:
            self.ilp_solver = ILPSolver(time_limit=30.0)
        else:
            self.ilp_solver = None
    
    def solve(self, problem: PackingProblem) -> PackingSolution:
        """Find the best solution using multi-tier approach."""
        self._start_timing()
        
        print(f"🔧 HYBRID SOLVER: {problem.tile_w}×{problem.tile_h} tiles in {problem.container_w}×{problem.container_h}")
        print(f"📊 Theoretical maximum: {problem.theoretical_max_tiles} tiles")
        
        best_solution = PackingSolution(
            tile_positions=[],
            container_w=problem.container_w,
            container_h=problem.container_h,
            solve_time=0,
            solver_name=self.name
        )
        
        # Tier 1: Mathematical solver
        print("🎯 TIER 1: Trying mathematical solver...")
        math_solution = self.mathematical_solver.solve(problem)
        if math_solution.num_tiles > 0:
            efficiency = math_solution.efficiency
            print(f"   ✅ Mathematical: {math_solution.num_tiles} tiles ({efficiency:.1f}% efficiency)")
            best_solution = math_solution
            
            # If we got optimal solution or very high efficiency, we're done
            if best_solution.num_tiles >= problem.theoretical_max_tiles or efficiency >= 95:
                print(f"   🏆 Optimal/Excellent solution found! Stopping early.")
                self._end_timing()
                best_solution.solve_time = self.solve_time
                best_solution.solver_name = f"Hybrid({best_solution.solver_name})"
                return best_solution
        
        # Tier 2: Greedy solver
        print("🎯 TIER 2: Trying greedy solver...")
        greedy_solution = self.greedy_solver.solve(problem)
        if greedy_solution.num_tiles > best_solution.num_tiles:
            print(f"   ✅ Greedy improved: {greedy_solution.num_tiles} tiles ({greedy_solution.efficiency:.1f}% efficiency)")
            best_solution = greedy_solution
        
        # Check if we achieved optimal solution
        if best_solution.num_tiles >= problem.theoretical_max_tiles:
            print(f"   🏆 Optimal solution found! Stopping early.")
            self._end_timing()
            best_solution.solve_time = self.solve_time
            best_solution.solver_name = f"Hybrid({best_solution.solver_name})"
            return best_solution
        
        # Check remaining time
        elapsed = time.time() - self._start_time
        if elapsed > self.time_limit * 0.7:
            print(f"   ⏰ Time limit approaching, returning best solution so far.")
            self._end_timing()
            best_solution.solve_time = self.solve_time
            return best_solution
        
        # Tier 3: Backtracking solver
        print("🎯 TIER 3: Trying backtracking solver...")
        remaining_time = max(5.0, self.time_limit - elapsed - 10)  # Reserve 10s for ILP
        self.backtrack_solver.time_limit = remaining_time
        
        backtrack_solution = self.backtrack_solver.solve(problem)
        if backtrack_solution.num_tiles > best_solution.num_tiles:
            print(f"   ✅ Backtracking improved: {backtrack_solution.num_tiles} tiles ({backtrack_solution.efficiency:.1f}% efficiency)")
            best_solution = backtrack_solution
            
            # Check if we achieved optimal solution after backtracking
            if best_solution.num_tiles >= problem.theoretical_max_tiles:
                print(f"   🏆 Optimal solution found! Stopping early.")
                self._end_timing()
                best_solution.solve_time = self.solve_time
                best_solution.solver_name = f"Hybrid({best_solution.solver_name})"
                return best_solution
        
        # Check time again
        elapsed = time.time() - self._start_time
        if elapsed > self.time_limit * 0.8 or not self.ilp_solver:
            print(f"   ⏰ Finishing with current best solution.")
            self._end_timing()
            best_solution.solve_time = self.solve_time
            return best_solution
        
        # Tier 4: ILP solver (if available and time permits)
        print("🎯 TIER 4: Trying ILP solver...")
        remaining_time = max(5.0, self.time_limit - elapsed)
        self.ilp_solver.time_limit = remaining_time
        
        ilp_solution = self.ilp_solver.solve(problem)
        if ilp_solution.num_tiles > best_solution.num_tiles:
            print(f"   ✅ ILP improved: {ilp_solution.num_tiles} tiles ({ilp_solution.efficiency:.1f}% efficiency)")
            best_solution = ilp_solution
        
        self._end_timing()
        best_solution.solve_time = self.solve_time
        best_solution.solver_name = f"Hybrid({best_solution.solver_name})"
        
        print(f"🏁 FINAL RESULT: {best_solution.num_tiles} tiles ({best_solution.efficiency:.1f}% efficiency) in {self.solve_time:.2f}s")
        return best_solution
    
    def solve_all_optimal(self, problem: PackingProblem, max_solutions: int = 10) -> List[PackingSolution]:
        """Find all optimal solutions using the best available method."""
        self._start_timing()
        
        print(f"🔧 FINDING ALL OPTIMAL SOLUTIONS")
        
        # First, find the maximum number of tiles possible
        best_single = self.solve(problem)
        if best_single.num_tiles == 0:
            return []
        
        target_tiles = best_single.num_tiles
        print(f"🎯 Target: {target_tiles} tiles")
        
        # Use the most appropriate solver for exhaustive search
        if target_tiles <= 10:  # Small problems - use backtracking
            print("   Using backtracking for exhaustive search...")
            solutions = self.backtrack_solver.solve_all_optimal(problem, max_solutions)
        else:  # Larger problems - try mathematical first, then backtracking if needed
            print("   Using mathematical solver for multiple arrangements...")
            solutions = self.mathematical_solver.solve_all_optimal(problem, max_solutions)
            
            # If mathematical didn't find the optimum, use backtracking instead
            if not solutions or solutions[0].num_tiles < target_tiles:
                print("   Mathematical solver suboptimal, switching to backtracking...")
                solutions = self.backtrack_solver.solve_all_optimal(problem, max_solutions)
                
                # If backtracking still didn't find optimum, fall back to single best
                if not solutions or solutions[0].num_tiles < target_tiles:
                    solutions = [best_single]
        
        # Deduplicate solutions
        if len(solutions) > 1:
            print(f"   Deduplicating {len(solutions)} solutions...")
            solutions = deduplicate_solutions(solutions, problem)
            print(f"   {len(solutions)} unique solutions after deduplication")
        
        # Center all solutions
        for solution in solutions:
            if problem.require_centering and not solution.is_centered:
                solution.tile_positions = center_solution(
                    solution.tile_positions, 
                    problem.container_w, 
                    problem.container_h
                )
        
        self._end_timing()
        for solution in solutions:
            solution.solve_time = self.solve_time
            solution.solver_name = f"Hybrid({solution.solver_name})"
        
        print(f"🏁 FOUND {len(solutions)} OPTIMAL SOLUTIONS in {self.solve_time:.2f}s")
        return solutions
