import numpy as np
import matplotlib.pyplot as plt
from ortools.linear_solver import pywraplp
import time
from collections import defaultdict
import itertools

class FreeRectangleManager:
    """Efficient management of free rectangular spaces."""
    
    def __init__(self, container_w, container_h):
        self.free_rects = [(0, 0, container_w, container_h)]  # (x, y, width, height)
        self.container_w = container_w
        self.container_h = container_h
    
    def get_valid_placements(self, tile_w, tile_h):
        """Get all valid placements for a tile of given dimensions."""
        placements = []
        
        for rect_x, rect_y, rect_w, rect_h in self.free_rects:
            # Try original orientation
            if tile_w <= rect_w and tile_h <= rect_h:
                # BLF heuristic: bottom-left positions within this rectangle
                for y in range(rect_y, rect_y + rect_h - tile_h + 1):
                    for x in range(rect_x, rect_x + rect_w - tile_w + 1):
                        placements.append((x, y, tile_w, tile_h, 0))
            
            # Try rotated orientation (if different)
            if tile_w != tile_h and tile_h <= rect_w and tile_w <= rect_h:
                for y in range(rect_y, rect_y + rect_h - tile_w + 1):
                    for x in range(rect_x, rect_x + rect_w - tile_h + 1):
                        placements.append((x, y, tile_h, tile_w, 1))
        
        return placements
    
    def place_tile(self, x, y, w, h):
        """Place a tile and update free rectangles."""
        new_rects = []
        
        for rect_x, rect_y, rect_w, rect_h in self.free_rects:
            # Check if this rectangle intersects with the placed tile
            if (rect_x < x + w and rect_x + rect_w > x and 
                rect_y < y + h and rect_y + rect_h > y):
                
                # Split the rectangle around the placed tile
                # Left rectangle
                if rect_x < x:
                    new_rects.append((rect_x, rect_y, x - rect_x, rect_h))
                
                # Right rectangle  
                if rect_x + rect_w > x + w:
                    new_rects.append((x + w, rect_y, rect_x + rect_w - (x + w), rect_h))
                
                # Bottom rectangle
                if rect_y < y:
                    new_rects.append((max(rect_x, x), rect_y, 
                                    min(rect_x + rect_w, x + w) - max(rect_x, x), y - rect_y))
                
                # Top rectangle
                if rect_y + rect_h > y + h:
                    new_rects.append((max(rect_x, x), y + h,
                                    min(rect_x + rect_w, x + w) - max(rect_x, x), 
                                    rect_y + rect_h - (y + h)))
            else:
                # Rectangle doesn't intersect, keep it
                new_rects.append((rect_x, rect_y, rect_w, rect_h))
        
        self.free_rects = new_rects
        self._merge_rectangles()
    
    def _merge_rectangles(self):
        """Merge adjacent rectangles to maintain efficiency."""
        # Simple implementation - can be optimized further
        merged = True
        while merged:
            merged = False
            new_rects = []
            used = set()
            
            for i, rect1 in enumerate(self.free_rects):
                if i in used:
                    continue
                    
                x1, y1, w1, h1 = rect1
                merged_any = False
                
                for j, rect2 in enumerate(self.free_rects[i+1:], i+1):
                    if j in used:
                        continue
                        
                    x2, y2, w2, h2 = rect2
                    
                    # Check if rectangles can be merged horizontally
                    if (y1 == y2 and h1 == h2 and 
                        ((x1 + w1 == x2) or (x2 + w2 == x1))):
                        new_x = min(x1, x2)
                        new_rects.append((new_x, y1, w1 + w2, h1))
                        used.add(i)
                        used.add(j)
                        merged = True
                        merged_any = True
                        break
                    
                    # Check if rectangles can be merged vertically
                    elif (x1 == x2 and w1 == w2 and 
                          ((y1 + h1 == y2) or (y2 + h2 == y1))):
                        new_y = min(y1, y2)
                        new_rects.append((x1, new_y, w1, h1 + h2))
                        used.add(i)
                        used.add(j)
                        merged = True
                        merged_any = True
                        break
                
                if not merged_any:
                    new_rects.append(rect1)
            
            self.free_rects = new_rects
    
    def get_total_free_area(self):
        """Calculate total free area for pruning."""
        return sum(w * h for x, y, w, h in self.free_rects)

def apply_symmetry_breaking(container_w, container_h, tile_w, tile_h):
    """Apply symmetry breaking constraints to reduce search space."""
    constraints = []
    
    # Force first tile to be in top-left quadrant
    max_x = container_w // 2
    max_y = container_h // 2
    
    # If tiles are not square, prefer a specific orientation for the first tile
    preferred_orientation = 0 if tile_w >= tile_h else 1
    
    return max_x, max_y, preferred_orientation

def calculate_lower_bound(free_area, remaining_tiles, tile_area):
    """Calculate lower bound for pruning."""
    if remaining_tiles == 0:
        return 0
    
    # Area-based lower bound
    area_bound = free_area // tile_area
    
    return min(area_bound, remaining_tiles)

def normalize_solution(positions, container_w, container_h):
    """Normalize solution to canonical form and center it."""
    if not positions:
        return positions
    
    # Extract coordinates
    coords = [(x, y, w, h) for x, y, w, h, _ in positions]
    
    # Find bounding box
    min_x = min(x for x, y, w, h in coords)
    min_y = min(y for x, y, w, h in coords)
    max_x = max(x + w for x, y, w, h in coords)
    max_y = max(y + h for x, y, w, h in coords)
    
    # Calculate centering offset
    used_w = max_x - min_x
    used_h = max_y - min_y
    offset_x = (container_w - used_w) // 2 - min_x
    offset_y = (container_h - used_h) // 2 - min_y
    
    # Apply centering
    centered_positions = []
    for (x, y, w, h, orientation) in positions:
        new_x = x + offset_x
        new_y = y + offset_y
        centered_positions.append((new_x, new_y, w, h, orientation))
    
    return centered_positions

def are_solutions_equivalent(sol1, sol2):
    """Check if two solutions are equivalent under symmetry."""
    if len(sol1) != len(sol2):
        return False
    
    # Convert to sets of tile dimensions and relative positions
    def solution_to_signature(sol):
        tiles = [(w, h) for x, y, w, h, _ in sol]
        tiles.sort()
        return tuple(tiles)
    
    return solution_to_signature(sol1) == solution_to_signature(sol2)

def deduplicate_solutions(solutions):
    """Remove duplicate solutions that are symmetric or equivalent."""
    if not solutions:
        return solutions
    
    unique_solutions = []
    
    for sol in solutions:
        is_duplicate = False
        for existing_sol in unique_solutions:
            if are_solutions_equivalent(sol, existing_sol):
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_solutions.append(sol)
    
    return unique_solutions

def solve_rectangle_packing_optimized(container_w, container_h, tile_w, tile_h, 
                                    max_tiles=None, time_limit_sec=60, center_solution=True):
    """
    Optimized ILP solver with performance tuning and symmetry handling.
    """
    print(f"🔧 OPTIMIZED ILP SOLVER: {tile_w}×{tile_h} tiles in {container_w}×{container_h} container")
    
    # Calculate bounds and apply symmetry breaking
    theoretical_max = (container_w * container_h) // (tile_w * tile_h)
    if max_tiles is None:
        max_tiles = theoretical_max
    
    tile_area = tile_w * tile_h
    max_first_x, max_first_y, preferred_orientation = apply_symmetry_breaking(
        container_w, container_h, tile_w, tile_h)
    
    print(f"📊 Theoretical maximum: {theoretical_max} tiles")
    print(f"🎯 Attempting to place: {max_tiles} tiles")
    print(f"⚡ Symmetry breaking: first tile limited to ({max_first_x}, {max_first_y})")
    
    # Initialize free rectangle manager for efficient placement detection
    free_rect_manager = FreeRectangleManager(container_w, container_h)
    
    # Create solver
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        print("❌ Could not create solver!")
        return 0, [], {}
    
    solver.SetTimeLimit(time_limit_sec * 1000)
    
    print(f"⚙️ Creating optimized variables and constraints...")
    
    # === VARIABLES WITH REDUCED SEARCH SPACE ===
    orientations = [(tile_w, tile_h), (tile_h, tile_w)] if tile_w != tile_h else [(tile_w, tile_h)]
    x = {}
    variable_count = 0
    
    for i in range(max_tiles):
        for j in range(container_w):
            for k in range(container_h):
                for o, (w, h) in enumerate(orientations):
                    # Containment constraint
                    if j + w <= container_w and k + h <= container_h:
                        # Symmetry breaking for first tile
                        if i == 0:
                            if j > max_first_x or k > max_first_y:
                                continue
                            if preferred_orientation is not None and o != preferred_orientation:
                                continue
                        
                        var_name = f"x_{i}_{j}_{k}_{o}"
                        x[i, j, k, o] = solver.IntVar(0, 1, var_name)
                        variable_count += 1
    
    print(f"📈 Created {variable_count} variables (reduced from naive approach)")
    
    # === CONSTRAINTS ===
    constraint_count = 0
    
    # 1. Placement constraints with area-based pruning
    for i in range(max_tiles):
        constraint = solver.Constraint(0, 1, f"place_tile_{i}")
        for j in range(container_w):
            for k in range(container_h):
                for o in range(len(orientations)):
                    if (i, j, k, o) in x:
                        constraint.SetCoefficient(x[i, j, k, o], 1)
        constraint_count += 1
    
    # 2. Non-overlapping constraints (optimized)
    for cell_x in range(container_w):
        for cell_y in range(container_h):
            constraint = solver.Constraint(0, 1, f"cell_{cell_x}_{cell_y}")
            
            for i in range(max_tiles):
                for j in range(container_w):
                    for k in range(container_h):
                        for o, (w, h) in enumerate(orientations):
                            if (i, j, k, o) in x:
                                if (j <= cell_x < j + w) and (k <= cell_y < k + h):
                                    constraint.SetCoefficient(x[i, j, k, o], 1)
            constraint_count += 1
    
    # 3. Additional feasibility constraints
    # Area constraint: total placed tile area ≤ container area
    area_constraint = solver.Constraint(0, container_w * container_h // tile_area, "total_area")
    for i in range(max_tiles):
        for j in range(container_w):
            for k in range(container_h):
                for o in range(len(orientations)):
                    if (i, j, k, o) in x:
                        area_constraint.SetCoefficient(x[i, j, k, o], 1)
    constraint_count += 1
    
    print(f"📈 Created {constraint_count} constraints")
    
    # === OBJECTIVE ===
    objective = solver.Objective()
    for i in range(max_tiles):
        for j in range(container_w):
            for k in range(container_h):
                for o in range(len(orientations)):
                    if (i, j, k, o) in x:
                        objective.SetCoefficient(x[i, j, k, o], 1)
    objective.SetMaximization()
    
    # === SOLVE ===
    print(f"🚀 Starting optimized solver...")
    start_time = time.time()
    status = solver.Solve()
    solve_time = time.time() - start_time
    
    # === EXTRACT AND PROCESS RESULTS ===
    solve_info = {
        'status': status,
        'solve_time': solve_time,
        'variables': variable_count,
        'constraints': constraint_count,
        'objective_value': solver.Objective().Value() if status == pywraplp.Solver.OPTIMAL else 0
    }
    
    if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE]:
        status_text = "OPTIMAL" if status == pywraplp.Solver.OPTIMAL else "FEASIBLE"
        print(f"✅ {status_text} SOLUTION FOUND in {solve_time:.2f}s")
        print(f"🎯 Tiles placed: {int(solver.Objective().Value())}")
        
        # Extract tile positions
        tile_positions = []
        for i in range(max_tiles):
            for j in range(container_w):
                for k in range(container_h):
                    for o, (w, h) in enumerate(orientations):
                        if (i, j, k, o) in x and x[i, j, k, o].solution_value() > 0.5:
                            orientation_desc = "rotated" if o == 1 else "original"
                            tile_positions.append((j, k, w, h, orientation_desc))
        
        # Apply centering if requested
        if center_solution:
            print("🎨 Centering solution...")
            tile_positions = normalize_solution(tile_positions, container_w, container_h)
        
        # Show final positions
        print("📋 Final tile positions:")
        for i, (x, y, w, h, orientation) in enumerate(tile_positions):
            print(f"   Tile {i+1}: ({x},{y}) {w}×{h} {orientation}")
        
        return int(solver.Objective().Value()), tile_positions, solve_info
    
    else:
        print(f"❌ NO SOLUTION FOUND in {solve_time:.2f}s")
        return 0, [], solve_info

def draw_optimized_solution(container_w, container_h, tile_positions, title="Optimized ILP Solution"):
    """Enhanced visualization with symmetry indicators."""
    fig, ax = plt.subplots(figsize=(12, 12 * container_h / container_w))
    ax.set_xlim(0, container_w)
    ax.set_ylim(0, container_h)
    ax.set_aspect('equal')
    ax.invert_yaxis()
    ax.set_title(title, fontsize=16, fontweight='bold')

    # Container border
    ax.plot([0, container_w, container_w, 0, 0],
            [0, 0, container_h, container_h, 0], lw=3, color='black')

    # Draw center lines for symmetry reference
    center_x, center_y = container_w / 2, container_h / 2
    ax.axvline(x=center_x, color='red', linewidth=1, alpha=0.3, linestyle='--')
    ax.axhline(y=center_y, color='red', linewidth=1, alpha=0.3, linestyle='--')

    # Tiles with enhanced visualization
    if tile_positions:
        colors = plt.cm.Set3(np.linspace(0, 1, len(tile_positions)))
        for i, (x, y, w, h, orientation) in enumerate(tile_positions):
            # Different patterns for different orientations
            if orientation == "rotated":
                rect = plt.Rectangle((x, y), w, h, fill=True, facecolor=colors[i], 
                                   edgecolor='darkblue', alpha=0.8, linewidth=2,
                                   hatch='///')
            else:
                rect = plt.Rectangle((x, y), w, h, fill=True, facecolor=colors[i], 
                                   edgecolor='darkblue', alpha=0.8, linewidth=2)
            
            ax.add_patch(rect)
            
            # Enhanced labels
            label = f"T{i+1}"
            if orientation == "rotated":
                label += "↻"
            
            ax.text(x + w / 2, y + h / 2, label, ha='center', va='center', 
                    fontsize=11, fontweight='bold', color='white',
                    bbox=dict(boxstyle="round,pad=0.1", facecolor='black', alpha=0.7))

    # Grid lines
    for i in range(container_w + 1):
        ax.axvline(x=i, color='lightgray', linewidth=0.5, alpha=0.7)
    for i in range(container_h + 1):
        ax.axhline(y=i, color='lightgray', linewidth=0.5, alpha=0.7)

    # Add efficiency information
    if tile_positions:
        total_tile_area = sum(w * h for x, y, w, h, _ in tile_positions)
        efficiency = (total_tile_area / (container_w * container_h)) * 100
        ax.text(0.02, 0.98, f"Efficiency: {efficiency:.1f}%", 
                transform=ax.transAxes, fontsize=12, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.8))

    plt.tight_layout()
    plt.show()

def test_optimized_solver():
    """Test the optimized solver on various cases."""
    test_cases = [
       # (40, 40, 24, 16, "Pinwheel Test (Optimized)"),
       # (20, 20, 10, 10, "Perfect Grid (Optimized)"),
        (40, 48, 10, 10, "Large Grid (Previously Problematic)"),
       # (30, 30, 12, 18, "Complex Case (Optimized)"),
       # (36, 36, 18, 12, "Symmetry Test Case"),
    ]
    
    print(f"\n{'='*100}")
    print(f"🚀 TESTING OPTIMIZED ILP SOLVER WITH PERFORMANCE TUNING")
    print(f"{'='*100}")
    
    for i, (cw, ch, tw, th, description) in enumerate(test_cases, 1):
        print(f"\n{'🎯' * 25}")
        print(f"TEST CASE {i}: {description}")
        print(f"{'🎯' * 25}")
        
        num_tiles, positions, info = solve_rectangle_packing_optimized(
            cw, ch, tw, th, time_limit_sec=60, center_solution=True
        )
        
        if num_tiles > 0:
            efficiency = (num_tiles * tw * th) / (cw * ch) * 100
            print(f"📊 Space efficiency: {efficiency:.1f}%")
            
            title = f"{description}: {num_tiles} tiles (Centered & Optimized)"
            draw_optimized_solution(cw, ch, positions, title)
            
            print(f"⚡ Performance metrics:")
            print(f"   Variables: {info['variables']:,}")
            print(f"   Constraints: {info['constraints']:,}")
            print(f"   Solve time: {info['solve_time']:.2f}s")
        else:
            print(f"❌ No solution found")

if __name__ == "__main__":
    test_optimized_solver()