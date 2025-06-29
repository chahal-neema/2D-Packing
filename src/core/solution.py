"""
Solution representation and utilities for rectangle packing.
"""

from dataclasses import dataclass
from typing import List, Tuple, Dict, Any, Optional
import time

# Type alias for tile position: (x, y, width, height, orientation)
TilePosition = Tuple[int, int, int, int, str]

@dataclass
class PackingSolution:
    """Represents a solution to a rectangle packing problem."""
    
    tile_positions: List[TilePosition]
    container_w: int
    container_h: int
    solve_time: float = 0.0
    solver_name: str = "unknown"
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize computed properties."""
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def num_tiles(self) -> int:
        """Number of tiles placed."""
        return len(self.tile_positions)
    
    @property 
    def efficiency(self) -> float:
        """Packing efficiency as percentage."""
        if self.num_tiles == 0:
            return 0.0
        total_tile_area = sum(w * h for _, _, w, h, _ in self.tile_positions)
        container_area = self.container_w * self.container_h
        return (total_tile_area / container_area) * 100
    
    @property
    def bounding_box(self) -> Tuple[int, int, int, int]:
        """Bounding box of all placed tiles: (min_x, min_y, max_x, max_y)."""
        if not self.tile_positions:
            return (0, 0, 0, 0)
        
        min_x = min(x for x, _, _, _, _ in self.tile_positions)
        min_y = min(y for _, y, _, _, _ in self.tile_positions)
        max_x = max(x + w for x, _, w, _, _ in self.tile_positions)
        max_y = max(y + h for _, y, _, h, _ in self.tile_positions)
        
        return (min_x, min_y, max_x, max_y)
    
    @property
    def is_centered(self) -> bool:
        """Check if solution is approximately centered."""
        if not self.tile_positions:
            return True
            
        min_x, min_y, max_x, max_y = self.bounding_box
        used_w = max_x - min_x
        used_h = max_y - min_y
        
        expected_offset_x = (self.container_w - used_w) // 2
        expected_offset_y = (self.container_h - used_h) // 2
        
        # Allow small tolerance for centering
        tolerance = 1
        return (abs(min_x - expected_offset_x) <= tolerance and 
                abs(min_y - expected_offset_y) <= tolerance)
    
    def get_tile_at_position(self, x: int, y: int) -> Optional[int]:
        """Get tile index at given position, or None if empty."""
        for i, (tx, ty, tw, th, _) in enumerate(self.tile_positions):
            if tx <= x < tx + tw and ty <= y < ty + th:
                return i
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert solution to dictionary representation."""
        return {
            'tile_positions': self.tile_positions,
            'container_w': self.container_w,
            'container_h': self.container_h,
            'num_tiles': self.num_tiles,
            'efficiency': self.efficiency,
            'solve_time': self.solve_time,
            'solver_name': self.solver_name,
            'metadata': self.metadata
        }
