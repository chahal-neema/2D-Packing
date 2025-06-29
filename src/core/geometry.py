"""
Geometric operations for rectangle packing (rotations, translations, etc.).
"""

from typing import List, Tuple
from ..core.solution import TilePosition

def rotate_point_90(x: int, y: int, container_w: int, container_h: int) -> Tuple[int, int]:
    """Rotate a point 90 degrees clockwise around container center."""
    return (container_h - 1 - y, x)

def rotate_point_180(x: int, y: int, container_w: int, container_h: int) -> Tuple[int, int]:
    """Rotate a point 180 degrees around container center.""" 
    return (container_w - 1 - x, container_h - 1 - y)

def rotate_point_270(x: int, y: int, container_w: int, container_h: int) -> Tuple[int, int]:
    """Rotate a point 270 degrees clockwise around container center."""
    return (y, container_w - 1 - x)

def mirror_point_horizontal(x: int, y: int, container_w: int, container_h: int) -> Tuple[int, int]:
    """Mirror a point horizontally."""
    return (container_w - 1 - x, y)

def mirror_point_vertical(x: int, y: int, container_w: int, container_h: int) -> Tuple[int, int]:
    """Mirror a point vertically."""
    return (x, container_h - 1 - y)

def rotate_tile_90(tile: TilePosition, container_w: int, container_h: int) -> TilePosition:
    """Rotate a tile 90 degrees clockwise."""
    x, y, w, h, orientation = tile
    new_x, new_y = rotate_point_90(x + w - 1, y, container_w, container_h)
    new_x = new_x - h + 1
    return (new_x, new_y, h, w, orientation)

def rotate_tile_180(tile: TilePosition, container_w: int, container_h: int) -> TilePosition:
    """Rotate a tile 180 degrees."""
    x, y, w, h, orientation = tile
    new_x, new_y = rotate_point_180(x + w - 1, y + h - 1, container_w, container_h)
    new_x = new_x - w + 1
    new_y = new_y - h + 1
    return (new_x, new_y, w, h, orientation)

def rotate_tile_270(tile: TilePosition, container_w: int, container_h: int) -> TilePosition:
    """Rotate a tile 270 degrees clockwise."""
    x, y, w, h, orientation = tile
    new_x, new_y = rotate_point_270(x, y + h - 1, container_w, container_h)
    new_y = new_y - w + 1  
    return (new_x, new_y, h, w, orientation)

def rotate_solution_90(positions: List[TilePosition], container_w: int, container_h: int) -> List[TilePosition]:
    """Rotate an entire solution 90 degrees clockwise."""
    return [rotate_tile_90(tile, container_w, container_h) for tile in positions]

def rotate_solution_180(positions: List[TilePosition], container_w: int, container_h: int) -> List[TilePosition]:
    """Rotate an entire solution 180 degrees."""
    return [rotate_tile_180(tile, container_w, container_h) for tile in positions]

def rotate_solution_270(positions: List[TilePosition], container_w: int, container_h: int) -> List[TilePosition]:
    """Rotate an entire solution 270 degrees clockwise.""" 
    return [rotate_tile_270(tile, container_w, container_h) for tile in positions]

def translate_solution(positions: List[TilePosition], offset_x: int, offset_y: int) -> List[TilePosition]:
    """Translate all tiles by given offset."""
    return [(x + offset_x, y + offset_y, w, h, orientation) 
            for x, y, w, h, orientation in positions]

def center_solution(positions: List[TilePosition], container_w: int, container_h: int) -> List[TilePosition]:
    """Center a solution in the container."""
    if not positions:
        return positions
    
    # Find bounding box
    min_x = min(x for x, _, _, _, _ in positions)
    min_y = min(y for _, y, _, _, _ in positions)
    max_x = max(x + w for x, _, w, _, _ in positions)
    max_y = max(y + h for _, y, _, h, _ in positions)
    
    # Calculate centering offset
    used_w = max_x - min_x
    used_h = max_y - min_y
    offset_x = (container_w - used_w) // 2 - min_x
    offset_y = (container_h - used_h) // 2 - min_y
    
    return translate_solution(positions, offset_x, offset_y)

def calculate_bounding_box(positions: List[TilePosition]) -> Tuple[int, int, int, int]:
    """Calculate bounding box of tile positions."""
    if not positions:
        return (0, 0, 0, 0)
    
    min_x = min(x for x, _, _, _, _ in positions)
    min_y = min(y for _, y, _, _, _ in positions)
    max_x = max(x + w for x, _, w, _, _ in positions)
    max_y = max(y + h for _, y, _, h, _ in positions)
    
    return (min_x, min_y, max_x, max_y)
