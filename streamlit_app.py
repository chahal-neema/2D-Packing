#!/usr/bin/env python3
"""
Interactive 2D Rectangle Packing Visualization with Streamlit
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import time
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

# Import the packing framework
from src.core.problem import PackingProblem
from src.solvers.hybrid_solver import HybridSolver
from src.visualization.plotter import visualize_solution

# Configure Streamlit page
st.set_page_config(
    page_title="2D Rectangle Packing Visualizer",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-metric {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .warning-metric {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    .info-metric {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
    }
    .log-container {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 0.25rem;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        max-height: 400px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

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
        # Use a more vibrant color palette
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
    
    # Add container dimensions as annotations
    ax.annotate(f'{solution.container_w}', xy=(solution.container_w/2, -1), 
                ha='center', va='top', fontsize=10, fontweight='bold')
    ax.annotate(f'{solution.container_h}', xy=(-1, solution.container_h/2), 
                ha='right', va='center', rotation=90, fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    return fig

def capture_solver_output(solver, problem):
    """Capture solver output for display in logs."""
    # Create string buffers to capture output
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    
    # Capture both stdout and stderr
    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        solution = solver.solve(problem)
    
    # Get the captured output
    stdout_content = stdout_buffer.getvalue()
    stderr_content = stderr_buffer.getvalue()
    
    return solution, stdout_content, stderr_content

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">📦 2D Rectangle Packing Visualizer</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("🔧 Configuration")
        
        st.subheader("Container Dimensions")
        container_w = st.number_input("Container Width", min_value=1, max_value=200, value=40, step=1)
        container_h = st.number_input("Container Height", min_value=1, max_value=200, value=40, step=1)
        
        st.subheader("Tile Dimensions")
        tile_w = st.number_input("Tile Width", min_value=1, max_value=100, value=24, step=1)
        tile_h = st.number_input("Tile Height", min_value=1, max_value=100, value=16, step=1)
        
        st.subheader("Solver Options")
        allow_rotation = st.checkbox("Allow Rotation", value=True)
        time_limit = st.slider("Time Limit (seconds)", min_value=5, max_value=120, value=60, step=5)
        
        # Preset examples
        st.subheader("📋 Preset Examples")
        if st.button("40×40 with 24×16 (Pinwheel)"):
            st.session_state.container_w = 40
            st.session_state.container_h = 40
            st.session_state.tile_w = 24
            st.session_state.tile_h = 16
            st.experimental_rerun()
            
        if st.button("40×48 with 12×16"):
            st.session_state.container_w = 40
            st.session_state.container_h = 48
            st.session_state.tile_w = 12
            st.session_state.tile_h = 16
            st.experimental_rerun()
            
        if st.button("40×48 with 10×10"):
            st.session_state.container_w = 40
            st.session_state.container_h = 48
            st.session_state.tile_w = 10
            st.session_state.tile_h = 10
            st.experimental_rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎯 Packing Visualization")
        
        # Solve button
        if st.button("🚀 Solve Packing Problem", type="primary", use_container_width=True):
            
            # Validate inputs
            if tile_w > container_w or tile_h > container_h:
                st.error("❌ Tile dimensions cannot be larger than container dimensions!")
                return
            
            # Create problem
            try:
                problem = PackingProblem(
                    container_w=container_w,
                    container_h=container_h,
                    tile_w=tile_w,
                    tile_h=tile_h,
                    allow_rotation=allow_rotation
                )
                
                # Solve with progress tracking
                solver = HybridSolver(time_limit=time_limit)
                
                with st.spinner("🔄 Solving packing problem..."):
                    start_time = time.time()
                    solution, stdout_logs, stderr_logs = capture_solver_output(solver, problem)
                    solve_time = time.time() - start_time
                
                # Store results in session state
                st.session_state.solution = solution
                st.session_state.problem = problem
                st.session_state.logs = stdout_logs
                st.session_state.solve_time = solve_time
                
                st.success("✅ Packing problem solved successfully!")
                
            except Exception as e:
                st.error(f"❌ Error solving problem: {str(e)}")
                return
        
        # Display visualization if solution exists
        if hasattr(st.session_state, 'solution') and st.session_state.solution:
            solution = st.session_state.solution
            problem = st.session_state.problem
            
            # Create enhanced visualization
            fig = create_enhanced_visualization(solution, problem)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)  # Clean up memory
    
    with col2:
        st.subheader("📊 Results & Metrics")
        
        if hasattr(st.session_state, 'solution') and st.session_state.solution:
            solution = st.session_state.solution
            problem = st.session_state.problem
            
            # Key Metrics Cards
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.metric(
                    label="🎯 Tiles Placed",
                    value=solution.num_tiles,
                    delta=f"of {problem.theoretical_max_tiles} max"
                )
                
            with col_b:
                efficiency = solution.efficiency
                st.metric(
                    label="⚡ Efficiency",
                    value=f"{efficiency:.1f}%",
                    delta="Optimal" if efficiency >= 95 else "Sub-optimal"
                )
            
            # Additional metrics
            st.markdown("### 📈 Detailed Metrics")
            
            metrics_data = {
                "Container Size": f"{problem.container_w} × {problem.container_h}",
                "Tile Size": f"{problem.tile_w} × {problem.tile_h}",
                "Container Area": f"{problem.container_area} units²",
                "Tile Area": f"{problem.tile_area} units²",
                "Used Area": f"{solution.num_tiles * problem.tile_area} units²",
                "Wasted Area": f"{problem.container_area - (solution.num_tiles * problem.tile_area)} units²",
                "Rotation Allowed": "✅ Yes" if problem.allow_rotation else "❌ No",
                "Solver Used": solution.solver_name,
                "Solve Time": f"{solution.solve_time:.3f}s"
            }
            
            for label, value in metrics_data.items():
                st.text(f"{label}: {value}")
            
            # Tile positions table
            if solution.tile_positions:
                st.markdown("### 📋 Tile Positions")
                
                tile_data = []
                for i, (x, y, w, h, orientation) in enumerate(solution.tile_positions):
                    tile_data.append({
                        "Tile": f"T{i+1}",
                        "X": x,
                        "Y": y,
                        "Width": w,
                        "Height": h,
                        "Orientation": orientation
                    })
                
                st.dataframe(tile_data, use_container_width=True)
        
        else:
            st.info("👆 Configure parameters and click 'Solve Packing Problem' to see results!")
    
    # Solver Logs Section
    if hasattr(st.session_state, 'logs') and st.session_state.logs:
        st.markdown("---")
        st.subheader("🔍 Solver Logs")
        
        with st.expander("📜 View Detailed Solver Output", expanded=False):
            st.markdown(
                f'<div class="log-container">{st.session_state.logs}</div>',
                unsafe_allow_html=True
            )
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            🔧 Built with Streamlit | 📦 2D Rectangle Packing Framework | 
            🎯 Powered by OR-Tools & Advanced Algorithms
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()