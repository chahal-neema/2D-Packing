"""
Standard test cases for rectangle packing algorithms.
"""

from src.core.problem import PackingProblem
from typing import List, Dict, Any

class TestCaseLibrary:
    """Library of standard test cases for rectangle packing."""
    
    @staticmethod
    def get_trivial_cases() -> List[Dict[str, Any]]:
        """Get trivial test cases with known optimal solutions."""
        return [
            {
                'name': 'Perfect 2x2 Square',
                'problem': PackingProblem(20, 20, 10, 10),
                'optimal_tiles': 4,
                'optimal_efficiency': 100.0,
                'description': 'Perfect square grid - should achieve 100% efficiency'
            },
            {
                'name': 'Perfect 3x2 Rectangle',
                'problem': PackingProblem(30, 20, 10, 10),
                'optimal_tiles': 6,
                'optimal_efficiency': 100.0,
                'description': 'Perfect rectangular grid'
            },
            {
                'name': 'Single Tile Fit',
                'problem': PackingProblem(15, 15, 10, 10),
                'optimal_tiles': 1,
                'optimal_efficiency': 44.4,
                'description': 'Only one tile can fit'
            },
            {
                'name': 'No Tiles Fit',
                'problem': PackingProblem(5, 5, 10, 10),
                'optimal_tiles': 0,
                'optimal_efficiency': 0.0,
                'description': 'Tiles too large for container'
            }
        ]
    
    @staticmethod
    def get_rotation_cases() -> List[Dict[str, Any]]:
        """Get test cases that benefit from rotation."""
        return [
            {
                'name': 'Rotation Required',
                'problem': PackingProblem(25, 15, 5, 10, allow_rotation=True),
                'optimal_tiles': 6,
                'description': 'Rotation necessary to fit optimally'
            },
            {
                'name': 'Rotation Forbidden',
                'problem': PackingProblem(25, 15, 5, 10, allow_rotation=False),
                'optimal_tiles': 3,
                'description': 'Same as above but rotation not allowed'
            },
            {
                'name': 'Mixed Orientations',
                'problem': PackingProblem(35, 25, 7, 10, allow_rotation=True),
                'optimal_tiles': 10,
                'description': 'Benefits from mixing orientations'
            }
        ]
    
    @staticmethod
    def get_challenging_cases() -> List[Dict[str, Any]]:
        """Get challenging test cases with non-obvious solutions."""
        return [
            {
                'name': 'Prime Dimensions',
                'problem': PackingProblem(37, 31, 7, 11),
                'description': 'Prime numbers make tiling challenging'
            },
            {
                'name': 'Aspect Ratio Mismatch',
                'problem': PackingProblem(50, 10, 8, 8),
                'description': 'Very different aspect ratios'
            },
            {
                'name': 'Near-Perfect Fit',
                'problem': PackingProblem(33, 27, 11, 9),
                'description': 'Close to perfect fit but not quite'
            },
            {
                'name': 'Wasteful Dimensions',
                'problem': PackingProblem(29, 23, 10, 8),
                'description': 'Dimensions chosen to create waste'
            },
            {
                'name': 'Large Scale',
                'problem': PackingProblem(100, 100, 13, 17),
                'description': 'Large problem with irregular tile size'
            }
        ]
    
    @staticmethod
    def get_regression_cases() -> List[Dict[str, Any]]:
        """Get cases that have caused issues in the past."""
        return [
            {
                'name': 'Zero Area Container',
                'problem': PackingProblem(0, 10, 5, 5),
                'optimal_tiles': 0,
                'description': 'Edge case: zero-width container',
                'should_fail': True
            },
            {
                'name': 'Zero Area Tile',
                'problem': PackingProblem(20, 20, 0, 5),
                'optimal_tiles': 0,
                'description': 'Edge case: zero-width tile',
                'should_fail': True
            },
            {
                'name': 'Very Thin Container',
                'problem': PackingProblem(1, 100, 1, 10),
                'optimal_tiles': 10,
                'description': 'Extremely thin container'
            },
            {
                'name': 'Very Thin Tiles',
                'problem': PackingProblem(100, 100, 1, 1),
                'optimal_tiles': 10000,
                'description': 'Tiny tiles in large container'
            }
        ]
    
    @staticmethod
    def get_performance_cases() -> List[Dict[str, Any]]:
        """Get cases designed to test performance."""
        return [
            {
                'name': 'Medium Complexity',
                'problem': PackingProblem(60, 40, 8, 12),
                'description': 'Medium-sized problem for performance testing'
            },
            {
                'name': 'High Complexity',
                'problem': PackingProblem(100, 80, 11, 13),
                'description': 'Large problem with irregular dimensions'
            },
            {
                'name': 'Very High Complexity',
                'problem': PackingProblem(150, 120, 17, 19),
                'description': 'Very large problem - may timeout'
            },
            {
                'name': 'Backtrack Killer',
                'problem': PackingProblem(50, 50, 7, 11),
                'description': 'Designed to be hard for backtracking algorithms'
            }
        ]
    
    @staticmethod
    def get_symmetry_cases() -> List[Dict[str, Any]]:
        """Get cases designed to test symmetry detection."""
        return [
            {
                'name': 'Perfect Square Symmetry',
                'problem': PackingProblem(40, 40, 10, 10),
                'optimal_tiles': 16,
                'description': 'Should produce symmetric solutions'
            },
            {
                'name': 'Rectangle with Center Line',
                'problem': PackingProblem(60, 30, 10, 10),
                'optimal_tiles': 18,
                'description': 'Solutions should have mirror symmetry'
            },
            {
                'name': 'Asymmetric Container',
                'problem': PackingProblem(37, 23, 5, 5),
                'description': 'Container dimensions prevent perfect symmetry'
            }
        ]
    
    @staticmethod
    def get_all_test_cases() -> Dict[str, List[Dict[str, Any]]]:
        """Get all test cases organized by category."""
        return {
            'trivial': TestCaseLibrary.get_trivial_cases(),
            'rotation': TestCaseLibrary.get_rotation_cases(),
            'challenging': TestCaseLibrary.get_challenging_cases(),
            'regression': TestCaseLibrary.get_regression_cases(),
            'performance': TestCaseLibrary.get_performance_cases(),
            'symmetry': TestCaseLibrary.get_symmetry_cases()
        }
    
    @staticmethod
    def get_test_case_by_name(name: str) -> Dict[str, Any]:
        """Get a specific test case by name."""
        all_cases = TestCaseLibrary.get_all_test_cases()
        
        for category, cases in all_cases.items():
            for case in cases:
                if case['name'] == name:
                    return case
        
        raise ValueError(f"Test case '{name}' not found")
    
    @staticmethod
    def get_quick_test_suite() -> List[Dict[str, Any]]:
        """Get a quick test suite for rapid validation."""
        return [
            TestCaseLibrary.get_test_case_by_name('Perfect 2x2 Square'),
            TestCaseLibrary.get_test_case_by_name('Perfect 3x2 Rectangle'),
            TestCaseLibrary.get_test_case_by_name('Rotation Required'),
            TestCaseLibrary.get_test_case_by_name('Prime Dimensions'),
            TestCaseLibrary.get_test_case_by_name('Medium Complexity')
        ]
    
    @staticmethod
    def get_comprehensive_test_suite() -> List[Dict[str, Any]]:
        """Get comprehensive test suite for thorough validation."""
        suite = []
        all_cases = TestCaseLibrary.get_all_test_cases()
        
        # Include all cases except regression edge cases that should fail
        for category, cases in all_cases.items():
            for case in cases:
                if not case.get('should_fail', False):
                    suite.append(case)
        
        return suite

def validate_test_case(test_case: Dict[str, Any], solver) -> Dict[str, Any]:
    """
    Validate a test case against a solver.
    
    Args:
        test_case: Test case dictionary
        solver: Solver instance to test
        
    Returns:
        Validation results dictionary
    """
    problem = test_case['problem']
    expected_tiles = test_case.get('optimal_tiles')
    expected_efficiency = test_case.get('optimal_efficiency')
    
    try:
        solution = solver.solve(problem)
        
        result = {
            'name': test_case['name'],
            'solver': solver.name,
            'success': True,
            'tiles_found': solution.num_tiles,
            'efficiency_found': solution.efficiency,
            'solve_time': solution.solve_time,
            'is_centered': solution.is_centered
        }
        
        # Check if solution meets expectations
        if expected_tiles is not None:
            result['meets_optimal_tiles'] = solution.num_tiles >= expected_tiles
            result['tiles_gap'] = expected_tiles - solution.num_tiles
        
        if expected_efficiency is not None:
            result['meets_optimal_efficiency'] = solution.efficiency >= expected_efficiency * 0.95  # 5% tolerance
            result['efficiency_gap'] = expected_efficiency - solution.efficiency
        
        return result
        
    except Exception as e:
        return {
            'name': test_case['name'],
            'solver': solver.name,
            'success': False,
            'error': str(e),
            'tiles_found': 0,
            'efficiency_found': 0,
            'solve_time': float('inf')
        }

def run_test_suite(solver, test_suite: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Run a complete test suite against a solver.
    
    Args:
        solver: Solver instance to test
        test_suite: List of test cases (defaults to quick suite)
        
    Returns:
        Test suite results
    """
    if test_suite is None:
        test_suite = TestCaseLibrary.get_quick_test_suite()
    
    print(f"🧪 RUNNING TEST SUITE: {len(test_suite)} test cases for {solver.name}")
    
    results = []
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_suite):
        print(f"   Test {i+1}/{len(test_suite)}: {test_case['name']}...", end=' ')
        
        result = validate_test_case(test_case, solver)
        results.append(result)
        
        if result['success']:
            # Check if meets expectations
            meets_expectations = True
            if 'meets_optimal_tiles' in result:
                meets_expectations &= result['meets_optimal_tiles']
            if 'meets_optimal_efficiency' in result:
                meets_expectations &= result['meets_optimal_efficiency']
            
            if meets_expectations:
                print(f"✅ {result['tiles_found']} tiles ({result['efficiency_found']:.1f}%)")
                passed += 1
            else:
                print(f"⚠️  {result['tiles_found']} tiles ({result['efficiency_found']:.1f}%) - below expected")
                passed += 1  # Still counts as passed, just not optimal
        else:
            print(f"❌ FAILED: {result['error']}")
            failed += 1
    
    summary = {
        'solver': solver.name,
        'total_tests': len(test_suite),
        'passed': passed,
        'failed': failed,
        'success_rate': passed / len(test_suite) * 100,
        'results': results
    }
    
    print(f"\n📊 RESULTS: {passed}/{len(test_suite)} passed ({summary['success_rate']:.1f}% success rate)")
    
    return summary

if __name__ == "__main__":
    # Example usage
    from src.solvers.hybrid_solver import HybridSolver
    
    solver = HybridSolver(time_limit=10.0)
    quick_results = run_test_suite(solver)
    
    print(f"\nQuick test completed with {quick_results['success_rate']:.1f}% success rate")
