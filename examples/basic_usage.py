"""
Basic usage examples for the rectangle packing framework.
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.core.problem import PackingProblem
from src.core.solution import PackingSolution
from src.solvers.hybrid_solver import HybridSolver
from src.solvers.mathematical_solver import MathematicalSolver
from src.solvers.greedy_solver import GreedySolver
from src.visualization.plotter import visualize_solution, visualize_multiple_solutions

def example_1_simple_packing():
    """Example 1: Simple rectangle packing with a single solver."""
    print("🔧 EXAMPLE 1: Simple Rectangle Packing")
    print("="*50)
    
    # Define the problem
    problem = PackingProblem(
        container_w=40,
        container_h=48,
        tile_w=10,
        tile_h=10,
        allow_rotation=True
    )
    
    print(f"Problem: Pack {problem.tile_w}×{problem.tile_h} tiles in {problem.container_w}×{problem.container_h} container")
    print(f"Theoretical maximum: {problem.theoretical_max_tiles} tiles")
    
    # Solve with hybrid solver
    solver = HybridSolver(time_limit=30)
    solution = solver.solve(problem)
    
    # Display results
    print(f"\n✅ Solution found!")
    print(f"   Tiles placed: {solution.num_tiles}")
    print(f"   Efficiency: {solution.efficiency:.1f}%")
    print(f"   Solve time: {solution.solve_time:.3f}s")
    print(f"   Solver used: {solution.solver_name}")
    print(f"   Centered: {solution.is_centered}")
    
    # Show tile positions
    print(f"\n📋 Tile positions:")
    for i, (x, y, w, h, orientation) in enumerate(solution.tile_positions):
        print(f"   Tile {i+1}: ({x},{y}) {w}×{h} {orientation}")
    
    # Visualize
    print(f"\n🎨 Creating visualization...")
    fig = visualize_solution(solution, problem, title="Example 1: Simple Packing")
    
    return solution

def example_2_compare_solvers():
    """Example 2: Compare different solvers on the same problem."""
    print("\n🔧 EXAMPLE 2: Comparing Different Solvers")
    print("="*50)
    
    # Define problem
    problem = PackingProblem(30, 20, 8, 5, allow_rotation=True)
    print(f"Problem: Pack {problem.tile_w}×{problem.tile_h} tiles in {problem.container_w}×{problem.container_h} container")
    
    # Test different solvers
    solvers = [
        ("Mathematical", MathematicalSolver()),
        ("Greedy (Bottom-Left)", GreedySolver("bottom_left")),
        ("Greedy (Center-Out)", GreedySolver("center_out")),
        ("Hybrid", HybridSolver(time_limit=10))
    ]
    
    solutions = []
    
    print(f"\n🏁 Solver comparison:")
    for name, solver in solvers:
        print(f"   Testing {name}...", end=" ")
        
        try:
            solution = solver.solve(problem)
            solutions.append(solution)
            
            print(f"✅ {solution.num_tiles} tiles ({solution.efficiency:.1f}%) in {solution.solve_time:.3f}s")
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    # Find best solution
    if solutions:
        best_solution = max(solutions, key=lambda s: s.num_tiles)
        print(f"\n🏆 Best result: {best_solution.solver_name} with {best_solution.num_tiles} tiles")
        
        # Visualize comparison
        print(f"\n🎨 Creating comparison visualization...")
        fig = visualize_multiple_solutions(solutions, problem)
    
    return solutions

def example_3_rotation_impact():
    """Example 3: Demonstrate the impact of allowing rotation."""
    print("\n🔧 EXAMPLE 3: Impact of Rotation")
    print("="*50)
    
    # Test same problem with and without rotation
    base_problem = PackingProblem(35, 25, 7, 10)
    
    problems = [
        ("Without Rotation", PackingProblem(35, 25, 7, 10, allow_rotation=False)),
        ("With Rotation", PackingProblem(35, 25, 7, 10, allow_rotation=True))
    ]
    
    solver = HybridSolver(time_limit=15)
    solutions = []
    
    print(f"Container: 35×25, Tiles: 7×10")
    print(f"\n🔄 Rotation comparison:")
    
    for name, problem in problems:
        print(f"   {name}...", end=" ")
        
        solution = solver.solve(problem)
        solutions.append(solution)
        
        print(f"✅ {solution.num_tiles} tiles ({solution.efficiency:.1f}%)")
        
        # Show orientation breakdown
        orientations = {}
        for _, _, _, _, orientation in solution.tile_positions:
            orientations[orientation] = orientations.get(orientation, 0) + 1
        
        if orientations:
            orientation_str = ", ".join([f"{count} {orient}" for orient, count in orientations.items()])
            print(f"      Orientations: {orientation_str}")
    
    # Calculate improvement
    if len(solutions) == 2:
        without_rot, with_rot = solutions
        improvement = with_rot.num_tiles - without_rot.num_tiles
        improvement_pct = (improvement / without_rot.num_tiles * 100) if without_rot.num_tiles > 0 else 0
        
        print(f"\n📈 Improvement with rotation: +{improvement} tiles ({improvement_pct:.1f}% increase)")
    
    # Visualize
    if solutions:
        print(f"\n🎨 Creating rotation comparison...")
        labels = [name for name, _ in problems]
        fig = visualize_multiple_solutions(solutions, max_cols=2)
    
    return solutions

def example_4_find_all_solutions():
    """Example 4: Find all optimal solutions."""
    print("\n🔧 EXAMPLE 4: Finding All Optimal Solutions")
    print("="*50)
    
    # Problem that might have multiple solutions
    problem = PackingProblem(30, 20, 10, 5, allow_rotation=True)
    print(f"Problem: Pack {problem.tile_w}×{problem.tile_h} tiles in {problem.container_w}×{problem.container_h} container")
    
    # Find all optimal solutions
    solver = HybridSolver(time_limit=20)
    print(f"\n🔍 Searching for all optimal solutions...")
    
    solutions = solver.solve_all_optimal(problem, max_solutions=10)
    
    if solutions:
        max_tiles = max(s.num_tiles for s in solutions)
        print(f"✅ Found {len(solutions)} optimal solutions with {max_tiles} tiles each:")
        
        for i, solution in enumerate(solutions):
            print(f"   Solution {i+1}: {solution.efficiency:.1f}% efficiency, centered: {solution.is_centered}")
            
            # Show unique characteristics
            bbox = solution.bounding_box
            used_w = bbox[2] - bbox[0]
            used_h = bbox[3] - bbox[1]
            aspect_ratio = used_w / used_h if used_h > 0 else float('inf')
            print(f"      Bounding box: {used_w}×{used_h} (aspect ratio: {aspect_ratio:.2f})")
        
        # Visualize all solutions
        print(f"\n🎨 Creating visualization of all solutions...")
        fig = visualize_multiple_solutions(solutions, problem, max_cols=3)
    else:
        print("❌ No solutions found!")
    
    return solutions

def example_5_large_problem():
    """Example 5: Solving a larger, more challenging problem."""
    print("\n🔧 EXAMPLE 5: Large Problem Challenge")
    print("="*50)
    
    # Larger, more challenging problem
    problem = PackingProblem(60, 45, 7, 11, allow_rotation=True)
    print(f"Problem: Pack {problem.tile_w}×{problem.tile_h} tiles in {problem.container_w}×{problem.container_h} container")
    print(f"Theoretical maximum: {problem.theoretical_max_tiles} tiles")
    print(f"Challenge: Irregular tile dimensions make this harder to solve optimally")
    
    # Solve with extended time limit
    solver = HybridSolver(time_limit=60)
    print(f"\n⏱️  Solving (may take up to 60 seconds)...")
    
    solution = solver.solve(problem)
    
    print(f"\n✅ Large problem solved!")
    print(f"   Tiles placed: {solution.num_tiles}/{problem.theoretical_max_tiles}")
    print(f"   Efficiency: {solution.efficiency:.1f}%")
    print(f"   Optimality: {solution.num_tiles/problem.theoretical_max_tiles*100:.1f}% of theoretical max")
    print(f"   Solve time: {solution.solve_time:.3f}s")
    print(f"   Final solver: {solution.solver_name}")
    
    # Calculate some statistics
    total_tile_area = solution.num_tiles * problem.tile_area
    wasted_area = problem.container_area - total_tile_area
    print(f"   Wasted area: {wasted_area} units² ({wasted_area/problem.container_area*100:.1f}%)")
    
    # Visualize
    print(f"\n🎨 Creating visualization...")
    fig = visualize_solution(solution, problem, title="Example 5: Large Problem")
    
    return solution

def example_6_export_results():
    """Example 6: Export results in various formats."""
    print("\n🔧 EXAMPLE 6: Exporting Results")
    print("="*50)
    
    # Solve a problem
    problem = PackingProblem(25, 25, 6, 8, allow_rotation=True)
    solver = HybridSolver()
    solution = solver.solve(problem)
    
    print(f"Solved: {solution.num_tiles} tiles in {problem.container_w}×{problem.container_h} container")
    
    # Export in different formats
    from src.visualization.export import (
        export_solution_to_json, export_solution_to_csv,
        save_solution_as_image, create_solution_report
    )
    
    print(f"\n💾 Exporting results...")
    
    try:
        # Export to JSON
        export_solution_to_json(solution, "example_solution.json")
        
        # Export to CSV
        export_solution_to_csv(solution, "example_solution.csv")
        
        # Export as image
        save_solution_as_image(solution, "example_solution.png", 
                             title="Example 6: Exported Solution")
        
        # Create HTML report
        create_solution_report(problem, [solution], "example_report.html")
        
        print("✅ Exported files:")
        print("   - example_solution.json (solution data)")
        print("   - example_solution.csv (tile positions)")
        print("   - example_solution.png (visualization)")
        print("   - example_report.html (complete report)")
        
    except Exception as e:
        print(f"❌ Export failed: {e}")
    
    return solution

def run_all_examples():
    """Run all examples in sequence."""
    print("🚀 RECTANGLE PACKING FRAMEWORK - BASIC EXAMPLES")
    print("="*70)
    
    examples = [
        example_1_simple_packing,
        example_2_compare_solvers,
        example_3_rotation_impact,
        example_4_find_all_solutions,
        example_5_large_problem,
        example_6_export_results
    ]
    
    results = {}
    
    for i, example_func in enumerate(examples, 1):
        try:
            print(f"\n{'='*70}")
            result = example_func()
            results[f"example_{i}"] = result
            print(f"✅ Example {i} completed successfully!")
            
        except Exception as e:
            print(f"❌ Example {i} failed: {e}")
            results[f"example_{i}"] = None
        
        # Pause between examples
        if i < len(examples):
            input("\nPress Enter to continue to next example...")
    
    print(f"\n{'='*70}")
    print("🏁 ALL EXAMPLES COMPLETED!")
    
    # Summary
    successful = sum(1 for result in results.values() if result is not None)
    print(f"📊 Results: {successful}/{len(examples)} examples completed successfully")
    
    return results

def interactive_example():
    """Interactive example where user can input their own problem."""
    print("\n🔧 INTERACTIVE EXAMPLE")
    print("="*50)
    print("Define your own rectangle packing problem!")
    
    try:
        # Get user input
        print("\nContainer dimensions:")
        container_w = int(input("  Width: "))
        container_h = int(input("  Height: "))
        
        print("\nTile dimensions:")
        tile_w = int(input("  Width: "))
        tile_h = int(input("  Height: "))
        
        allow_rotation = input("\nAllow rotation? (y/n): ").lower().startswith('y')
        
        # Create and solve problem
        problem = PackingProblem(container_w, container_h, tile_w, tile_h, allow_rotation=allow_rotation)
        
        print(f"\n📊 Your problem:")
        print(f"   Container: {container_w}×{container_h}")
        print(f"   Tiles: {tile_w}×{tile_h}")
        print(f"   Rotation: {'Allowed' if allow_rotation else 'Not allowed'}")
        print(f"   Theoretical max: {problem.theoretical_max_tiles} tiles")
        
        # Solve
        solver = HybridSolver(time_limit=30)
        print(f"\n🔍 Solving...")
        solution = solver.solve(problem)
        
        # Results
        print(f"\n✅ Solution:")
        print(f"   Tiles placed: {solution.num_tiles}")
        print(f"   Efficiency: {solution.efficiency:.1f}%")
        print(f"   Solve time: {solution.solve_time:.3f}s")
        
        # Visualize
        fig = visualize_solution(solution, problem, title="Your Custom Problem")
        
        return solution
        
    except ValueError as e:
        print(f"❌ Invalid input: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🎯 BASIC EXAMPLES MENU")
    print("="*30)
    print("1. Run all examples")
    print("2. Interactive example")
    print("3. Single example")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == "1":
        run_all_examples()
    elif choice == "2":
        interactive_example()
    elif choice == "3":
        print("\nAvailable examples:")
        print("1. Simple packing")
        print("2. Compare solvers")
        print("3. Rotation impact")
        print("4. Find all solutions")
        print("5. Large problem")
        print("6. Export results")
        
        example_num = input("\nChoose example (1-6): ").strip()
        
        examples = {
            "1": example_1_simple_packing,
            "2": example_2_compare_solvers,
            "3": example_3_rotation_impact,
            "4": example_4_find_all_solutions,
            "5": example_5_large_problem,
            "6": example_6_export_results
        }
        
        if example_num in examples:
            examples[example_num]()
        else:
            print("Invalid choice!")
    else:
        print("Invalid choice!")
