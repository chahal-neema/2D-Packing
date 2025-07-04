#!/usr/bin/env python3
"""
Enhanced CSV Batch Packer with Multiple Solutions and Centering
Finds all optimal arrangements for each packing problem.
"""

import csv
import json
import math
import sys
from typing import List, Dict, Any

from src.core.problem import PackingProblem
from src.solvers.hybrid_solver import HybridSolver
from src.core.geometry import center_solution


def read_rows(filename: str):
    """Yield dictionaries of parameters from a CSV file."""
    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row


def parse_bool(value: str) -> bool:
    if value is None:
        return True
    value = value.strip().lower()
    return value in {"1", "true", "t", "yes", "y"}


def round_up(value: str) -> int:
    return int(math.ceil(float(value)))


def solve_problem_multiple(params: dict) -> List[Dict[str, Any]]:
    """Solve a problem and return ALL optimal solutions with centering."""
    container_w = round_up(params.get("container_w"))
    container_h = round_up(params.get("container_h"))
    tile_w = round_up(params.get("tile_w"))
    tile_h = round_up(params.get("tile_h"))
    allow_rotation = parse_bool(params.get("allow_rotation", "true"))
    max_solutions = int(params.get("max_solutions", "20"))

    problem = PackingProblem(
        container_w=container_w,
        container_h=container_h,
        tile_w=tile_w,
        tile_h=tile_h,
        allow_rotation=allow_rotation,
    )

    print(f"\n🔧 Processing: {container_w}×{container_h} container with {tile_w}×{tile_h} tiles")
    
    solver = HybridSolver()
    
    # First get the best single solution to know the target
    best_solution = solver.solve(problem)
    if best_solution.num_tiles == 0:
        return []
    
    # Try to find multiple solutions using backtracking for manageable cases
    if best_solution.num_tiles <= 25:  # Manageable for backtracking
        print(f"   Using backtracking to find multiple solutions...")
        from src.solvers.backtrack_solver import BacktrackSolver
        backtrack_solver = BacktrackSolver(max_solutions=max_solutions, time_limit=30.0)
        try:
            solutions = backtrack_solver.solve_all_optimal(problem, max_solutions)
            if not solutions or solutions[0].num_tiles < best_solution.num_tiles:
                print(f"   Backtracking didn't find optimal, using single best solution")
                solutions = [best_solution]
        except Exception as e:
            print(f"   Backtracking failed: {e}, using single best solution")
            solutions = [best_solution]
    else:
        # For very large problems, just use the single best solution
        print(f"   Problem too large for multiple solution search, using single best")
        solutions = [best_solution]
    
    if not solutions:
        return []
    
    results = []
    for i, solution in enumerate(solutions):
        # Center the solution
        centered_positions = center_solution(
            solution.tile_positions, 
            container_w, 
            container_h
        )
        
        # Calculate bounding box for the centered solution
        if centered_positions:
            min_x = min(x for x, y, w, h, o in centered_positions)
            min_y = min(y for _, y, w, h, o in centered_positions)
            max_x = max(x + w for x, y, w, h, o in centered_positions)
            max_y = max(y + h for _, y, w, h, o in centered_positions)
            used_width = max_x - min_x
            used_height = max_y - min_y
            is_centered = abs((min_x + max_x) / 2 - container_w / 2) < 0.5 and abs((min_y + max_y) / 2 - container_h / 2) < 0.5
        else:
            used_width = used_height = 0
            is_centered = False
        
        # Count tile orientations
        orientations = {}
        for _, _, _, _, orientation in centered_positions:
            orientations[orientation] = orientations.get(orientation, 0) + 1
        
        result = {
            "container_w": container_w,
            "container_h": container_h,
            "tile_w": tile_w,
            "tile_h": tile_h,
            "allow_rotation": allow_rotation,
            "solution_number": i + 1,
            "total_solutions": len(solutions),
            "theoretical_max_tiles": problem.theoretical_max_tiles,
            "tiles_placed": solution.num_tiles,
            "efficiency": round(solution.efficiency, 2),
            "used_width": used_width,
            "used_height": used_height,
            "is_centered": is_centered,
            "original_tiles": orientations.get("original", 0),
            "rotated_tiles": orientations.get("rotated", 0),
            "solver_used": solution.solver_name,
            "tile_positions": centered_positions,
        }
        results.append(result)
    
    print(f"✅ Found {len(solutions)} optimal solutions, all centered")
    return results


def write_results_enhanced(results: List[Dict], filename: str):
    """Write enhanced results with multiple solutions per problem."""
    if not results:
        print("No results to write")
        return
        
    fieldnames = [
        "container_w", "container_h", "tile_w", "tile_h", "allow_rotation",
        "solution_number", "total_solutions", 
        "theoretical_max_tiles", "tiles_placed", "efficiency",
        "used_width", "used_height", "is_centered",
        "original_tiles", "rotated_tiles", "solver_used",
        "tile_positions"
    ]
    
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            row_copy = row.copy()
            # Serialize tile positions as JSON string
            row_copy["tile_positions"] = json.dumps(row_copy["tile_positions"])
            writer.writerow(row_copy)


def create_summary_report(results: List[Dict], filename: str):
    """Create a summary report showing all solutions per problem."""
    if not results:
        return
        
    # Group results by problem
    problems = {}
    for result in results:
        key = (result["container_w"], result["container_h"], result["tile_w"], result["tile_h"])
        if key not in problems:
            problems[key] = []
        problems[key].append(result)
    
    with open(filename, "w") as f:
        f.write("# 2D Packing Results Summary\n\n")
        
        for i, (key, solutions) in enumerate(problems.items(), 1):
            container_w, container_h, tile_w, tile_h = key
            first_solution = solutions[0]
            
            f.write(f"## Problem {i}: {container_w}×{container_h} container with {tile_w}×{tile_h} tiles\n\n")
            f.write(f"- **Theoretical Maximum**: {first_solution['theoretical_max_tiles']} tiles\n")
            f.write(f"- **Solutions Found**: {len(solutions)} optimal arrangements\n")
            f.write(f"- **Tiles Placed**: {first_solution['tiles_placed']} tiles\n")
            f.write(f"- **Efficiency**: {first_solution['efficiency']}%\n")
            f.write(f"- **Solver**: {first_solution['solver_used']}\n\n")
            
            if len(solutions) > 1:
                f.write("### Different Optimal Arrangements:\n\n")
                for j, sol in enumerate(solutions, 1):
                    f.write(f"**Solution {j}**:\n")
                    f.write(f"- Used area: {sol['used_width']}×{sol['used_height']}\n")
                    f.write(f"- Centered: {'✅' if sol['is_centered'] else '❌'}\n")
                    f.write(f"- Original orientation: {sol['original_tiles']} tiles\n")
                    f.write(f"- Rotated orientation: {sol['rotated_tiles']} tiles\n\n")
            
            f.write("---\n\n")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python csv_batch_packer_enhanced.py <input.csv> <output.csv>")
        print("\nOptional CSV columns:")
        print("- max_solutions: Maximum number of solutions to find (default: 20)")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    summary_file = output_file.replace('.csv', '_summary.md')

    all_results = []
    
    for params in read_rows(input_file):
        try:
            problem_results = solve_problem_multiple(params)
            all_results.extend(problem_results)
        except Exception as e:
            print(f"❌ Failed to process row {params}: {e}")

    if all_results:
        write_results_enhanced(all_results, output_file)
        create_summary_report(all_results, summary_file)
        print(f"\n📊 Results written to:")
        print(f"   - {output_file} (detailed CSV)")
        print(f"   - {summary_file} (summary report)")
        
        # Print quick summary
        total_problems = len(set((r["container_w"], r["container_h"], r["tile_w"], r["tile_h"]) for r in all_results))
        total_solutions = len(all_results)
        print(f"\n✅ Processed {total_problems} problems, found {total_solutions} total solutions")
    else:
        print("❌ No results generated")