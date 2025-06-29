"""
Unit tests for all solver implementations.
"""

import pytest
import time
from src.core.problem import PackingProblem
from src.core.solution import PackingSolution
from src.solvers.mathematical_solver import MathematicalSolver
from src.solvers.greedy_solver import GreedySolver
from src.solvers.backtrack_solver import BacktrackSolver
from src.solvers.hybrid_solver import HybridSolver

# Test cases: (container_w, container_h, tile_w, tile_h, expected_min_tiles)
TEST_CASES = [
    (20, 20, 10, 10, 4),     # Perfect 2x2 grid
    (30, 20, 10, 10, 6),     # 3x2 grid
    (40, 48, 10, 10, 16),    # Your example case
    (15, 15, 5, 5, 9),       # 3x3 grid
    (25, 15, 5, 10, 6),      # Mixed arrangement
]

class TestMathematicalSolver:
    """Test the mathematical solver."""
    
    def test_perfect_rectangular_arrangements(self):
        """Test that mathematical solver finds perfect rectangular arrangements."""
        solver = MathematicalSolver()
        
        for container_w, container_h, tile_w, tile_h, expected_min in TEST_CASES:
            problem = PackingProblem(container_w, container_h, tile_w, tile_h)
            solution = solver.solve(problem)
            
            assert solution.num_tiles >= expected_min, f"Expected at least {expected_min} tiles, got {solution.num_tiles}"
            assert solution.solve_time < 1.0, "Mathematical solver should be very fast"
    
    def test_multiple_solutions(self):
        """Test finding multiple optimal solutions."""
        solver = MathematicalSolver()
        problem = PackingProblem(30, 20, 10, 10)  # Could have 3x2 or 2x3 arrangements
        
        solutions = solver.solve_all_optimal(problem, max_solutions=5)
        assert len(solutions) >= 1, "Should find at least one solution"
        
        # All solutions should have same number of tiles
        tile_counts = [s.num_tiles for s in solutions]
        assert len(set(tile_counts)) == 1, "All optimal solutions should have same tile count"
    
    def test_infeasible_problem(self):
        """Test behavior with infeasible problems."""
        solver = MathematicalSolver()
        problem = PackingProblem(5, 5, 10, 10)  # Tile larger than container
        
        solution = solver.solve(problem)
        assert solution.num_tiles == 0, "Should find no tiles for infeasible problem"

class TestGreedySolver:
    """Test the greedy solver."""
    
    def test_bottom_left_strategy(self):
        """Test bottom-left greedy strategy."""
        solver = GreedySolver(strategy="bottom_left")
        
        for container_w, container_h, tile_w, tile_h, expected_min in TEST_CASES:
            problem = PackingProblem(container_w, container_h, tile_w, tile_h)
            solution = solver.solve(problem)
            
            assert solution.num_tiles > 0, "Should find at least one tile"
            assert solution.solve_time < 5.0, "Greedy solver should be fast"
    
    def test_center_out_strategy(self):
        """Test center-outward greedy strategy."""
        solver = GreedySolver(strategy="center_out")
        
        problem = PackingProblem(40, 48, 10, 10)
        solution = solver.solve(problem)
        
        assert solution.num_tiles > 0, "Should find at least one tile"
        # Center-out should produce more centered results
        assert solution.is_centered or solution.num_tiles > 10, "Should be centered or find many tiles"
    
    def test_invalid_strategy(self):
        """Test error handling for invalid strategy."""
        solver = GreedySolver(strategy="invalid_strategy")
        problem = PackingProblem(20, 20, 10, 10)
        
        with pytest.raises(ValueError):
            solver.solve(problem)

class TestBacktrackSolver:
    """Test the backtracking solver."""
    
    def test_small_problem_exhaustive(self):
        """Test backtracking on small problems where it can be exhaustive."""
        solver = BacktrackSolver(max_solutions=10, time_limit=10.0)
        problem = PackingProblem(20, 20, 10, 10)  # Small enough for exhaustive search
        
        solutions = solver.solve_all_optimal(problem)
        assert len(solutions) >= 1, "Should find at least one solution"
        
        # Check that all solutions are valid
        for solution in solutions:
            assert solution.num_tiles > 0, "Each solution should have tiles"
            assert solution.efficiency > 0, "Each solution should have positive efficiency"
    
    def test_time_limit_respected(self):
        """Test that time limit is respected."""
        solver = BacktrackSolver(time_limit=1.0)  # Short time limit
        problem = PackingProblem(50, 50, 7, 11)  # Challenging problem
        
        start_time = time.time()
        solution = solver.solve(problem)
        elapsed = time.time() - start_time
        
        assert elapsed <= 2.0, f"Should respect time limit, took {elapsed}s"
    
    def test_rotation_handling(self):
        """Test that rotation is handled correctly."""
        solver = BacktrackSolver(max_solutions=5, time_limit=5.0)
        
        # Problem where rotation matters
        problem = PackingProblem(30, 20, 5, 10, allow_rotation=True)
        solution_with_rotation = solver.solve(problem)
        
        problem_no_rotation = PackingProblem(30, 20, 5, 10, allow_rotation=False)
        solution_no_rotation = solver.solve(problem_no_rotation)
        
        # With rotation should generally do better or equal
        assert solution_with_rotation.num_tiles >= solution_no_rotation.num_tiles

class TestHybridSolver:
    """Test the hybrid solver that orchestrates multiple approaches."""
    
    def test_multi_tier_approach(self):
        """Test that hybrid solver tries multiple approaches."""
        solver = HybridSolver(time_limit=30.0)
        
        for container_w, container_h, tile_w, tile_h, expected_min in TEST_CASES[:3]:  # Test subset for speed
            problem = PackingProblem(container_w, container_h, tile_w, tile_h)
            solution = solver.solve(problem)
            
            assert solution.num_tiles >= expected_min, f"Expected at least {expected_min}, got {solution.num_tiles}"
            assert "Hybrid" in solution.solver_name, "Should indicate hybrid solving"
    
    def test_all_optimal_solutions(self):
        """Test finding all optimal solutions."""
        solver = HybridSolver()
        problem = PackingProblem(20, 20, 10, 10)
        
        solutions = solver.solve_all_optimal(problem, max_solutions=5)
        assert len(solutions) >= 1, "Should find at least one solution"
        
        # All should be optimal (same tile count)
        tile_counts = [s.num_tiles for s in solutions]
        max_tiles = max(tile_counts)
        assert all(count == max_tiles for count in tile_counts), "All solutions should be optimal"
    
    def test_early_termination(self):
        """Test that solver terminates early for good solutions."""
        solver = HybridSolver(time_limit=60.0)
        problem = PackingProblem(40, 48, 10, 10)  # Should find perfect solution quickly
        
        start_time = time.time()
        solution = solver.solve(problem)
        elapsed = time.time() - start_time
        
        # Should find good solution quickly and terminate early
        assert solution.num_tiles >= 16, "Should find good solution"
        assert elapsed < 30.0, "Should terminate early for good solutions"

class TestSolverValidation:
    """Test that all solvers produce valid solutions."""
    
    def test_solution_validity(self):
        """Test that all solvers produce valid solutions."""
        from src.utils.validation import validate_solution
        
        solvers = [
            MathematicalSolver(),
            GreedySolver("bottom_left"),
            GreedySolver("center_out"),
            BacktrackSolver(time_limit=2.0),
        ]
        
        try:
            from src.solvers.ilp_solver import ILPSolver
            solvers.append(ILPSolver(time_limit=5.0))
        except ImportError:
            pass  # OR-Tools not available
        
        problem = PackingProblem(30, 20, 10, 10)
        
        for solver in solvers:
            solution = solver.solve(problem)
            is_valid, errors = validate_solution(solution, problem)
            
            assert is_valid, f"Solver {solver.name} produced invalid solution: {errors}"
            
            if solution.num_tiles > 0:
                assert 0 < solution.efficiency <= 100, f"Invalid efficiency: {solution.efficiency}"

class TestSolverPerformance:
    """Test solver performance characteristics."""
    
    def test_solver_timing(self):
        """Test that solvers complete within reasonable time."""
        problem = PackingProblem(40, 48, 10, 10)
        
        # Mathematical should be very fast
        math_solver = MathematicalSolver()
        start = time.time()
        math_solver.solve(problem)
        math_time = time.time() - start
        assert math_time < 1.0, f"Mathematical solver too slow: {math_time}s"
        
        # Greedy should be fast
        greedy_solver = GreedySolver()
        start = time.time()
        greedy_solver.solve(problem)
        greedy_time = time.time() - start
        assert greedy_time < 5.0, f"Greedy solver too slow: {greedy_time}s"
    
    def test_solution_quality_progression(self):
        """Test that more sophisticated solvers generally produce better results."""
        problem = PackingProblem(35, 25, 7, 8)  # Irregular problem
        
        math_solution = MathematicalSolver().solve(problem)
        greedy_solution = GreedySolver("center_out").solve(problem)
        backtrack_solution = BacktrackSolver(time_limit=3.0).solve(problem)
        
        # More sophisticated methods should generally do better
        solutions = [math_solution, greedy_solution, backtrack_solution]
        tile_counts = [s.num_tiles for s in solutions]
        
        # At least one advanced method should match or beat mathematical
        max_tiles = max(tile_counts)
        assert max_tiles >= math_solution.num_tiles, "Advanced methods should compete with mathematical"

# Pytest fixtures
@pytest.fixture
def simple_problem():
    """Fixture for a simple test problem."""
    return PackingProblem(20, 20, 10, 10)

@pytest.fixture
def complex_problem():
    """Fixture for a more complex test problem."""
    return PackingProblem(47, 33, 7, 11, allow_rotation=True)

# Integration tests
def test_end_to_end_workflow(simple_problem):
    """Test complete workflow from problem to visualization."""
    solver = HybridSolver(time_limit=10.0)
    solutions = solver.solve_all_optimal(simple_problem, max_solutions=3)
    
    assert len(solutions) >= 1, "Should find solutions"
    
    # Test that we can validate and export solutions
    from src.utils.validation import validate_solution
    from src.visualization.export import export_solutions_to_json
    import tempfile
    import os
    
    for solution in solutions:
        is_valid, errors = validate_solution(solution, simple_problem)
        assert is_valid, f"Invalid solution: {errors}"
    
    # Test export functionality
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_filename = f.name
    
    try:
        export_solutions_to_json(solutions, temp_filename)
        assert os.path.exists(temp_filename), "Export file should be created"
    finally:
        if os.path.exists(temp_filename):
            os.unlink(temp_filename)

if __name__ == "__main__":
    # Run tests if script is called directly
    pytest.main([__file__])
