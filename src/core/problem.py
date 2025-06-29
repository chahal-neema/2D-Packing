"""
Problem definition and data structures for rectangle packing.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class PackingProblem:
    """Defines a 2D rectangle packing problem."""
    
    container_w: int
    container_h: int
    tile_w: int  
    tile_h: int
    max_tiles: Optional[int] = None
    allow_rotation: bool = True
    require_centering: bool = True
    
    def __post_init__(self):
        """Validate problem parameters."""
        if self.container_w <= 0 or self.container_h <= 0:
            raise ValueError("Container dimensions must be positive")
        if self.tile_w <= 0 or self.tile_h <= 0:
            raise ValueError("Tile dimensions must be positive")
        if self.tile_w > self.container_w or self.tile_h > self.container_h:
            raise ValueError("Tile cannot fit in container")
    
    @property
    def container_area(self) -> int:
        """Total container area."""
        return self.container_w * self.container_h
    
    @property 
    def tile_area(self) -> int:
        """Area of a single tile."""
        return self.tile_w * self.tile_h
        
    @property
    def theoretical_max_tiles(self) -> int:
        """Theoretical maximum number of tiles based on area."""
        return self.container_area // self.tile_area
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'container_w': self.container_w,
            'container_h': self.container_h,
            'tile_w': self.tile_w,
            'tile_h': self.tile_h,
            'max_tiles': self.max_tiles,
            'allow_rotation': self.allow_rotation,
            'require_centering': self.require_centering
        }
