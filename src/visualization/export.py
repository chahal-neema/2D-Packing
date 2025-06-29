"""
Export utilities for saving visualizations and solutions in various formats.
"""

import json
import csv
from typing import List, Dict, Any, Optional
from pathlib import Path
import matplotlib.pyplot as plt

from ..core.solution import PackingSolution
from ..core.problem import PackingProblem

def export_solution_to_json(solution: PackingSolution, filename: str):
    """Export a solution to JSON format."""
    data = solution.to_dict()
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Exported solution to {filename}")

def export_solutions_to_json(solutions: List[PackingSolution], filename: str):
    """Export multiple solutions to JSON format."""
    data = {
        'num_solutions': len(solutions),
        'solutions': [sol.to_dict() for sol in solutions]
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"💾 Exported {len(solutions)} solutions to {filename}")

def export_solution_to_csv(solution: PackingSolution, filename: str):
    """Export solution tile positions to CSV format."""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow(['tile_id', 'x', 'y', 'width', 'height', 'orientation'])
        
        # Write tile data
        for i, (x, y, w, h, orientation) in enumerate(solution.tile_positions):
            writer.writerow([i+1, x, y, w, h, orientation])
    
    print(f"💾 Exported solution to {filename}")

def export_comparison_to_csv(solutions: List[PackingSolution], 
                           solver_names: List[str] = None, 
                           filename: str = "solution_comparison.csv"):
    """Export solution comparison metrics to CSV."""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow(['solver', 'num_tiles', 'efficiency_percent', 'solve_time_seconds', 
                        'container_w', 'container_h', 'is_centered'])
        
        # Write solution data
        for i, solution in enumerate(solutions):
            solver_name = solver_names[i] if solver_names and i < len(solver_names) else solution.solver_name
            writer.writerow([
                solver_name,
                solution.num_tiles,
                round(solution.efficiency, 2),
                round(solution.solve_time, 4),
                solution.container_w,
                solution.container_h,
                solution.is_centered
            ])
    
    print(f"💾 Exported comparison to {filename}")

def save_solution_as_image(solution: PackingSolution, filename: str, 
                          format: str = 'png', dpi: int = 300,
                          title: str = None, figsize: tuple = (10, 8)):
    """Save a solution visualization as an image file."""
    from .plotter import visualize_solution
    
    fig = visualize_solution(solution, title=title, figsize=figsize)
    fig.savefig(filename, format=format, dpi=dpi, bbox_inches='tight')
    plt.close(fig)
    
    print(f"💾 Saved solution image to {filename}")

def save_multiple_solutions_as_images(solutions: List[PackingSolution], 
                                    output_dir: str = "solution_images",
                                    prefix: str = "solution",
                                    format: str = 'png'):
    """Save multiple solutions as separate image files."""
    from .plotter import visualize_solution
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    for i, solution in enumerate(solutions):
        filename = f"{output_dir}/{prefix}_{i+1:03d}.{format}"
        title = f"Solution {i+1} - {solution.num_tiles} tiles ({solution.efficiency:.1f}%)"
        
        fig = visualize_solution(solution, title=title)
        fig.savefig(filename, format=format, dpi=300, bbox_inches='tight')
        plt.close(fig)
    
    print(f"💾 Saved {len(solutions)} solution images to {output_dir}/")

def export_problem_and_solutions(problem: PackingProblem, 
                                solutions: List[PackingSolution],
                                output_dir: str = "packing_results"):
    """Export complete problem and solution set in multiple formats."""
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    # Export problem definition
    problem_data = problem.to_dict()
    with open(f"{output_dir}/problem.json", 'w') as f:
        json.dump(problem_data, f, indent=2)
    
    # Export solutions
    export_solutions_to_json(solutions, f"{output_dir}/solutions.json")
    export_comparison_to_csv(solutions, filename=f"{output_dir}/comparison.csv")
    
    # Save visualizations
    if solutions:
        from .plotter import visualize_multiple_solutions, compare_solutions
        
        # Individual solution images
        save_multiple_solutions_as_images(solutions, f"{output_dir}/images")
        
        # Comparison plot
        if len(solutions) > 1:
            fig = compare_solutions(solutions)
            fig.savefig(f"{output_dir}/comparison.png", dpi=300, bbox_inches='tight')
            plt.close(fig)
        
        # Grid view of all solutions
        fig = visualize_multiple_solutions(solutions)
        fig.savefig(f"{output_dir}/all_solutions.png", dpi=300, bbox_inches='tight')
        plt.close(fig)
    
    print(f"📦 Exported complete results to {output_dir}/")

def load_solution_from_json(filename: str) -> PackingSolution:
    """Load a solution from JSON format."""
    with open(filename, 'r') as f:
        data = json.load(f)
    
    # Reconstruct solution object
    solution = PackingSolution(
        tile_positions=data['tile_positions'],
        container_w=data['container_w'],
        container_h=data['container_h'],
        solve_time=data.get('solve_time', 0.0),
        solver_name=data.get('solver_name', 'unknown'),
        metadata=data.get('metadata')
    )
    
    return solution

def load_solutions_from_json(filename: str) -> List[PackingSolution]:
    """Load multiple solutions from JSON format."""
    with open(filename, 'r') as f:
        data = json.load(f)
    
    solutions = []
    for sol_data in data['solutions']:
        solution = PackingSolution(
            tile_positions=sol_data['tile_positions'],
            container_w=sol_data['container_w'],
            container_h=sol_data['container_h'],
            solve_time=sol_data.get('solve_time', 0.0),
            solver_name=sol_data.get('solver_name', 'unknown'),
            metadata=sol_data.get('metadata')
        )
        solutions.append(solution)
    
    return solutions

def export_to_svg(solution: PackingSolution, filename: str, 
                 include_labels: bool = True):
    """Export solution as SVG for scalable graphics."""
    from .plotter import visualize_solution
    
    fig = visualize_solution(solution, show_labels=include_labels)
    fig.savefig(filename, format='svg', bbox_inches='tight')
    plt.close(fig)
    
    print(f"💾 Exported SVG to {filename}")

def create_solution_report(problem: PackingProblem, 
                         solutions: List[PackingSolution],
                         output_file: str = "packing_report.html"):
    """Create an HTML report with all solutions and analysis."""
    html_content = _generate_html_report(problem, solutions)
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"📄 Created HTML report: {output_file}")

def _generate_html_report(problem: PackingProblem, solutions: List[PackingSolution]) -> str:
    """Generate HTML content for the solution report."""
    if not solutions:
        return "<html><body><h1>No solutions found</h1></body></html>"
    
    best_solution = max(solutions, key=lambda s: s.num_tiles)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Rectangle Packing Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; }}
            .solution {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
            .metrics {{ display: flex; gap: 20px; }}
            .metric {{ background-color: #e9f4ff; padding: 10px; border-radius: 5px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Rectangle Packing Solution Report</h1>
            <p><strong>Problem:</strong> {problem.tile_w}×{problem.tile_h} tiles in {problem.container_w}×{problem.container_h} container</p>
            <p><strong>Solutions found:</strong> {len(solutions)}</p>
            <p><strong>Best result:</strong> {best_solution.num_tiles} tiles ({best_solution.efficiency:.1f}% efficiency)</p>
        </div>
    """
    
    # Solution comparison table
    html += """
        <h2>Solution Comparison</h2>
        <table>
            <tr>
                <th>Solver</th>
                <th>Tiles</th>
                <th>Efficiency (%)</th>
                <th>Solve Time (s)</th>
                <th>Centered</th>
            </tr>
    """
    
    for i, solution in enumerate(solutions):
        html += f"""
            <tr>
                <td>{solution.solver_name}</td>
                <td>{solution.num_tiles}</td>
                <td>{solution.efficiency:.1f}%</td>
                <td>{solution.solve_time:.3f}</td>
                <td>{'Yes' if solution.is_centered else 'No'}</td>
            </tr>
        """
    
    html += "</table>"
    
    # Individual solution details
    html += "<h2>Solution Details</h2>"
    for i, solution in enumerate(solutions):
        html += f"""
        <div class="solution">
            <h3>Solution {i+1}: {solution.solver_name}</h3>
            <div class="metrics">
                <div class="metric">
                    <strong>Tiles:</strong> {solution.num_tiles}
                </div>
                <div class="metric">
                    <strong>Efficiency:</strong> {solution.efficiency:.1f}%
                </div>
                <div class="metric">
                    <strong>Solve Time:</strong> {solution.solve_time:.3f}s
                </div>
            </div>
            <h4>Tile Positions:</h4>
            <table>
                <tr><th>Tile</th><th>X</th><th>Y</th><th>Width</th><th>Height</th><th>Orientation</th></tr>
        """
        
        for j, (x, y, w, h, orientation) in enumerate(solution.tile_positions):
            html += f"<tr><td>{j+1}</td><td>{x}</td><td>{y}</td><td>{w}</td><td>{h}</td><td>{orientation}</td></tr>"
        
        html += "</table></div>"
    
    html += """
        </body>
    </html>
    """
    
    return html

# Batch export functions
def export_solutions_batch(solutions: List[PackingSolution], 
                          output_dir: str = "batch_export",
                          formats: List[str] = None):
    """Export solutions in multiple formats."""
    if formats is None:
        formats = ['json', 'csv', 'png']
    
    Path(output_dir).mkdir(exist_ok=True)
    
    for format_type in formats:
        if format_type == 'json':
            export_solutions_to_json(solutions, f"{output_dir}/solutions.json")
        elif format_type == 'csv':
            export_comparison_to_csv(solutions, filename=f"{output_dir}/solutions.csv")
        elif format_type in ['png', 'pdf', 'svg']:
            save_multiple_solutions_as_images(solutions, f"{output_dir}/images", format=format_type)
    
    print(f"📦 Batch export completed to {output_dir}/")
