"""
Symmetry detection and canonical form generation for eliminating duplicate solutions.
"""

from typing import List, Set, Tuple
from ..core.solution import PackingSolution, TilePosition
from ..core.problem import PackingProblem
from ..core.geometry import (
    rotate_solution_90, rotate_solution_180, rotate_solution_270,
    center_solution
)

def get_canonical_form(positions: List[TilePosition], container_w: int, container_h: int) -> Tuple[TilePosition, ...]:
    """
    Convert a solution to its canonical form to detect duplicates.
    Returns the lexicographically smallest representation among all symmetries.
    """
    if not positions:
        return tuple()
    
    # Generate all 8 possible symmetries (4 rotations × 2 mirrors)
    transforms = []
    
    # Original and rotations
    transforms.append(positions)
    transforms.append(rotate_solution_90(positions, container_w, container_h))
    transforms.append(rotate_solution_180(positions, container_w, container_h))
    transforms.append(rotate_solution_270(positions, container_w, container_h))
    
    # Mirrored versions (horizontal flip of each rotation)
    for transform in transforms[:4]:  # Only original 4 rotations
        mirrored = mirror_solution_horizontal(transform, container_w)
        transforms.append(mirrored)
    
    # Convert each transform to a sortable form and find minimum
    canonical_forms = []
    for transform in transforms:
        # Sort tiles by position for consistent representation
        sorted_tiles = sorted(transform, key=lambda t: (t[1], t[0], t[2], t[3]))  # Sort by y, x, w, h
        canonical_forms.append(tuple(sorted_tiles))
    
    # Return lexicographically smallest form
    return min(canonical_forms)

def mirror_solution_horizontal(positions: List[TilePosition], container_w: int) -> List[TilePosition]:
    """Mirror solution horizontally (flip left-right)."""
    mirrored = []
    for x, y, w, h, orientation in positions:
        new_x = container_w - x - w
        mirrored.append((new_x, y, w, h, orientation))
    return mirrored

def mirror_solution_vertical(positions: List[TilePosition], container_h: int) -> List[TilePosition]:
    """Mirror solution vertically (flip top-bottom)."""
    mirrored = []
    for x, y, w, h, orientation in positions:
        new_y = container_h - y - h
        mirrored.append((x, new_y, w, h, orientation))
    return mirrored

def are_solutions_equivalent(sol1: PackingSolution, sol2: PackingSolution) -> bool:
    """Check if two solutions are equivalent under symmetry transformations."""
    if sol1.num_tiles != sol2.num_tiles:
        return False
    
    if sol1.container_w != sol2.container_w or sol1.container_h != sol2.container_h:
        return False
    
    canonical1 = get_canonical_form(sol1.tile_positions, sol1.container_w, sol1.container_h)
    canonical2 = get_canonical_form(sol2.tile_positions, sol2.container_w, sol2.container_h)
    
    return canonical1 == canonical2

def deduplicate_solutions(solutions: List[PackingSolution], problem: PackingProblem) -> List[PackingSolution]:
    """
    Remove duplicate solutions that are equivalent under symmetry.
    Returns a list of unique solutions.
    """
    if not solutions:
        return solutions
    
    unique_solutions = []
    seen_canonical_forms = set()
    
    for solution in solutions:
        canonical_form = get_canonical_form(
            solution.tile_positions, 
            problem.container_w, 
            problem.container_h
        )
        
        if canonical_form not in seen_canonical_forms:
            seen_canonical_forms.add(canonical_form)
            unique_solutions.append(solution)
    
    return unique_solutions

def detect_symmetry_type(positions: List[TilePosition], container_w: int, container_h: int) -> List[str]:
    """
    Detect what types of symmetry a solution has.
    Returns a list of symmetry types: ['rotational_90', 'rotational_180', 'mirror_horizontal', etc.]
    """
    symmetries = []
    
    # Check rotational symmetries
    rotated_90 = rotate_solution_90(positions, container_w, container_h)
    if _positions_equivalent(positions, rotated_90):
        symmetries.append('rotational_90')
    
    rotated_180 = rotate_solution_180(positions, container_w, container_h)
    if _positions_equivalent(positions, rotated_180):
        symmetries.append('rotational_180')
    
    rotated_270 = rotate_solution_270(positions, container_w, container_h)
    if _positions_equivalent(positions, rotated_270):
        symmetries.append('rotational_270')
    
    # Check mirror symmetries
    mirrored_h = mirror_solution_horizontal(positions, container_w)
    if _positions_equivalent(positions, mirrored_h):
        symmetries.append('mirror_horizontal')
    
    mirrored_v = mirror_solution_vertical(positions, container_h)
    if _positions_equivalent(positions, mirrored_v):
        symmetries.append('mirror_vertical')
    
    return symmetries

def _positions_equivalent(pos1: List[TilePosition], pos2: List[TilePosition]) -> bool:
    """Check if two position lists represent the same arrangement."""
    if len(pos1) != len(pos2):
        return False
    
    # Sort both lists for comparison
    sorted_pos1 = sorted(pos1, key=lambda t: (t[1], t[0], t[2], t[3]))
    sorted_pos2 = sorted(pos2, key=lambda t: (t[1], t[0], t[2], t[3]))
    
    return sorted_pos1 == sorted_pos2

def get_preferred_orientation(solutions: List[PackingSolution], problem: PackingProblem) -> List[PackingSolution]:
    """
    For solutions that are equivalent under rotation, choose the preferred orientation.
    Preference: wider arrangements over taller ones for landscape containers.
    """
    if not solutions:
        return solutions
    
    oriented_solutions = []
    
    for solution in solutions:
        # Check all 4 rotations and pick the most aesthetically pleasing
        rotations = [
            solution.tile_positions,
            rotate_solution_90(solution.tile_positions, problem.container_w, problem.container_h),
            rotate_solution_180(solution.tile_positions, problem.container_w, problem.container_h),
            rotate_solution_270(solution.tile_positions, problem.container_w, problem.container_h)
        ]
        
        best_rotation = rotations[0]
        best_score = _aesthetic_score(rotations[0], problem)
        
        for rotation in rotations[1:]:
            score = _aesthetic_score(rotation, problem)
            if score > best_score:
                best_score = score
                best_rotation = rotation
        
        # Create new solution with preferred orientation
        oriented_solution = PackingSolution(
            tile_positions=best_rotation,
            container_w=problem.container_w,
            container_h=problem.container_h,
            solve_time=solution.solve_time,
            solver_name=solution.solver_name,
            metadata=solution.metadata
        )
        oriented_solutions.append(oriented_solution)
    
    return oriented_solutions

def _aesthetic_score(positions: List[TilePosition], problem: PackingProblem) -> float:
    """
    Calculate aesthetic score for a solution orientation.
    Higher scores are preferred.
    """
    if not positions:
        return 0.0
    
    # Calculate bounding box
    min_x = min(x for x, _, _, _, _ in positions)
    min_y = min(y for _, y, _, _, _ in positions)
    max_x = max(x + w for x, _, w, _, _ in positions)
    max_y = max(y + h for _, y, _, h, _ in positions)
    
    used_w = max_x - min_x
    used_h = max_y - min_y
    
    score = 0.0
    
    # Prefer arrangements that match container aspect ratio
    container_ratio = problem.container_w / problem.container_h
    used_ratio = used_w / used_h if used_h > 0 else 1.0
    ratio_score = 1.0 / (1.0 + abs(container_ratio - used_ratio))
    score += ratio_score * 100
    
    # Prefer more compact arrangements (less perimeter for same area)
    perimeter = 2 * (used_w + used_h)
    area = used_w * used_h
    compactness = area / perimeter if perimeter > 0 else 0
    score += compactness * 10
    
    # Prefer centered arrangements
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    container_center_x = problem.container_w / 2
    container_center_y = problem.container_h / 2
    center_distance = abs(center_x - container_center_x) + abs(center_y - container_center_y)
    centering_score = 1.0 / (1.0 + center_distance)
    score += centering_score * 50
    
    return score
