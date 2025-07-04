#!/usr/bin/env python3
"""
Quick test script for the 2D packing framework.
"""

from src.core.problem import PackingProblem
from src.solvers.hybrid_solver import HybridSolver

def test_case(name, container_w, container_h, tile_w, tile_h):
    """Test a specific packing case."""
    print(f"\n=== {name} ===")
    print(f"Container: {container_w}×{container_h}, Tiles: {tile_w}×{tile_h}")
    
    problem = PackingProblem(
        container_w=container_w, 
        container_h=container_h,
        tile_w=tile_w, 
        tile_h=tile_h, 
        allow_rotation=True
    )
    
    solver = HybridSolver(time_limit=60.0)
    solution = solver.solve(problem)
    
    print(f"Result: {solution.num_tiles}/{problem.theoretical_max_tiles} tiles ({solution.efficiency:.1f}% efficiency)")
    print(f"Solve time: {solution.solve_time:.3f}s")
    
    return solution

def main():
    """Run test cases."""
    print("🚀 2D Rectangle Packing Framework Test")
    print("=" * 50)
    
    # Test cases
    test_case("Case 1: 40×48 with 12×16 tiles", 40, 48, 12, 16)
    test_case("Case 2: 40×48 with 10×10 tiles", 40, 48, 10, 10) 
    test_case("Case 3: 40×40 with 24×16 tiles (Pinwheel)", 40, 40, 24, 16)
    
    print(f"\n✅ All tests completed!")

if __name__ == "__main__":
    main()