"""
Configuration parameters for all solvers and algorithms.
"""

class SolverConfig:
    """Configuration settings for all solvers."""
    
    # General settings
    DEFAULT_TIME_LIMIT = 60  # seconds
    DEFAULT_MAX_SOLUTIONS = 10
    
    # ILP Solver settings
    ILP_TIME_LIMIT = 60
    ILP_COMPACTNESS_WEIGHT = 0.1
    
    # Backtracking settings
    BACKTRACK_MAX_SOLUTIONS = 50
    BACKTRACK_TIME_LIMIT = 30
    
    # Greedy solver settings
    GREEDY_STRATEGY = "bottom_left"  # Options: "bottom_left", "center_out"
    
    # Symmetry settings
    ENABLE_SYMMETRY_BREAKING = True
    ENABLE_ROTATION_DETECTION = True
    
    # Visualization settings
    FIGURE_SIZE = (12, 10)
    DPI = 100
    SHOW_TILE_LABELS = True
    ALPHA = 0.7

class ProblemConfig:
    """Configuration for problem constraints."""
    
    ALLOW_ROTATION = True
    REQUIRE_CENTER_ALIGNMENT = True
    ELIMINATE_DUPLICATES = True
