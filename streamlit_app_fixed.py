#!/usr/bin/env python3
"""
Interactive 2D Rectangle Packing Visualization with Streamlit - Fixed Version
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
    title = f"Packing Solution: {solution.num_tiles} tiles (Efficiency: {efficiency_text})"
    if solution.solver_name != "unknown":
        title += f"\nSolver: {solution.solver_name}"
    
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
    st.markdown("### Interactive optimization of rectangle packing problems")
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
        find_all_solutions = st.checkbox("Find All Optimal Solutions", value=False, help="Find multiple optimal arrangements (may take longer)")
        max_solutions = st.slider("Max Solutions", min_value=1, max_value=50, value=20, step=5, disabled=not find_all_solutions)
        
        if find_all_solutions:
            deduplicate_symmetric = st.checkbox("Remove Symmetric/Rotated Duplicates", value=True, 
                                              help="Filter out solutions that are just rotations or mirror images of each other")
        
        # Preset examples
        st.subheader("📋 Preset Examples")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Pinwheel\n40×40, 24×16", use_container_width=True):
                st.session_state.container_w = 40
                st.session_state.container_h = 40
                st.session_state.tile_w = 24
                st.session_state.tile_h = 16
                st.rerun()
                
        with col2:
            if st.button("Optimal\n40×48, 12×16", use_container_width=True):
                st.session_state.container_w = 40
                st.session_state.container_h = 48
                st.session_state.tile_w = 12
                st.session_state.tile_h = 16
                st.rerun()
                
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Square Pack\n40×48, 10×10", use_container_width=True):
                st.session_state.container_w = 40
                st.session_state.container_h = 48
                st.session_state.tile_w = 10
                st.session_state.tile_h = 10
                st.rerun()
                
        with col2:
            if st.button("Multi-Solution\n40×48, 8×10", use_container_width=True):
                st.session_state.container_w = 40
                st.session_state.container_h = 48
                st.session_state.tile_w = 8
                st.session_state.tile_h = 10
                st.rerun()
    
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
                
                # Show problem info
                st.info(f"📊 Problem: Pack {tile_w}×{tile_h} tiles in {container_w}×{container_h} container (Max: {problem.theoretical_max_tiles} tiles)")
                
                # Solve with progress tracking
                solver = HybridSolver(time_limit=time_limit)
                
                with st.spinner("🔄 Solving packing problem..."):
                    start_time = time.time()
                    
                    if find_all_solutions:
                        # Find all optimal solutions
                        stdout_buffer = io.StringIO()
                        with redirect_stdout(stdout_buffer):
                            if deduplicate_symmetric:
                                solutions = solver.solve_all_optimal(problem, max_solutions)
                            else:
                                # Force backtracking solver to get raw solutions without deduplication
                                from src.solvers.backtrack_solver import BacktrackSolver
                                raw_solver = BacktrackSolver(max_solutions=max_solutions, time_limit=time_limit//2)
                                solutions = raw_solver.solve_all_optimal(problem, max_solutions)
                        stdout_logs = stdout_buffer.getvalue()
                        
                        if solutions:
                            solution = solutions[0]  # Primary solution for metrics
                            solve_time = time.time() - start_time
                            
                            st.success(f"✅ Found {len(solutions)} optimal solution(s) with {solution.num_tiles} tiles ({solution.efficiency:.1f}% efficiency)!")
                        else:
                            solution = None
                            solutions = []
                            solve_time = time.time() - start_time
                            st.warning("⚠️ No optimal solutions found!")
                    else:
                        # Find single best solution
                        solution, stdout_logs, stderr_logs = capture_solver_output(solver, problem)
                        solutions = [solution] if solution.num_tiles > 0 else []
                        solve_time = time.time() - start_time
                        
                        if solution.num_tiles > 0:
                            st.success(f"✅ Found solution with {solution.num_tiles} tiles ({solution.efficiency:.1f}% efficiency)!")
                        else:
                            st.warning("⚠️ No valid packing found!")
                
                # Store results in session state
                st.session_state.solution = solution
                st.session_state.solutions = solutions
                st.session_state.problem = problem
                st.session_state.logs = stdout_logs
                st.session_state.solve_time = solve_time
                if find_all_solutions:
                    st.session_state.deduplicate_symmetric = deduplicate_symmetric
                
            except Exception as e:
                st.error(f"❌ Error solving problem: {str(e)}")
                return
        
        # Display visualization if solution exists
        if hasattr(st.session_state, 'solutions') and st.session_state.solutions:
            solutions = st.session_state.solutions
            problem = st.session_state.problem
            
            if len(solutions) == 1:
                # Single solution display
                try:
                    fig = create_enhanced_visualization(solutions[0], problem)
                    st.pyplot(fig, use_container_width=True)
                    plt.close(fig)
                except Exception as e:
                    st.error(f"❌ Visualization error: {str(e)}")
            else:
                # Multiple solutions display
                st.subheader(f"🎯 All {len(solutions)} Optimal Solutions")
                
                # Solution selector
                solution_idx = st.selectbox(
                    "Select Solution to View:",
                    range(len(solutions)),
                    format_func=lambda x: f"Solution {x+1}" + (f" - {solutions[x].solver_name}" if hasattr(solutions[x], 'solver_name') else "")
                )
                
                # Display selected solution
                try:
                    selected_solution = solutions[solution_idx]
                    fig = create_enhanced_visualization(selected_solution, problem)
                    st.pyplot(fig, use_container_width=True)
                    plt.close(fig)
                    
                    # Show differences between solutions
                    st.info(f"📍 **Solution {solution_idx+1}**: {selected_solution.num_tiles} tiles, "
                           f"bounding box: {selected_solution.bounding_box}")
                    
                except Exception as e:
                    st.error(f"❌ Visualization error: {str(e)}")
    
    with col2:
        st.subheader("📊 Results & Metrics")
        
        if hasattr(st.session_state, 'solutions') and st.session_state.solutions:
            solutions = st.session_state.solutions
            solution = solutions[0]  # Primary solution for metrics
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
                delta_label = "Optimal" if efficiency >= 95 else "Sub-optimal"
                st.metric(
                    label="⚡ Efficiency",
                    value=f"{efficiency:.1f}%",
                    delta=delta_label
                )
            
            # Additional metrics in expandable section
            with st.expander("📈 Detailed Metrics", expanded=True):
                metrics_data = {
                    "Container Size": f"{problem.container_w} × {problem.container_h}",
                    "Tile Size": f"{problem.tile_w} × {problem.tile_h}",
                    "Container Area": f"{problem.container_area:,} units²",
                    "Tile Area": f"{problem.tile_area} units²",
                    "Used Area": f"{solution.num_tiles * problem.tile_area:,} units²",
                    "Wasted Area": f"{problem.container_area - (solution.num_tiles * problem.tile_area):,} units²",
                    "Rotation Allowed": "✅ Yes" if problem.allow_rotation else "❌ No",
                    "Solver Used": solution.solver_name,
                    "Solve Time": f"{solution.solve_time:.3f}s"
                }
                
                for label, value in metrics_data.items():
                    st.text(f"{label}: {value}")
            
            # Tile positions table
            if solution.tile_positions:
                with st.expander("📋 Tile Positions"):
                    
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
            
            # Multiple solutions summary
            if len(solutions) > 1:
                st.markdown("### 🔄 All Solutions Summary")
                
                solutions_data = []
                for i, sol in enumerate(solutions):
                    bbox = sol.bounding_box
                    used_w = bbox[2] - bbox[0] if bbox else 0
                    used_h = bbox[3] - bbox[1] if bbox else 0
                    
                    solutions_data.append({
                        "Solution": f"#{i+1}",
                        "Tiles": sol.num_tiles,
                        "Efficiency": f"{sol.efficiency:.1f}%",
                        "Bounding Box": f"{used_w}×{used_h}",
                        "Solver": getattr(sol, 'solver_name', 'Unknown'),
                        "Centered": "✅" if getattr(sol, 'is_centered', False) else "❌"
                    })
                
                st.dataframe(solutions_data, use_container_width=True)
                
                dedup_status = "after removing symmetric duplicates" if hasattr(st.session_state, 'deduplicate_symmetric') and st.session_state.get('deduplicate_symmetric', True) else "including symmetric variations"
                st.info(f"💡 Found {len(solutions)} different ways to achieve {solution.num_tiles} tiles with {solution.efficiency:.1f}% efficiency ({dedup_status})!")
        
        else:
            st.info("👆 Configure parameters and click 'Solve Packing Problem' to see results!")
    
    # Solver Logs Section
    if hasattr(st.session_state, 'logs') and st.session_state.logs:
        st.markdown("---")
        st.subheader("🔍 Solver Logs")
        
        with st.expander("📜 View Detailed Solver Output", expanded=False):
            st.code(st.session_state.logs, language='text')
    
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