"""
Solution validation and feasibility checking utilities.
"""

from typing import List, Set, Tuple, Optional
from ..core.solution import PackingSolution, TilePosition
from ..core.problem import PackingProblem

def validate_solution(solution: PackingSolution, problem: PackingProblem) -> Tuple[bool, List[str]]:
    """
    Validate a packing solution for correctness.
    
    Returns:
        (is_valid, error_messages): Tuple of validation result and any error messages
    """
    errors = []
    
    # Check container dimensions match
    if (solution.container_w != problem.container_w or 
        solution.container_h != problem.container_h):
        errors.append(f"Container dimensions mismatch: solution has {solution.container_w}×{solution.container_h}, "
                     f"problem expects {problem.container_w}×{problem.container_h}")
    
    # Check each tile position
    for i, (x, y, w, h, orientation) in enumerate(solution.tile_positions):
        # Check bounds
        if x < 0 or y < 0:
            errors.append(f"Tile {i+1} has negative coordinates: ({x}, {y})")
        
        if x + w > problem.container_w:
            errors.append(f"Tile {i+1} extends beyond container width: x={x}, w={w}, container_w={problem.container_w}")
        
        if y + h > problem.container_h:
            errors.append(f"Tile {i+1} extends beyond container height: y={y}, h={h}, container_h={problem.container_h}")
        
        # Check dimensions are positive
        if w <= 0 or h <= 0:
            errors.append(f"Tile {i+1} has invalid dimensions: {w}×{h}")
        
        # Check dimensions match problem tile dimensions
        valid_dims = [(problem.tile_w, problem.tile_h)]
        if problem.allow_rotation:
            valid_dims.append((problem.tile_h, problem.tile_w))
        
        if (w, h) not in valid_dims:
            errors.append(f"Tile {i+1} has incorrect dimensions: {w}×{h}, expected {problem.tile_w}×{problem.tile_h}")
        
        # Check orientation consistency
        if orientation not in ["original", "rotated"]:
            errors.append(f"Tile {i+1} has invalid orientation: {orientation}")
        
        if orientation == "rotated" and not problem.allow_rotation:
            errors.append(f"Tile {i+1} is rotated but rotation not allowed")
        
        if orientation == "rotated" and (w, h) != (problem.tile_h, problem.tile_w):
            errors.append(f"Tile {i+1} marked as rotated but dimensions don't match: {w}×{h}")
        
        if orientation == "original" and (w, h) != (problem.tile_w, problem.tile_h):
            errors.append(f"Tile {i+1} marked as original but dimensions don't match: {w}×{h}")
    
    # Check for overlaps
    overlap_errors = check_overlaps(solution.tile_positions)
    errors.extend(overlap_errors)
    
    # Check tile count constraint
    if problem.max_tiles is not None and solution.num_tiles > problem.max_tiles:
        errors.append(f"Too many tiles: {solution.num_tiles} > {problem.max_tiles}")
    
    return len(errors) == 0, errors

def check_overlaps(positions: List[TilePosition]) -> List[str]:
    """Check for overlapping tiles and return error messages."""
    errors = []
    
    for i, (x1, y1, w1, h1, _) in enumerate(positions):
        for j, (x2, y2, w2, h2, _) in enumerate(positions[i+1:], i+1):
            if rectangles_overlap(x1, y1, w1, h1, x2, y2, w2, h2):
                errors.append(f"Tiles {i+1} and {j+1} overlap: "
                             f"({x1},{y1},{w1},{h1}) and ({x2},{y2},{w2},{h2})")
    
    return errors

def rectangles_overlap(x1: int, y1: int, w1: int, h1: int, 
                      x2: int, y2: int, w2: int, h2: int) -> bool:
    """Check if two rectangles overlap."""
    return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)

def check_feasibility(problem: PackingProblem) -> Tuple[bool, List[str]]:
    """
    Check if a packing problem is feasible.
    
    Returns:
        (is_feasible, warnings): Tuple of feasibility and any warnings
    """
    warnings = []
    
    # Basic feasibility: can at least one tile fit?
    orientations = [(problem.tile_w, problem.tile_h)]
    if problem.allow_rotation:
        orientations.append((problem.tile_h, problem.tile_w))
    
    can_fit_one = any(w <= problem.container_w and h <= problem.container_h 
                     for w, h in orientations)
    
    if not can_fit_one:
        return False, ["No tile can fit in the container with any orientation"]
    
    # Check theoretical maximum
    theoretical_max = problem.theoretical_max_tiles
    if problem.max_tiles is not None and problem.max_tiles > theoretical_max:
        warnings.append(f"Requested max_tiles ({problem.max_tiles}) exceeds theoretical maximum ({theoretical_max})")
    
    # Check for very low efficiency scenarios
    if theoretical_max < 2:
        warnings.append("Very low packing density possible - consider adjusting dimensions")
    
    # Check for problematic aspect ratios
    container_ratio = problem.container_w / problem.container_h
    tile_ratio = problem.tile_w / problem.tile_h
    
    if abs(container_ratio - tile_ratio) > 3:
        warnings.append("Large aspect ratio difference between container and tiles may result in poor packing")
    
    return True, warnings

def get_solution_quality_metrics(solution: PackingSolution, problem: PackingProblem) -> dict:
    """Calculate various quality metrics for a solution."""
    metrics = {}
    
    # Basic metrics
    metrics['num_tiles'] = solution.num_tiles
    metrics['efficiency'] = solution.efficiency
    metrics['solve_time'] = solution.solve_time
    
    # Area utilization
    total_tile_area = solution.num_tiles * problem.tile_area
    metrics['area_utilization'] = total_tile_area / problem.container_area
    
    # Compactness metrics
    if solution.tile_positions:
        min_x = min(x for x, _, _, _, _ in solution.tile_positions)
        min_y = min(y for _, y, _, _, _ in solution.tile_positions)
        max_x = max(x + w for x, _, w, _, _ in solution.tile_positions)
        max_y = max(y + h for _, y, _, h, _ in solution.tile_positions)
        
        used_w = max_x - min_x
        used_h = max_y - min_y
        bounding_box_area = used_w * used_h
        
        metrics['bounding_box_efficiency'] = total_tile_area / bounding_box_area if bounding_box_area > 0 else 0
        metrics['aspect_ratio'] = used_w / used_h if used_h > 0 else float('inf')
        
        # Centering metrics
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        container_center_x = problem.container_w / 2
        container_center_y = problem.container_h / 2
        
        metrics['center_deviation'] = ((center_x - container_center_x)**2 + (center_y - container_center_y)**2)**0.5
        metrics['is_centered'] = solution.is_centered
    else:
        metrics['bounding_box_efficiency'] = 0
        metrics['aspect_ratio'] = 0
        metrics['center_deviation'] = 0
        metrics['is_centered'] = True
    
    # Performance relative to theoretical maximum
    metrics['optimality_ratio'] = solution.num_tiles / problem.theoretical_max_tiles
    
    return metrics

def compare_solutions(solutions: List[PackingSolution], problem: PackingProblem) -> dict:
    """Compare multiple solutions and provide analysis."""
    if not solutions:
        return {'error': 'No solutions to compare'}
    
    analysis = {}
    
    # Basic statistics
    tile_counts = [sol.num_tiles for sol in solutions]
    efficiencies = [sol.efficiency for sol in solutions]
    solve_times = [sol.solve_time for sol in solutions]
    
    analysis['num_solutions'] = len(solutions)
    analysis['tile_count_range'] = (min(tile_counts), max(tile_counts))
    analysis['efficiency_range'] = (min(efficiencies), max(efficiencies))
    analysis['avg_solve_time'] = sum(solve_times) / len(solve_times)
    
    # Best solution analysis
    best_solution = max(solutions, key=lambda s: s.num_tiles)
    analysis['best_solution'] = {
        'tiles': best_solution.num_tiles,
        'efficiency': best_solution.efficiency,
        'solver': best_solution.solver_name,
        'solve_time': best_solution.solve_time
    }
    
    # Solution diversity
    unique_tile_counts = len(set(tile_counts))
    analysis['solution_diversity'] = unique_tile_counts / len(solutions)
    
    return analysis
