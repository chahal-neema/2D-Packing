"""
Matplotlib-based visualization for rectangle packing solutions.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from typing import List, Optional, Tuple
from ..core.solution import PackingSolution
from ..core.problem import PackingProblem
from ...config.solver_config import SolverConfig

def visualize_solution(solution: PackingSolution, problem: PackingProblem = None, 
                      title: str = None, show_grid: bool = True, 
                      show_labels: bool = True, figsize: Tuple[int, int] = None) -> plt.Figure:
    """
    Visualize a single packing solution.
    
    Args:
        solution: The packing solution to visualize
        problem: Optional problem for additional context
        title: Custom title for the plot
        show_grid: Whether to show grid lines
        show_labels: Whether to show tile labels
        figsize: Figure size (width, height)
    
    Returns:
        matplotlib Figure object
    """
    if figsize is None:
        figsize = SolverConfig.FIGURE_SIZE
    
    fig, ax = plt.subplots(1, 1, figsize=figsize, dpi=SolverConfig.DPI)
    
    # Draw container boundary
    container_rect = patches.Rectangle(
        (0, 0), solution.container_w, solution.container_h,
        linewidth=2, edgecolor='black', facecolor='none'
    )
    ax.add_patch(container_rect)
    
    # Generate colors for tiles
    if solution.tile_positions:
        colors = plt.cm.Set3(np.linspace(0, 1, len(solution.tile_positions)))
    else:
        colors = []
    
    # Draw tiles
    for i, (x, y, w, h, orientation) in enumerate(solution.tile_positions):
        tile_rect = patches.Rectangle(
            (x, y), w, h,
            linewidth=1, edgecolor='black', 
            facecolor=colors[i], alpha=SolverConfig.ALPHA
        )
        ax.add_patch(tile_rect)
        
        # Add tile label
        if show_labels and SolverConfig.SHOW_TILE_LABELS:
            ax.text(x + w/2, y + h/2, f'T{i+1}', 
                   ha='center', va='center', fontweight='bold', fontsize=10)
            
            # Add orientation indicator for rotated tiles
            if orientation == "rotated":
                ax.text(x + w - 2, y + 2, '↻', 
                       ha='right', va='bottom', fontsize=8, color='red')
    
    # Set up the plot
    ax.set_xlim(-1, solution.container_w + 1)
    ax.set_ylim(-1, solution.container_h + 1)
    ax.set_aspect('equal')
    
    if show_grid:
        ax.grid(True, alpha=0.3)
    
    # Create title
    if title is None:
        efficiency_text = f"{solution.efficiency:.1f}%" if solution.num_tiles > 0 else "0%"
        title = f"{solution.num_tiles} tiles (Efficiency: {efficiency_text})"
        if solution.solver_name != "unknown":
            title += f" - {solution.solver_name}"
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    
    plt.tight_layout()
    return fig

def visualize_multiple_solutions(solutions: List[PackingSolution], 
                                problem: PackingProblem = None,
                                max_cols: int = 3, 
                                figsize: Tuple[int, int] = None) -> plt.Figure:
    """
    Visualize multiple solutions in a grid layout.
    
    Args:
        solutions: List of solutions to visualize
        problem: Optional problem for context
        max_cols: Maximum number of columns in the grid
        figsize: Figure size (width, height)
    
    Returns:
        matplotlib Figure object
    """
    if not solutions:
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        ax.text(0.5, 0.5, 'No solutions to display', 
                ha='center', va='center', fontsize=16)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        return fig
    
    # Calculate grid dimensions
    n_solutions = len(solutions)
    n_cols = min(max_cols, n_solutions)
    n_rows = (n_solutions + n_cols - 1) // n_cols
    
    if figsize is None:
        figsize = (4 * n_cols, 4 * n_rows)
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize, 
                            dpi=SolverConfig.DPI)
    
    # Handle single subplot case
    if n_solutions == 1:
        axes = [axes]
    elif n_rows == 1:
        axes = axes.reshape(1, -1)
    
    # Plot each solution
    for i, solution in enumerate(solutions):
        row = i // n_cols
        col = i % n_cols
        ax = axes[row][col] if n_rows > 1 else axes[col]
        
        _plot_solution_on_axis(ax, solution, f"Solution {i+1}")
    
    # Hide unused subplots
    for i in range(n_solutions, n_rows * n_cols):
        row = i // n_cols
        col = i % n_cols
        ax = axes[row][col] if n_rows > 1 else axes[col]
        ax.set_visible(False)
    
    plt.tight_layout()
    return fig

def compare_solutions(solutions: List[PackingSolution], 
                     labels: List[str] = None,
                     problem: PackingProblem = None) -> plt.Figure:
    """
    Create a comparison visualization of multiple solutions.
    
    Args:
        solutions: List of solutions to compare
        labels: Optional labels for each solution
        problem: Optional problem for context
    
    Returns:
        matplotlib Figure object with comparison plots
    """
    if not solutions:
        return plt.figure()
    
    # Create subplots: solutions on top, metrics on bottom
    n_solutions = len(solutions)
    fig = plt.figure(figsize=(4 * n_solutions, 10))
    
    # Top row: solution visualizations
    for i, solution in enumerate(solutions):
        ax = plt.subplot(2, n_solutions, i + 1)
        label = labels[i] if labels and i < len(labels) else f"Solution {i+1}"
        _plot_solution_on_axis(ax, solution, label)
    
    # Bottom row: metrics comparison
    ax_metrics = plt.subplot(2, 1, 2)
    _plot_solution_metrics(ax_metrics, solutions, labels)
    
    plt.tight_layout()
    return fig

def visualize_solution_evolution(solutions: List[PackingSolution], 
                               titles: List[str] = None) -> plt.Figure:
    """
    Visualize the evolution of solutions (e.g., from different algorithm stages).
    
    Args:
        solutions: List of solutions showing evolution
        titles: Optional titles for each stage
    
    Returns:
        matplotlib Figure object
    """
    return visualize_multiple_solutions(solutions, max_cols=len(solutions), 
                                      figsize=(3 * len(solutions), 4))

def save_visualization(fig: plt.Figure, filename: str, format: str = 'png', 
                      dpi: int = 300, bbox_inches: str = 'tight'):
    """
    Save a visualization to file.
    
    Args:
        fig: matplotlib Figure to save
        filename: Output filename
        format: Image format ('png', 'pdf', 'svg', etc.)
        dpi: Resolution for raster formats
        bbox_inches: Bounding box setting
    """
    fig.savefig(filename, format=format, dpi=dpi, bbox_inches=bbox_inches)
    print(f"💾 Saved visualization to {filename}")

def _plot_solution_on_axis(ax, solution: PackingSolution, title: str):
    """Helper function to plot a solution on a given axis."""
    # Draw container
    container_rect = patches.Rectangle(
        (0, 0), solution.container_w, solution.container_h,
        linewidth=2, edgecolor='black', facecolor='none'
    )
    ax.add_patch(container_rect)
    
    # Draw tiles
    if solution.tile_positions:
        colors = plt.cm.Set3(np.linspace(0, 1, len(solution.tile_positions)))
        
        for i, (x, y, w, h, orientation) in enumerate(solution.tile_positions):
            tile_rect = patches.Rectangle(
                (x, y), w, h,
                linewidth=1, edgecolor='black',
                facecolor=colors[i], alpha=SolverConfig.ALPHA
            )
            ax.add_patch(tile_rect)
            
            # Add tile number
            if SolverConfig.SHOW_TILE_LABELS:
                ax.text(x + w/2, y + h/2, str(i+1), 
                       ha='center', va='center', fontweight='bold', fontsize=8)
    
    # Format axis
    ax.set_xlim(-0.5, solution.container_w + 0.5)
    ax.set_ylim(-0.5, solution.container_h + 0.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    # Title with metrics
    efficiency = f"{solution.efficiency:.1f}%" if solution.num_tiles > 0 else "0%"
    full_title = f"{title}\n{solution.num_tiles} tiles ({efficiency})"
    ax.set_title(full_title, fontsize=10, fontweight='bold')

def _plot_solution_metrics(ax, solutions: List[PackingSolution], labels: List[str] = None):
    """Helper function to plot solution metrics comparison."""
    if not solutions:
        return
    
    metrics = {
        'Tiles': [s.num_tiles for s in solutions],
        'Efficiency (%)': [s.efficiency for s in solutions],
        'Solve Time (s)': [s.solve_time for s in solutions]
    }
    
    x_labels = labels if labels else [f"Sol {i+1}" for i in range(len(solutions))]
    x_pos = np.arange(len(solutions))
    
    # Create grouped bar chart
    width = 0.25
    multiplier = 0
    
    for metric_name, values in metrics.items():
        offset = width * multiplier
        bars = ax.bar(x_pos + offset, values, width, label=metric_name)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{value:.1f}', ha='center', va='bottom', fontsize=8)
        
        multiplier += 1
    
    ax.set_xlabel('Solutions')
    ax.set_ylabel('Value')
    ax.set_title('Solution Metrics Comparison')
    ax.set_xticks(x_pos + width)
    ax.set_xticklabels(x_labels)
    ax.legend()
    ax.grid(True, alpha=0.3)

# Convenience functions
def quick_plot(solution: PackingSolution, save_path: str = None) -> plt.Figure:
    """Quickly plot a solution with minimal configuration."""
    fig = visualize_solution(solution)
    if save_path:
        save_visualization(fig, save_path)
    plt.show()
    return fig

def plot_comparison(solutions: List[PackingSolution], 
                   solver_names: List[str] = None) -> plt.Figure:
    """Quickly compare multiple solutions."""
    labels = solver_names or [s.solver_name for s in solutions]
    fig = compare_solutions(solutions, labels)
    plt.show()
    return fig
