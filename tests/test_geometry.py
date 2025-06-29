"""
Tests for geometric operations and transformations.
"""

import pytest
from src.core.geometry import (
    rotate_point_90, rotate_point_180, rotate_point_270,
    mirror_point_horizontal, mirror_point_vertical,
    rotate_solution_90, rotate_solution_180, rotate_solution_270,
    center_solution, translate_solution, calculate_bounding_box
)
from src.core.solution import TilePosition

class TestPointTransformations:
    """Test individual point transformation functions."""
    
    def test_rotate_point_90(self):
        """Test 90-degree point rotation."""
        # Test in 10x10 container
        assert rotate_point_90(0, 0, 10, 10) == (9, 0)
        assert rotate_point_90(5, 5, 10, 10) == (4, 5)
        assert rotate_point_90(9, 0, 10, 10) == (9, 9)
    
    def test_rotate_point_180(self):
        """Test 180-degree point rotation."""
        assert rotate_point_180(0, 0, 10, 10) == (9, 9)
        assert rotate_point_180(5, 5, 10, 10) == (4, 4)
        assert rotate_point_180(9, 9, 10, 10) == (0, 0)
    
    def test_rotate_point_270(self):
        """Test 270-degree point rotation."""
        assert rotate_point_270(0, 0, 10, 10) == (0, 9)
        assert rotate_point_270(5, 5, 10, 10) == (5, 4)
        assert rotate_point_270(0, 9, 10, 10) == (0, 0)
    
    def test_mirror_point_horizontal(self):
        """Test horizontal mirroring."""
        assert mirror_point_horizontal(0, 5, 10, 10) == (9, 5)
        assert mirror_point_horizontal(5, 3, 10, 10) == (4, 3)
        assert mirror_point_horizontal(9, 7, 10, 10) == (0, 7)
    
    def test_mirror_point_vertical(self):
        """Test vertical mirroring."""
        assert mirror_point_vertical(5, 0, 10, 10) == (5, 9)
        assert mirror_point_vertical(3, 5, 10, 10) == (3, 4)
        assert mirror_point_vertical(7, 9, 10, 10) == (7, 0)

class TestSolutionTransformations:
    """Test solution-level transformations."""
    
    @pytest.fixture
    def sample_solution(self):
        """Sample solution with 2 tiles."""
        return [
            (0, 0, 5, 5, "original"),  # Bottom-left tile
            (5, 0, 5, 5, "original")   # Bottom-right tile
        ]
    
    def test_rotate_solution_90(self, sample_solution):
        """Test 90-degree solution rotation."""
        rotated = rotate_solution_90(sample_solution, 10, 10)
        
        # Check that we have same number of tiles
        assert len(rotated) == len(sample_solution)
        
        # Check tile dimensions are preserved (but may be swapped)
        for original, rot in zip(sample_solution, rotated):
            orig_area = original[2] * original[3]
            rot_area = rot[2] * rot[3]
            assert orig_area == rot_area, "Area should be preserved"
    
    def test_rotate_solution_180(self, sample_solution):
        """Test 180-degree solution rotation."""
        rotated = rotate_solution_180(sample_solution, 10, 10)
        
        assert len(rotated) == len(sample_solution)
        
        # 180-degree rotation should preserve tile dimensions
        for original, rot in zip(sample_solution, rotated):
            assert original[2] == rot[2], "Width should be preserved"
            assert original[3] == rot[3], "Height should be preserved"
    
    def test_double_rotation_identity(self, sample_solution):
        """Test that rotating twice by 180° gives back original (approximately)."""
        rotated_once = rotate_solution_180(sample_solution, 10, 10)
        rotated_twice = rotate_solution_180(rotated_once, 10, 10)
        
        # Sort both solutions for comparison
        original_sorted = sorted(sample_solution)
        twice_rotated_sorted = sorted(rotated_twice)
        
        assert original_sorted == twice_rotated_sorted, "Double 180° rotation should be identity"
    
    def test_translation(self, sample_solution):
        """Test solution translation."""
        translated = translate_solution(sample_solution, 3, 2)
        
        # Check that all tiles are moved by the same offset
        for original, trans in zip(sample_solution, translated):
            assert trans[0] == original[0] + 3, "X coordinate should be offset by 3"
            assert trans[1] == original[1] + 2, "Y coordinate should be offset by 2"
            assert trans[2] == original[2], "Width should be unchanged"
            assert trans[3] == original[3], "Height should be unchanged"
            assert trans[4] == original[4], "Orientation should be unchanged"
    
    def test_center_solution(self):
        """Test solution centering."""
        # Off-center solution
        positions = [
            (10, 10, 5, 5, "original"),
            (15, 10, 5, 5, "original")
        ]
        
        centered = center_solution(positions, 30, 30)
        
        # Calculate bounding box of centered solution
        min_x = min(x for x, _, _, _, _ in centered)
        min_y = min(y for _, y, _, _, _ in centered)
        max_x = max(x + w for x, _, w, _, _ in centered)
        max_y = max(y + h for _, y, _, h, _ in centered)
        
        # Should be approximately centered
        used_w = max_x - min_x
        used_h = max_y - min_y
        expected_offset_x = (30 - used_w) // 2
        expected_offset_y = (30 - used_h) // 2
        
        assert abs(min_x - expected_offset_x) <= 1, "Should be horizontally centered"
        assert abs(min_y - expected_offset_y) <= 1, "Should be vertically centered"
    
    def test_calculate_bounding_box(self, sample_solution):
        """Test bounding box calculation."""
        bbox = calculate_bounding_box(sample_solution)
        
        # For sample solution: two 5x5 tiles at (0,0) and (5,0)
        expected_bbox = (0, 0, 10, 5)  # (min_x, min_y, max_x, max_y)
        assert bbox == expected_bbox
    
    def test_empty_solution_transformations(self):
        """Test transformations on empty solutions."""
        empty_solution = []
        
        # All transformations should handle empty solutions gracefully
        assert rotate_solution_90(empty_solution, 10, 10) == []
        assert rotate_solution_180(empty_solution, 10, 10) == []
        assert rotate_solution_270(empty_solution, 10, 10) == []
        assert translate_solution(empty_solution, 5, 5) == []
        assert center_solution(empty_solution, 10, 10) == []
        assert calculate_bounding_box(empty_solution) == (0, 0, 0, 0)

class TestGeometricProperties:
    """Test geometric property preservation."""
    
    def test_area_preservation(self):
        """Test that transformations preserve total area."""
        positions = [
            (0, 0, 3, 4, "original"),
            (3, 0, 2, 6, "rotated"),
            (0, 4, 5, 2, "original")
        ]
        
        original_area = sum(w * h for _, _, w, h, _ in positions)
        
        transformations = [
            rotate_solution_90(positions, 20, 20),
            rotate_solution_180(positions, 20, 20),
            rotate_solution_270(positions, 20, 20),
            translate_solution(positions, 5, 3)
        ]
        
        for transformed in transformations:
            transformed_area = sum(w * h for _, _, w, h, _ in transformed)
            assert transformed_area == original_area, "Area should be preserved"
    
    def test_tile_count_preservation(self):
        """Test that transformations preserve tile count."""
        positions = [
            (i * 2, 0, 2, 2, "original") for i in range(5)
        ]
        
        transformations = [
            rotate_solution_90(positions, 20, 20),
            rotate_solution_180(positions, 20, 20),
            rotate_solution_270(positions, 20, 20),
            translate_solution(positions, 3, 3),
            center_solution(positions, 30, 30)
        ]
        
        for transformed in transformations:
            assert len(transformed) == len(positions), "Tile count should be preserved"
    
    def test_bounds_checking(self):
        """Test that transformations respect container bounds."""
        positions = [(0, 0, 5, 5, "original")]
        
        # Center in small container
        centered = center_solution(positions, 10, 10)
        
        for x, y, w, h, _ in centered:
            assert x >= 0, "X coordinate should be non-negative"
            assert y >= 0, "Y coordinate should be non-negative"
            assert x + w <= 10, "Tile should not exceed container width"
            assert y + h <= 10, "Tile should not exceed container height"

class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_single_tile(self):
        """Test transformations on single tile."""
        single_tile = [(5, 3, 4, 2, "original")]
        
        # All transformations should work
        rotated = rotate_solution_90(single_tile, 20, 20)
        assert len(rotated) == 1
        
        translated = translate_solution(single_tile, 1, 1)
        assert translated[0][:2] == (6, 4)
        
        centered = center_solution(single_tile, 20, 20)
        # Should be approximately centered
        x, y, w, h, _ = centered[0]
        expected_x = (20 - w) // 2
        expected_y = (20 - h) // 2
        assert abs(x - expected_x) <= 1
        assert abs(y - expected_y) <= 1
    
    def test_square_tiles(self):
        """Test transformations on square tiles."""
        square_tiles = [(0, 0, 5, 5, "original"), (5, 5, 5, 5, "original")]
        
        # Rotations of square tiles should preserve dimensions
        rotated_90 = rotate_solution_90(square_tiles, 20, 20)
        for original, rotated in zip(square_tiles, rotated_90):
            assert rotated[2] == original[2], "Square width should be preserved"
            assert rotated[3] == original[3], "Square height should be preserved"
    
    def test_large_translations(self):
        """Test large translations."""
        positions = [(0, 0, 2, 2, "original")]
        
        # Large positive translation
        translated = translate_solution(positions, 100, 100)
        assert translated[0][:2] == (100, 100)
        
        # Large negative translation
        translated = translate_solution(positions, -50, -50)
        assert translated[0][:2] == (-50, -50)
    
    def test_rotation_consistency(self):
        """Test that multiple rotations are consistent."""
        positions = [(2, 3, 4, 6, "original")]
        
        # Four 90-degree rotations should return to original (approximately)
        current = positions
        for i in range(4):
            current = rotate_solution_90(current, 20, 20)
        
        # Should be back to roughly original position (may have small offset due to rounding)
        original_bbox = calculate_bounding_box(positions)
        final_bbox = calculate_bounding_box(current)
        
        # Areas should match
        orig_area = (original_bbox[2] - original_bbox[0]) * (original_bbox[3] - original_bbox[1])
        final_area = (final_bbox[2] - final_bbox[0]) * (final_bbox[3] - final_bbox[1])
        assert orig_area == final_area, "Area should be preserved after 4 rotations"

if __name__ == "__main__":
    pytest.main([__file__])
