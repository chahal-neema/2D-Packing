import csv
import json
import math
import sys

from src.core.problem import PackingProblem
from src.solvers.hybrid_solver import HybridSolver


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


def solve_problem(params: dict) -> dict:
    container_w = round_up(params.get("container_w"))
    container_h = round_up(params.get("container_h"))
    tile_w = round_up(params.get("tile_w"))
    tile_h = round_up(params.get("tile_h"))
    allow_rotation = parse_bool(params.get("allow_rotation", "true"))

    problem = PackingProblem(
        container_w=container_w,
        container_h=container_h,
        tile_w=tile_w,
        tile_h=tile_h,
        allow_rotation=allow_rotation,
    )

    solver = HybridSolver()
    solution = solver.solve(problem)

    return {
        "container_w": container_w,
        "container_h": container_h,
        "tile_w": tile_w,
        "tile_h": tile_h,
        "allow_rotation": allow_rotation,
        "theoretical_max_tiles": problem.theoretical_max_tiles,
        "tiles_placed": solution.num_tiles,
        "efficiency": round(solution.efficiency, 2),
        "tile_positions": solution.tile_positions,
    }


def write_results(results, filename: str):
    fieldnames = [
        "container_w",
        "container_h",
        "tile_w",
        "tile_h",
        "allow_rotation",
        "theoretical_max_tiles",
        "tiles_placed",
        "efficiency",
        "tile_positions",
    ]
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            row = row.copy()
            # Serialize tile positions as JSON string for easy parsing
            row["tile_positions"] = json.dumps(row["tile_positions"])
            writer.writerow(row)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python csv_batch_packer.py <input.csv> <output.csv>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    results = []
    for params in read_rows(input_file):
        try:
            results.append(solve_problem(params))
        except Exception as e:
            print(f"Failed to process row {params}: {e}")

    write_results(results, output_file)
    print(f"Results written to {output_file}")
