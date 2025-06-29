"""
Interactive visualization using Plotly for rectangle packing solutions.
"""

try:
    import plotly.graph_objects as go
    import plotly.subplots as sp
    from plotly.colors import qualitative
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

import numpy as np
from typing import List, Optional, Dict, Any
from ..core.solution import PackingSolution
from ..core.problem import PackingProblem

def create_interactive_solution_plot(solution: PackingSolution, 
                                   problem: PackingProblem = None,
                                   title: str = None) -> Any:
    """
    Create an interactive plot of a packing solution using Plotly.
    
    Returns:
        Plotly Figure object or None if Plotly not available
    """
    if not PLOTLY_AVAILABLE:
        print("❌ Plotly not available. Install with: pip install plotly")
        return None
    
    fig = go.Figure()
    
    # Add container boundary
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=solution.container_w, y1=solution.container_h,
        line=dict(color="black", width=3),
        fillcolor="rgba(0,0,0,0)"
    )
    
    # Add tiles
    colors = qualitative.Set3
    for i, (x, y, w, h, orientation) in enumerate(solution.tile_positions):
        color = colors[i % len(colors)]
        
        # Add tile rectangle
        fig.add_shape(
            type="rect",
            x0=x, y0=y, x1=x+w, y1=y+h,
            line=dict(color="black", width=1),
            fillcolor=color,
            opacity=0.7
        )
        
        # Add tile label
        fig.add_annotation(
            x=x + w/2, y=y + h/2,
            text=f"T{i+1}",
            showarrow=False,
            font=dict(size=12, color="black"),
            bgcolor="white",
            bordercolor="black",
            borderwidth=1
        )
        
        # Add hover info
        hover_text = (f"Tile {i+1}<br>"
                     f"Position: ({x}, {y})<br>"
                     f"Size: {w}×{h}<br>"
                     f"Orientation: {orientation}")
        
        # Add invisible scatter point for hover
        fig.add_trace(go.Scatter(
            x=[x + w/2], y=[y + h/2],
            mode='markers',
            marker=dict(size=1, opacity=0),
            hovertext=hover_text,
            hoverinfo='text',
            showlegend=False
        ))
    
    # Update layout
    if title is None:
        efficiency = f"{solution.efficiency:.1f}%" if solution.num_tiles > 0 else "0%"
        title = f"Interactive Packing Solution - {solution.num_tiles} tiles ({efficiency})"
    
    fig.update_layout(
        title=title,
        xaxis=dict(title="X Position", range=[-1, solution.container_w + 1]),
        yaxis=dict(title="Y Position", range=[-1, solution.container_h + 1]),
        width=800, height=600,
        showlegend=False
    )
    
    # Ensure equal aspect ratio
    fig.update_yaxis(scaleanchor="x", scaleratio=1)
    
    return fig

def create_solution_comparison_dashboard(solutions: List[PackingSolution],
                                       labels: List[str] = None) -> Any:
    """
    Create an interactive dashboard comparing multiple solutions.
    """
    if not PLOTLY_AVAILABLE:
        print("❌ Plotly not available. Install with: pip install plotly")
        return None
    
    if not solutions:
        return None
    
    n_solutions = len(solutions)
    labels = labels or [f"Solution {i+1}" for i in range(n_solutions)]
    
    # Create subplots
    fig = sp.make_subplots(
        rows=2, cols=n_solutions,
        subplot_titles=labels,
        specs=[[{"type": "scatter"}] * n_solutions,
               [{"colspan": n_solutions, "type": "bar"}] + [None] * (n_solutions - 1)],
        vertical_spacing=0.12,
        row_heights=[0.7, 0.3]
    )
    
    # Add solution plots
    colors = qualitative.Set3
    for sol_idx, (solution, label) in enumerate(zip(solutions, labels)):
        col = sol_idx + 1
        
        # Add container boundary
        fig.add_shape(
            type="rect",
            x0=0, y0=0, x1=solution.container_w, y1=solution.container_h,
            line=dict(color="black", width=2),
            fillcolor="rgba(0,0,0,0)",
            row=1, col=col
        )
        
        # Add tiles
        for i, (x, y, w, h, orientation) in enumerate(solution.tile_positions):
            color = colors[i % len(colors)]
            
            fig.add_shape(
                type="rect",
                x0=x, y0=y, x1=x+w, y1=y+h,
                line=dict(color="black", width=1),
                fillcolor=color,
                opacity=0.7,
                row=1, col=col
            )
            
            # Add tile annotation
            fig.add_annotation(
                x=x + w/2, y=y + h/2,
                text=str(i+1),
                showarrow=False,
                font=dict(size=10),
                row=1, col=col
            )
    
    # Add metrics comparison bar chart
    metrics = ['Tiles', 'Efficiency (%)', 'Solve Time (s)']
    tile_counts = [s.num_tiles for s in solutions]
    efficiencies = [s.efficiency for s in solutions]
    solve_times = [s.solve_time for s in solutions]
    
    fig.add_trace(
        go.Bar(name='Tiles', x=labels, y=tile_counts, yaxis='y3'),
        row=2, col=1
    )
    
    # Update layout
    fig.update_layout(
        title="Solution Comparison Dashboard",
        height=800,
        showlegend=False
    )
    
    # Update subplot axes
    for i in range(n_solutions):
        fig.update_xaxes(title="X", row=1, col=i+1)
        fig.update_yaxes(title="Y", row=1, col=i+1)
    
    fig.update_xaxes(title="Solutions", row=2, col=1)
    fig.update_yaxes(title="Value", row=2, col=1)
    
    return fig

def create_algorithm_performance_plot(solver_results: Dict[str, Dict]) -> Any:
    """
    Create interactive plot showing performance comparison of different algorithms.
    
    Args:
        solver_results: Dict mapping solver names to result dictionaries
                       containing 'solve_time', 'num_tiles', 'efficiency'
    """
    if not PLOTLY_AVAILABLE:
        print("❌ Plotly not available. Install with: pip install plotly")
        return None
    
    solvers = list(solver_results.keys())
    solve_times = [solver_results[s].get('solve_time', 0) for s in solvers]
    tile_counts = [solver_results[s].get('num_tiles', 0) for s in solvers]
    efficiencies = [solver_results[s].get('efficiency', 0) for s in solvers]
    
    # Create scatter plot: solve time vs efficiency, bubble size = tile count
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=solve_times,
        y=efficiencies,
        mode='markers+text',
        marker=dict(
            size=[max(10, t * 2) for t in tile_counts],  # Bubble size based on tile count
            color=tile_counts,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Number of Tiles")
        ),
        text=solvers,
        textposition="top center",
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Solve Time: %{x:.3f}s<br>"
            "Efficiency: %{y:.1f}%<br>"
            "Tiles: %{marker.color}<br>"
            "<extra></extra>"
        )
    ))
    
    fig.update_layout(
        title="Algorithm Performance Comparison",
        xaxis_title="Solve Time (seconds)",
        yaxis_title="Efficiency (%)",
        width=800, height=600
    )
    
    return fig

def show_interactive_plot(fig: Any, auto_open: bool = True):
    """
    Display an interactive plot in the browser.
    
    Args:
        fig: Plotly figure object
        auto_open: Whether to automatically open browser
    """
    if not PLOTLY_AVAILABLE or fig is None:
        return
    
    fig.show(config={'displayModeBar': True}, auto_open=auto_open)

def save_interactive_plot(fig: Any, filename: str, format: str = 'html'):
    """
    Save an interactive plot to file.
    
    Args:
        fig: Plotly figure object
        filename: Output filename
        format: Output format ('html', 'png', 'pdf', 'svg')
    """
    if not PLOTLY_AVAILABLE or fig is None:
        return
    
    if format == 'html':
        fig.write_html(filename)
    else:
        fig.write_image(filename, format=format)
    
    print(f"💾 Saved interactive plot to {filename}")

# Convenience functions
def quick_interactive_plot(solution: PackingSolution) -> Any:
    """Quickly create and show an interactive plot."""
    fig = create_interactive_solution_plot(solution)
    if fig:
        show_interactive_plot(fig)
    return fig

def interactive_comparison(solutions: List[PackingSolution], 
                         solver_names: List[str] = None) -> Any:
    """Quickly create and show an interactive comparison."""
    labels = solver_names or [s.solver_name for s in solutions]
    fig = create_solution_comparison_dashboard(solutions, labels)
    if fig:
        show_interactive_plot(fig)
    return fig
