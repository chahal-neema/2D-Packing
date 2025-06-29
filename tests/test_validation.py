"""
Tests for solution validation and feasibility checking.
"""

import pytest
from src.utils.validation import (
    validate_solution, check_overlaps, check_feasibility,
    get_solution_quality_metrics, compare_solutions, rectangles_overlap
)
from src.core.solution import PackingSolution
from src.core.problem import PackingProblem

class TestSolutionValidation:
    """Test solution validation functions."""
    
    def test_valid_solution(self):
        """Test validation of a valid solution."""
        problem = PackingProblem(20, 20, 5, 5)
        positions = [(0, 0, 5, 5, "original"), (5, 0, 5, 5, "original")]
        solution = PackingSolution(positions, 20, 20)
        
        is_valid, errors = validate_solution(solution, problem)
        assert is_valid, f"Valid solution should pass validation: {errors}"
        assert len(errors) == 0, "Valid solution should have no errors"
    
    def test_out_of_bounds_solution(self):
        """Test validation of solution with tiles outside container."""
        problem = PackingProblem(10, 10, 5, 5)
        # Tile extends beyond container
        positions = [(8, 8, 5, 5, "original")]
        solution = PackingSolution(positions, 10, 10)
        
        is_valid, errors = validate_solution(solution, problem)
        assert not is_valid, "Out of bounds solution should fail validation"
        assert len(errors) > 0, "Should report errors for out of bounds tiles"
        assert any("extends beyond" in error for error in errors), "Should mention boundary violation"
    
    def test_negative_coordinates(self):
        """Test validation of solution with negative coordinates."""
        problem = PackingProblem(20, 20, 5, 5)
        positions = [(-1, 0, 5, 5, "original")]
        solution = PackingSolution(positions, 20, 20)
        
        is_valid, errors = validate_solution(solution, problem)
        assert not is_valid, "Negative coordinates should fail validation"
        assert any("negative coordinates" in error for error in errors), "Should report negative coordinates"
    
    def test_overlapping_tiles(self):
        """Test validation of solution with overlapping tiles."""
        problem = PackingProblem(20, 20, 5, 5)
        # Two tiles that overlap
        positions = [(0, 0, 5, 5, "original"), (2, 2, 5, 5, "original")]
        solution = PackingSolution(positions, 20, 20)
        
        is_valid, errors = validate_solution(solution, problem)
        assert not is_valid, "Overlapping tiles should fail validation"
        assert any("overlap" in error for error in errors), "Should report overlaps"
    
    def test_wrong_tile_dimensions(self):
        """Test validation of solution with wrong tile dimensions."""
        problem = PackingProblem(20, 20, 5, 5)
        # Tile with wrong dimensions
        positions = [(0, 0, 3, 7, "original")]
        solution = PackingSolution(positions, 20, 20)
        
        is_valid, errors = validate_solution(solution, problem)
        assert not is_valid, "Wrong dimensions should fail validation"
        assert any("incorrect dimensions" in error for error in errors), "Should report dimension errors"
    
    def test_invalid_orientation(self):
        """Test validation of solution with invalid orientation."""
        problem = PackingProblem(20, 20, 5, 5)
        positions = [(0, 0, 5, 5, "invalid_orientation")]
        solution = PackingSolution(positions, 20, 20)
        
        is_valid, errors = validate_solution(solution, problem)
        assert not is_valid, "Invalid orientation should fail validation"
        assert any("invalid orientation" in error for error in errors), "Should report orientation errors"
    
    def test_rotation_not_allowed(self):
        """Test validation when rotation is not allowed but tile is rotated."""
        problem = PackingProblem(20, 20, 5, 3, allow_rotation=False)
        positions = [(0, 0, 3, 5, "rotated")]  # Rotated when not allowed
        solution = PackingSolution(positions, 20, 20)
        
        is_valid, errors = validate_solution(solution, problem)
        assert not is_valid, "Rotated tile should fail when rotation not allowed"
        assert any("rotation not allowed" in error for error in errors), "Should report rotation error"
    
    def test_container_dimension_mismatch(self):
        """Test validation with container dimension mismatch."""
        problem = PackingProblem(20, 20, 5, 5)
        positions = [(0, 0, 5, 5, "original")]
        solution = PackingSolution(positions, 30, 30)  # Wrong container size
        
        is_valid, errors = validate_solution(solution, problem)
        assert not is_valid, "Container mismatch should fail validation"
        assert any("dimensions mismatch" in error for error in errors), "Should report container mismatch"
    
    def test_too_many_tiles(self):
        """Test validation when solution has too many tiles."""
        problem = PackingProblem(20, 20, 5, 5, max_tiles=2)
        positions = [(0, 0, 5, 5, "original"), (5, 0, 5, 5, "original"), (10, 0, 5, 5, "original")]
        solution = PackingSolution(positions, 20, 20)
        
        is_valid, errors = validate_solution(solution, problem)
        assert not is_valid, "Too many tiles should fail validation"
        assert any("Too many tiles" in error for error in errors), "Should report tile count error"

class TestOverlapDetection:
    """Test overlap detection functions."""
    
    def test_rectangles_overlap_true(self):
        """Test overlap detection for overlapping rectangles."""
        # Rectangle 1: (0,0) to (5,5)
        # Rectangle 2: (3,3) to (8,8) - overlaps
        assert rectangles_overlap(0, 0, 5, 5, 3, 3, 5, 5), "Should detect overlap"
    
    def test_rectangles_overlap_false(self):
        """Test overlap detection for non-overlapping rectangles."""
        # Rectangle 1: (0,0) to (5,5)
        # Rectangle 2: (6,0) to (11,5) - no overlap
        assert not rectangles_overlap(0, 0, 5, 5, 6, 0, 5, 5), "Should not detect overlap"
    
    def test_rectangles_touching_not_overlap(self):
        """Test that touching rectangles are not considered overlapping."""
        # Rectangle 1: (0,0) to (5,5)
        # Rectangle 2: (5,0) to (10,5) - touching but not overlapping
        assert not rectangles_overlap(0, 0, 5, 5, 5, 0, 5, 5), "Touching rectangles should not overlap"
    
    def test_check_overlaps_none(self):
        """Test overlap checking with no overlaps."""
        positions = [(0, 0, 5, 5, "original"), (5, 0, 5, 5, "original")]
        errors = check_overlaps(positions)
        assert len(errors) == 0, "Should find no overlaps"
    
    def test_check_overlaps_found(self):
        """Test overlap checking with overlaps present."""
        positions = [(0, 0, 5, 5, "original"), (2, 2, 5, 5, "original")]
        errors = check_overlaps(positions)
        assert len(errors) > 0, "Should find overlaps"
        assert "overlap" in errors[0], "Error message should mention overlap"

class TestFeasibilityChecking:
    """Test problem feasibility checking."""
    
    def test_feasible_problem(self):
        """Test feasibility checking for feasible problem."""
        problem = PackingProblem(20, 20, 5, 5)
        is_feasible, warnings = check_feasibility(problem)
        
        assert is_feasible, "Basic problem should be feasible"
    
    def test_infeasible_problem(self):
        """Test feasibility checking for infeasible problem."""
        problem = PackingProblem(5, 5, 10, 10)  # Tile larger than container
        is_feasible, warnings = check_feasibility(problem)
        
        assert not is_feasible, "Oversized tile should make problem infeasible"
    
    def test_rotation_makes_feasible(self):
        """Test that rotation can make problem feasible."""
        # Tile doesn't fit in original orientation but fits when rotated
        problem = PackingProblem(10, 5, 8, 3, allow_rotation=True)
        is_feasible, warnings = check_feasibility(problem)
        
        assert is_feasible, "Rotation should make problem feasible"
    
    def test_warnings_for_low_efficiency(self):
        """Test warnings for low efficiency scenarios."""
        problem = PackingProblem(10, 10, 7, 7)  # Low packing density
        is_feasible, warnings = check_feasibility(problem)
        
        assert is_feasible, "Should still be feasible"
        assert len(warnings) > 0, "Should generate warnings for low efficiency"
    
    def test_warnings_for_excessive_max_tiles(self):
        """Test warnings when max_tiles exceeds theoretical maximum."""
        problem = PackingProblem(10, 10, 5, 5, max_tiles=100)  # Way too many
        is_feasible, warnings = check_feasibility(problem)
        
        assert is_feasible, "Should still be feasible"
        assert any("exceeds theoretical maximum" in warning for warning in warnings), "Should warn about excessive max_tiles"

class TestQualityMetrics:
    """Test solution quality metrics calculation."""
    
    def test_basic_metrics(self):
        """Test basic quality metrics calculation."""
        problem = PackingProblem(20, 20, 5, 5)
        positions = [(0, 0, 5, 5, "original"), (5, 0, 5, 5, "original")]
        solution = PackingSolution(positions, 20, 20, solve_time=1.5)
        
        metrics = get_solution_quality_metrics(solution, problem)
        
        assert metrics['num_tiles'] == 2, "Should count tiles correctly"
        assert metrics['solve_time'] == 1.5, "Should report solve time"
        assert 0 < metrics['efficiency'] <= 100, "Efficiency should be in valid range"
        assert 0 < metrics['area_utilization'] <= 1, "Area utilization should be in valid range"
    
    def test_metrics_for_empty_solution(self):
        """Test metrics for empty solution."""
        problem = PackingProblem(20, 20, 5, 5)
        solution = PackingSolution([], 20, 20)
        
        metrics = get_solution_quality_metrics(solution, problem)
        
        assert metrics['num_tiles'] == 0, "Should have zero tiles"
        assert metrics['efficiency'] == 0, "Efficiency should be zero"
        assert metrics['area_utilization'] == 0, "Area utilization should be zero"
        assert metrics['is_centered'] == True, "Empty solution should be considered centered"
    
    def test_centering_metrics(self):
        """Test centering quality metrics."""
        problem = PackingProblem(20, 20, 5, 5)
        
        # Centered solution
        centered_positions = [(7, 7, 5, 5, "original")]
        centered_solution = PackingSolution(centered_positions, 20, 20)
        centered_metrics = get_solution_quality_metrics(centered_solution, problem)
        
        # Off-center solution
        offcenter_positions = [(0, 0, 5, 5, "original")]
        offcenter_solution = PackingSolution(offcenter_positions, 20, 20)
        offcenter_metrics = get_solution_quality_metrics(offcenter_solution, problem)
        
        assert centered_metrics['center_deviation'] < offcenter_metrics['center_deviation'], \
            "Centered solution should have lower center deviation"
    
    def test_optimality_ratio(self):
        """Test optimality ratio calculation."""
        problem = PackingProblem(20, 20, 10, 10)  # Can fit exactly 4 tiles
        positions = [(0, 0, 10, 10, "original"), (10, 0, 10, 10, "original")]  # 2 tiles
        solution = PackingSolution(positions, 20, 20)
        
        metrics = get_solution_quality_metrics(solution, problem)
        
        expected_ratio = 2 / 4  # 2 tiles out of theoretical max 4
        assert abs(metrics['optimality_ratio'] - expected_ratio) < 0.01, \
            f"Optimality ratio should be {expected_ratio}, got {metrics['optimality_ratio']}"

class TestSolutionComparison:
    """Test solution comparison functions."""
    
    def test_compare_multiple_solutions(self):
        """Test comparison of multiple solutions."""
        problem = PackingProblem(20, 20, 5, 5)
        
        solutions = [
            PackingSolution([(0, 0, 5, 5, "original")], 20, 20, solve_time=0.1),
            PackingSolution([(0, 0, 5, 5, "original"), (5, 0, 5, 5, "original")], 20, 20, solve_time=0.2),
            PackingSolution([(0, 0, 5, 5, "original"), (5, 0, 5, 5, "original"), (10, 0, 5, 5, "original")], 20, 20, solve_time=0.5)
        ]
        
        analysis = compare_solutions(solutions, problem)
        
        assert analysis['num_solutions'] == 3, "Should count solutions correctly"
        assert analysis['tile_count_range'] == (1, 3), "Should find correct tile count range"
        assert analysis['best_solution']['tiles'] == 3, "Should identify best solution"
        assert 0 < analysis['solution_diversity'] <= 1, "Diversity should be in valid range"
    
    def test_compare_empty_solution_list(self):
        """Test comparison with empty solution list."""
        problem = PackingProblem(20, 20, 5, 5)
        analysis = compare_solutions([], problem)
        
        assert 'error' in analysis, "Should return error for empty list"
    
    def test_compare_identical_solutions(self):
        """Test comparison of identical solutions."""
        problem = PackingProblem(20, 20, 5, 5)
        positions = [(0, 0, 5, 5, "original")]
        
        solutions = [
            PackingSolution(positions, 20, 20),
            PackingSolution(positions, 20, 20),
            PackingSolution(positions, 20, 20)
        ]
        
        analysis = compare_solutions(solutions, problem)
        
        assert analysis['tile_count_range'] == (1, 1), "All solutions should have same tile count"
        assert analysis['solution_diversity'] < 1, "Identical solutions should have low diversity"

class TestValidationEdgeCases:
    """Test edge cases in validation."""
    
    def test_zero_dimension_tiles(self):
        """Test validation with zero-dimension tiles."""
        problem = PackingProblem(20, 20, 5, 5)
        positions = [(0, 0, 0, 5, "original")]  # Zero width
        solution = PackingSolution(positions, 20, 20)
        
        is_valid, errors = validate_solution(solution, problem)
        assert not is_valid, "Zero dimension should fail validation"
        assert any("invalid dimensions" in error for error in errors), "Should report invalid dimensions"
    
    def test_very_large_tiles(self):
        """Test validation with very large tiles."""
        problem = PackingProblem(20, 20, 5, 5)
        positions = [(0, 0, 1000, 1000, "original")]
        solution = PackingSolution(positions, 20, 20)
        
        is_valid, errors = validate_solution(solution, problem)
        assert not is_valid, "Oversized tile should fail validation"
    
    def test_many_small_overlaps(self):
        """Test overlap detection with many small overlaps."""
        positions = []
        for i in range(10):
            positions.append((i, 0, 2, 2, "original"))  # Each overlaps with next
        
        errors = check_overlaps(positions)
        assert len(errors) > 0, "Should detect multiple overlaps"
        # Should detect 9 overlaps (each adjacent pair)
        assert len(errors) == 9, f"Should detect 9 overlaps, found {len(errors)}"

if __name__ == "__main__":
    pytest.main([__file__])
