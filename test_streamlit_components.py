#!/usr/bin/env python3
"""
Test the core components of the Streamlit app without running Streamlit
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import io
from contextlib import redirect_stdout, redirect_stderr

from src.core.problem import PackingProblem
from src.solvers.hybrid_solver import HybridSolver

def create_enhanced_visualization(solution, problem):
    """Create an enhanced visualization of the packing solution."""
    fig, ax = plt.subplots(1, 1, figsize=(12, 10), dpi=100)
    
    # Draw container boundary with thick border
    container_rect = patches.Rectangle(
        (0, 0), solution.container_w, solution.container_h,
        linewidth=3, edgecolor='#2c3e50', facecolor='#ecf0f1', alpha=0.3
    )
    ax.add_patch(container_rect)
    
    # Generate distinct colors for tiles
    if solution.tile_positions:
        colors = plt.cm.Set1(np.linspace(0, 1, len(solution.tile_positions)))
    else:
        colors = []
    
    # Draw tiles with enhanced styling
    for i, (x, y, w, h, orientation) in enumerate(solution.tile_positions):
        # Main tile rectangle
        tile_rect = patches.Rectangle(
            (x, y), w, h,
            linewidth=2, edgecolor='#2c3e50', 
            facecolor=colors[i], alpha=0.8
        )
        ax.add_patch(tile_rect)
        
        # Add tile label with better styling
        ax.text(x + w/2, y + h/2, f'T{i+1}', 
                ha='center', va='center', fontweight='bold', 
                fontsize=12, color='white', 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))
                
        # Add orientation indicator for rotated tiles
        if orientation == "rotated":
            ax.text(x + w - 3, y + h - 3, '↻', 
                    ha='right', va='top', fontsize=16, color='red', fontweight='bold')
    
    # Enhanced plot formatting
    ax.set_xlim(-2, solution.container_w + 2)
    ax.set_ylim(-2, solution.container_h + 2)
    ax.set_aspect('equal')
    
    # Custom grid
    ax.grid(True, alpha=0.4, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)
    
    # Title and labels
    efficiency_text = f"{solution.efficiency:.1f}%" if solution.num_tiles > 0 else "0%"
    title = f"📦 Packing Solution: {solution.num_tiles} tiles (Efficiency: {efficiency_text})"
    if solution.solver_name != "unknown":
        title += f"\n🔧 Solver: {solution.solver_name}"
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('X Position', fontsize=12, fontweight='bold')
    ax.set_ylabel('Y Position', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    return fig

def capture_solver_output(solver, problem):
    """Capture solver output for display in logs."""
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    
    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        solution = solver.solve(problem)
    
    stdout_content = stdout_buffer.getvalue()
    stderr_content = stderr_buffer.getvalue()
    
    return solution, stdout_content, stderr_content

def test_streamlit_components():
    """Test the core visualization and solving components."""
    print("🧪 Testing Streamlit App Components")
    print("=" * 50)
    
    # Test case: Pinwheel arrangement
    print("\n📦 Testing 40×40 container with 24×16 tiles (Pinwheel Pattern)")
    
    problem = PackingProblem(
        container_w=40,
        container_h=40,
        tile_w=24,
        tile_h=16,
        allow_rotation=True
    )
    
    solver = HybridSolver(time_limit=30.0)
    
    print("🔄 Solving with log capture...")
    solution, stdout_logs, stderr_logs = capture_solver_output(solver, problem)
    
    print(f"\n✅ Solution Results:")
    print(f"   Tiles Placed: {solution.num_tiles}/{problem.theoretical_max_tiles}")
    print(f"   Efficiency: {solution.efficiency:.1f}%")
    print(f"   Solve Time: {solution.solve_time:.3f}s")
    print(f"   Solver: {solution.solver_name}")
    
    print(f"\n📜 Captured Logs ({len(stdout_logs)} characters):")
    print(stdout_logs[:500] + "..." if len(stdout_logs) > 500 else stdout_logs)
    
    print(f"\n🎨 Creating enhanced visualization...")
    fig = create_enhanced_visualization(solution, problem)
    
    # Save the visualization
    fig.savefig("test_streamlit_visualization.png", dpi=150, bbox_inches='tight')
    print(f"   Saved visualization to: test_streamlit_visualization.png")
    
    plt.close(fig)
    
    # Test metrics display
    print(f"\n📊 Metrics Summary:")
    metrics = {
        "Container Size": f"{problem.container_w} × {problem.container_h}",
        "Tile Size": f"{problem.tile_w} × {problem.tile_h}",
        "Container Area": f"{problem.container_area} units²",
        "Used Area": f"{solution.num_tiles * problem.tile_area} units²",
        "Wasted Area": f"{problem.container_area - (solution.num_tiles * problem.tile_area)} units²",
        "Rotation Allowed": "✅ Yes" if problem.allow_rotation else "❌ No"
    }
    
    for label, value in metrics.items():
        print(f"   {label}: {value}")
    
    # Test tile positions
    if solution.tile_positions:
        print(f"\n📋 Tile Positions:")
        for i, (x, y, w, h, orientation) in enumerate(solution.tile_positions):
            print(f"   T{i+1}: ({x},{y}) {w}×{h} {orientation}")
    
    print(f"\n✅ All components tested successfully!")
    return True

if __name__ == "__main__":
    test_streamlit_components()