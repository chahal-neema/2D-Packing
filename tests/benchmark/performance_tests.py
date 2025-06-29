"""
Performance benchmarking for rectangle packing solvers.
"""

import time
import statistics
from typing import List, Dict, Any, Callable
import matplotlib.pyplot as plt

from src.core.problem import PackingProblem
from src.solvers.mathematical_solver import MathematicalSolver
from src.solvers.greedy_solver import GreedySolver
from src.solvers.backtrack_solver import BacktrackSolver
from src.solvers.hybrid_solver import HybridSolver

try:
    from src.solvers.ilp_solver import ILPSolver
    ILP_AVAILABLE = True
except ImportError:
    ILP_AVAILABLE = False

class BenchmarkSuite:
    """Comprehensive benchmark suite for rectangle packing solvers."""
    
    def __init__(self):
        self.results = {}
        self.solvers = self._initialize_solvers()
    
    def _initialize_solvers(self) -> Dict[str, Any]:
        """Initialize all available solvers."""
        solvers = {
            'Mathematical': MathematicalSolver(),
            'Greedy_BL': GreedySolver('bottom_left'),
            'Greedy_CO': GreedySolver('center_out'),
            'Backtrack': BacktrackSolver(time_limit=5.0),
            'Hybrid': HybridSolver(time_limit=10.0)
        }
        
        if ILP_AVAILABLE:
            solvers['ILP'] = ILPSolver(time_limit=10.0)
        
        return solvers
    
    def run_performance_benchmark(self, problems: List[PackingProblem], 
                                runs_per_problem: int = 3) -> Dict[str, Any]:
        """
        Run performance benchmark on a list of problems.
        
        Args:
            problems: List of packing problems to test
            runs_per_problem: Number of runs per problem for averaging
            
        Returns:
            Dictionary with benchmark results
        """
        print(f"🔥 PERFORMANCE BENCHMARK: {len(problems)} problems, {runs_per_problem} runs each")
        
        results = {solver_name: {'times': [], 'tiles': [], 'efficiencies': []} 
                  for solver_name in self.solvers.keys()}
        
        for i, problem in enumerate(problems):
            print(f"\n📊 Problem {i+1}/{len(problems)}: {problem.container_w}×{problem.container_h} container, {problem.tile_w}×{problem.tile_h} tiles")
            
            for solver_name, solver in self.solvers.items():
                print(f"   Testing {solver_name}...", end=' ')
                
                run_times = []
                run_tiles = []
                run_efficiencies = []
                
                for run in range(runs_per_problem):
                    try:
                        start_time = time.time()
                        solution = solver.solve(problem)
                        end_time = time.time()
                        
                        run_times.append(end_time - start_time)
                        run_tiles.append(solution.num_tiles)
                        run_efficiencies.append(solution.efficiency)
                        
                    except Exception as e:
                        print(f"FAILED ({e})")
                        run_times.append(float('inf'))
                        run_tiles.append(0)
                        run_efficiencies.append(0)
                        break
                
                if run_times and run_times[0] != float('inf'):
                    avg_time = statistics.mean(run_times)
                    avg_tiles = statistics.mean(run_tiles)
                    avg_efficiency = statistics.mean(run_efficiencies)
                    
                    results[solver_name]['times'].append(avg_time)
                    results[solver_name]['tiles'].append(avg_tiles)
                    results[solver_name]['efficiencies'].append(avg_efficiency)
                    
                    print(f"{avg_tiles:.1f} tiles ({avg_efficiency:.1f}%) in {avg_time:.3f}s")
                else:
                    results[solver_name]['times'].append(float('inf'))
                    results[solver_name]['tiles'].append(0)
                    results[solver_name]['efficiencies'].append(0)
        
        self.results['performance'] = results
        return results
    
    def run_scalability_benchmark(self, base_problem: PackingProblem, 
                                scale_factors: List[float] = [1, 2, 3, 4, 5]) -> Dict[str, Any]:
        """
        Test how solvers scale with problem size.
        
        Args:
            base_problem: Base problem to scale
            scale_factors: Factors to scale container size by
            
        Returns:
            Scalability benchmark results
        """
        print(f"📈 SCALABILITY BENCHMARK: {len(scale_factors)} problem sizes")
        
        problems = []
        for factor in scale_factors:
            scaled_w = int(base_problem.container_w * factor)
            scaled_h = int(base_problem.container_h * factor)
            scaled_problem = PackingProblem(
                scaled_w, scaled_h,
                base_problem.tile_w, base_problem.tile_h,
                allow_rotation=base_problem.allow_rotation
            )
            problems.append(scaled_problem)
        
        # Run performance benchmark on scaled problems
        results = self.run_performance_benchmark(problems, runs_per_problem=2)
        
        # Add problem sizes for analysis
        problem_sizes = [p.container_w * p.container_h for p in problems]
        results['problem_sizes'] = problem_sizes
        results['scale_factors'] = scale_factors
        
        self.results['scalability'] = results
        return results
    
    def run_solution_quality_benchmark(self, problems: List[PackingProblem]) -> Dict[str, Any]:
        """
        Compare solution quality across solvers.
        
        Args:
            problems: List of problems to test
            
        Returns:
            Quality comparison results
        """
        print(f"🎯 SOLUTION QUALITY BENCHMARK: {len(problems)} problems")
        
        quality_results = {}
        
        for i, problem in enumerate(problems):
            print(f"\n📊 Problem {i+1}: {problem.container_w}×{problem.container_h}")
            problem_results = {}
            
            for solver_name, solver in self.solvers.items():
                try:
                    solution = solver.solve(problem)
                    problem_results[solver_name] = {
                        'tiles': solution.num_tiles,
                        'efficiency': solution.efficiency,
                        'solve_time': solution.solve_time,
                        'is_centered': solution.is_centered
                    }
                    print(f"   {solver_name}: {solution.num_tiles} tiles ({solution.efficiency:.1f}%)")
                except Exception as e:
                    print(f"   {solver_name}: FAILED ({e})")
                    problem_results[solver_name] = {
                        'tiles': 0, 'efficiency': 0, 'solve_time': float('inf'), 'is_centered': False
                    }
            
            quality_results[f"problem_{i+1}"] = problem_results
        
        self.results['quality'] = quality_results
        return quality_results
    
    def generate_benchmark_report(self) -> str:
        """Generate a comprehensive benchmark report."""
        if not self.results:
            return "No benchmark results available. Run benchmarks first."
        
        report = ["# Rectangle Packing Solver Benchmark Report\n"]
        
        # Performance Summary
        if 'performance' in self.results:
            report.append("## Performance Summary\n")
            perf_data = self.results['performance']
            
            for solver_name in perf_data.keys():
                times = [t for t in perf_data[solver_name]['times'] if t != float('inf')]
                tiles = perf_data[solver_name]['tiles']
                
                if times:
                    avg_time = statistics.mean(times)
                    avg_tiles = statistics.mean(tiles)
                    report.append(f"**{solver_name}**: {avg_tiles:.1f} avg tiles, {avg_time:.3f}s avg time\n")
        
        # Quality Summary
        if 'quality' in self.results:
            report.append("\n## Solution Quality Summary\n")
            quality_data = self.results['quality']
            
            solver_scores = {solver: [] for solver in self.solvers.keys()}
            
            for problem_results in quality_data.values():
                for solver_name, metrics in problem_results.items():
                    solver_scores[solver_name].append(metrics['tiles'])
            
            report.append("Average tiles placed:\n")
            for solver_name, scores in solver_scores.items():
                if scores:
                    avg_score = statistics.mean(scores)
                    report.append(f"- {solver_name}: {avg_score:.1f}\n")
        
        # Recommendations
        report.append("\n## Recommendations\n")
        if 'performance' in self.results:
            perf_data = self.results['performance']
            
            # Find fastest solver
            avg_times = {}
            for solver_name in perf_data.keys():
                times = [t for t in perf_data[solver_name]['times'] if t != float('inf')]
                if times:
                    avg_times[solver_name] = statistics.mean(times)
            
            if avg_times:
                fastest = min(avg_times.keys(), key=lambda k: avg_times[k])
                report.append(f"- **Fastest solver**: {fastest} ({avg_times[fastest]:.3f}s avg)\n")
            
            # Find best quality solver
            if 'quality' in self.results:
                quality_data = self.results['quality']
                solver_scores = {solver: [] for solver in self.solvers.keys()}
                
                for problem_results in quality_data.values():
                    for solver_name, metrics in problem_results.items():
                        solver_scores[solver_name].append(metrics['tiles'])
                
                avg_scores = {}
                for solver_name, scores in solver_scores.items():
                    if scores:
                        avg_scores[solver_name] = statistics.mean(scores)
                
                if avg_scores:
                    best_quality = max(avg_scores.keys(), key=lambda k: avg_scores[k])
                    report.append(f"- **Best quality**: {best_quality} ({avg_scores[best_quality]:.1f} avg tiles)\n")
        
        return ''.join(report)
    
    def save_benchmark_results(self, filename: str = "benchmark_results.json"):
        """Save benchmark results to JSON file."""
        import json
        
        # Convert any non-serializable values
        serializable_results = {}
        for key, value in self.results.items():
            if isinstance(value, dict):
                serializable_results[key] = {}
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, dict):
                        serializable_results[key][sub_key] = {}
                        for solver, metrics in sub_value.items():
                            if isinstance(metrics, dict):
                                clean_metrics = {}
                                for metric_name, metric_value in metrics.items():
                                    if isinstance(metric_value, list):
                                        clean_metrics[metric_name] = [v if v != float('inf') else None for v in metric_value]
                                    elif metric_value == float('inf'):
                                        clean_metrics[metric_name] = None
                                    else:
                                        clean_metrics[metric_name] = metric_value
                                serializable_results[key][sub_key][solver] = clean_metrics
                            else:
                                serializable_results[key][sub_key] = sub_value
                    else:
                        serializable_results[key][sub_key] = sub_value
            else:
                serializable_results[key] = value
        
        with open(filename, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        print(f"💾 Saved benchmark results to {filename}")

def create_benchmark_problems() -> List[PackingProblem]:
    """Create a standard set of benchmark problems."""
    problems = [
        # Small problems
        PackingProblem(20, 20, 5, 5),
        PackingProblem(30, 20, 10, 5),
        
        # Medium problems  
        PackingProblem(40, 48, 10, 10),
        PackingProblem(50, 30, 8, 12),
        
        # Large problems
        PackingProblem(60, 60, 15, 10),
        PackingProblem(80, 50, 12, 8),
        
        # Challenging ratios
        PackingProblem(35, 25, 7, 11),
        PackingProblem(42, 28, 6, 14),
        
        # Rotation-sensitive
        PackingProblem(30, 50, 10, 15, allow_rotation=True),
        PackingProblem(30, 50, 10, 15, allow_rotation=False),
    ]
    
    return problems

def quick_benchmark():
    """Run a quick benchmark with standard problems."""
    print("🚀 QUICK BENCHMARK")
    
    benchmark = BenchmarkSuite()
    problems = create_benchmark_problems()[:5]  # First 5 problems only
    
    # Run benchmarks
    benchmark.run_performance_benchmark(problems, runs_per_problem=2)
    benchmark.run_solution_quality_benchmark(problems)
    
    # Generate and print report
    report = benchmark.generate_benchmark_report()
    print("\n" + "="*60)
    print(report)
    print("="*60)
    
    return benchmark

def full_benchmark():
    """Run comprehensive benchmark suite."""
    print("🚀 COMPREHENSIVE BENCHMARK SUITE")
    
    benchmark = BenchmarkSuite()
    problems = create_benchmark_problems()
    
    # Run all benchmark types
    print("\n1. Performance Benchmark:")
    benchmark.run_performance_benchmark(problems, runs_per_problem=3)
    
    print("\n2. Solution Quality Benchmark:")
    benchmark.run_solution_quality_benchmark(problems)
    
    print("\n3. Scalability Benchmark:")
    base_problem = PackingProblem(20, 20, 5, 5)
    benchmark.run_scalability_benchmark(base_problem, [1, 1.5, 2, 2.5, 3])
    
    # Generate report
    report = benchmark.generate_benchmark_report()
    print("\n" + "="*80)
    print(report)
    print("="*80)
    
    # Save results
    benchmark.save_benchmark_results("full_benchmark_results.json")
    
    return benchmark

def stress_test():
    """Run stress test with challenging problems."""
    print("🔥 STRESS TEST")
    
    # Create challenging problems
    stress_problems = [
        PackingProblem(100, 100, 7, 11),   # Large with odd dimensions
        PackingProblem(50, 150, 13, 17),   # Very rectangular container
        PackingProblem(200, 80, 9, 23),    # Large asymmetric
        PackingProblem(75, 75, 8, 19),     # Medium with challenging ratio
    ]
    
    benchmark = BenchmarkSuite()
    
    # Only test fast solvers for stress test
    stress_solvers = {
        'Mathematical': MathematicalSolver(),
        'Greedy_CO': GreedySolver('center_out'),
        'Hybrid': HybridSolver(time_limit=30.0)  # Longer time limit
    }
    benchmark.solvers = stress_solvers
    
    # Run stress test
    results = benchmark.run_performance_benchmark(stress_problems, runs_per_problem=1)
    
    print("\n🔥 STRESS TEST RESULTS:")
    for solver_name, data in results.items():
        times = [t for t in data['times'] if t != float('inf')]
        if times:
            max_time = max(times)
            avg_tiles = statistics.mean(data['tiles'])
            print(f"   {solver_name}: {avg_tiles:.1f} avg tiles, {max_time:.2f}s max time")
        else:
            print(f"   {solver_name}: FAILED")
    
    return benchmark

if __name__ == "__main__":
    # Run quick benchmark by default
    quick_benchmark()
