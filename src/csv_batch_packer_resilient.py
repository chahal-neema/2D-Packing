#!/usr/bin/env python3
"""
Resilient CSV Batch Packer with Timeout and Horizontal Multiple Solutions
Processes grouped items CSV with 2-minute timeout per computation and horizontal solution layout.
"""

import csv
import json
import math
import sys
import os
import time
import signal
from typing import List, Dict, Any, Optional

from src.core.problem import PackingProblem
from src.solvers.hybrid_solver import HybridSolver
from src.core.geometry import center_solution

# Set a new field size limit
csv.field_size_limit(2**20)  # 1 MB

class TimeoutError(Exception):
    """Raised when computation exceeds timeout."""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutError("Computation timed out")


class ResilientBatchPacker:
    def __init__(self, input_file: str, output_file: str, progress_file: str = None, timeout_seconds: int = 120):
        self.input_file = input_file
        self.output_file = output_file
        self.progress_file = progress_file or f"{output_file}.progress"
        self.summary_file = output_file.replace('.csv', '_summary.md')
        self.timeout_seconds = timeout_seconds
        
        # Stats tracking
        self.total_rows = 0
        self.processed_rows = 0
        self.successful_rows = 0
        self.failed_rows = 0
        self.skipped_rows = 0
        self.timeout_rows = 0
        self.start_time = time.time()
        
    def count_total_rows(self) -> int:
        """Count total rows in input file (excluding header)."""
        print("📊 Counting total rows in input file...")
        with open(self.input_file, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            count = sum(1 for _ in reader)
        print(f"   Found {count:,} data rows to process")
        return count
    
    def get_last_processed_row(self) -> int:
        """Get the last successfully processed row number from progress file."""
        if not os.path.exists(self.progress_file):
            return 0
        
        try:
            with open(self.progress_file, 'r') as f:
                content = f.read().strip()
                if content:
                    return int(content)
        except (ValueError, IOError):
            pass
        return 0
    
    def update_progress(self, row_number: int):
        """Update the progress file with the last processed row."""
        try:
            with open(self.progress_file, 'w') as f:
                f.write(str(row_number))
        except IOError as e:
            print(f"⚠️  Warning: Could not update progress file: {e}")
    
    def setup_output_file(self, resume_from: int):
        """Setup the output file. If resuming, keep existing content."""
        # Base fieldnames - we'll dynamically add solution columns
        base_fieldnames = [
            "row_number", "rounded_length", "rounded_width", "item_count",
            "processing_time_ms", "status", "error_message"
        ]
        
        # We'll add solution fields dynamically: sol1_tiles, sol1_efficiency, sol1_positions, sol2_tiles, etc.
        
        # If not resuming, create new file with header (we'll write header when we know max solutions)
        return base_fieldnames
    
    def parse_bool(self, value: str) -> bool:
        """Parse string to boolean."""
        if value is None:
            return True
        value = value.strip().lower()
        return value in {"1", "true", "t", "yes", "y"}
    
    def round_up(self, value: str) -> int:
        """Round up a string value to integer."""
        return int(math.ceil(float(value)))
    
    def solve_group_with_timeout(self, row_data: dict, row_number: int) -> Dict[str, Any]:
        """Solve packing for a group of items with timeout protection."""
        start_time = time.time()
        
        try:
            # Extract group data
            rounded_length = float(row_data.get("rounded_length", 0))
            rounded_width = float(row_data.get("rounded_width", 0))
            items_json = row_data.get("items", "[]")
            
            # Parse items list
            try:
                items_list = json.loads(items_json)
            except json.JSONDecodeError:
                try:
                    # Try with ast.literal_eval for Python-style lists
                    import ast
                    items_list = ast.literal_eval(items_json)
                except (ValueError, SyntaxError):
                    items_list = []
            
            item_count = len(items_list)
            
            # Check minimum size requirement (4 inches for length and width)
            if rounded_length < 4.0 or rounded_width < 4.0:
                return {
                    "row_number": row_number,
                    "rounded_length": rounded_length,
                    "rounded_width": rounded_width,
                    "item_count": item_count,
                    "processing_time_ms": round((time.time() - start_time) * 1000, 2),
                    "status": "skipped_too_small",
                    "error_message": f"Group too small: length={rounded_length:.1f}in, width={rounded_width:.1f}in (minimum 4in required)",
                    "solutions": []
                }
            
            if item_count == 0:
                return {
                    "row_number": row_number,
                    "rounded_length": rounded_length,
                    "rounded_width": rounded_width,
                    "item_count": item_count,
                    "processing_time_ms": round((time.time() - start_time) * 1000, 2),
                    "status": "skipped_empty",
                    "error_message": "No items in group",
                    "solutions": []
                }
            
            # Set up timeout
            if os.name != 'nt':  # Unix/Linux systems
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(self.timeout_seconds)
            
            try:
                # Find multiple solutions for this tile size
                solutions = self.find_multiple_solutions(rounded_length, rounded_width, item_count)
                
                if os.name != 'nt':  # Cancel timeout
                    signal.alarm(0)
                
                return {
                    "row_number": row_number,
                    "rounded_length": rounded_length,
                    "rounded_width": rounded_width,
                    "item_count": item_count,
                    "processing_time_ms": round((time.time() - start_time) * 1000, 2),
                    "status": "success" if solutions else "no_solution",
                    "error_message": "" if solutions else "No suitable packing arrangements found",
                    "solutions": solutions
                }
                
            except TimeoutError:
                if os.name != 'nt':
                    signal.alarm(0)
                return {
                    "row_number": row_number,
                    "rounded_length": rounded_length,
                    "rounded_width": rounded_width,
                    "item_count": item_count,
                    "processing_time_ms": round((time.time() - start_time) * 1000, 2),
                    "status": "timeout",
                    "error_message": f"Computation exceeded {self.timeout_seconds} seconds timeout",
                    "solutions": []
                }
            
        except Exception as e:
            if os.name != 'nt':
                signal.alarm(0)
            return {
                "row_number": row_number,
                "rounded_length": row_data.get("rounded_length", 0),
                "rounded_width": row_data.get("rounded_width", 0),
                "item_count": 0,
                "processing_time_ms": round((time.time() - start_time) * 1000, 2),
                "status": "error",
                "error_message": str(e),
                "solutions": []
            }
    
    def find_multiple_solutions(self, tile_w: float, tile_h: float, item_count: int) -> List[Dict[str, Any]]:
        """Find multiple packing solutions for the given tile dimensions."""
        tile_w = int(tile_w)
        tile_h = int(tile_h)
        
        if tile_w <= 0 or tile_h <= 0:
            return []
        
        # Standard pallet dimensions
        pallet_w = 40  # inches
        pallet_h = 48  # inches
        
        # Try both orientations of the tiles on the standard pallet
        container_configs = [
            (pallet_w, pallet_h),   # Standard pallet orientation
            (pallet_h, pallet_w),   # Rotated pallet orientation
        ]
        
        solutions = []
        best_efficiency = 0
        
        for i, (container_w, container_h) in enumerate(container_configs):
            # Skip if container is smaller than the item
            if container_w < tile_w or container_h < tile_h:
                continue
            
            try:
                problem = PackingProblem(
                    container_w=container_w,
                    container_h=container_h,
                    tile_w=tile_w,
                    tile_h=tile_h,
                    allow_rotation=True,
                )
                
                solver = HybridSolver()
                solution = solver.solve(problem)
                
                # Only keep solutions that are reasonably good
                if solution.num_tiles > 0 and solution.efficiency >= best_efficiency * 0.8:
                    if solution.efficiency > best_efficiency:
                        best_efficiency = solution.efficiency
                    
                    # Center the solution
                    centered_positions = center_solution(
                        solution.tile_positions, 
                        container_w, 
                        container_h
                    )
                    
                    # Calculate metrics
                    if centered_positions:
                        min_x = min(x for x, y, w, h, o in centered_positions)
                        min_y = min(y for _, y, w, h, o in centered_positions)
                        max_x = max(x + w for x, y, w, h, o in centered_positions)
                        max_y = max(y + h for _, y, w, h, o in centered_positions)
                        used_width = max_x - min_x
                        used_height = max_y - min_y
                        is_centered = abs((min_x + max_x) / 2 - container_w / 2) < 0.5 and abs((min_y + max_y) / 2 - container_h / 2) < 0.5
                    else:
                        used_width = used_height = 0
                        is_centered = False
                    
                    # Count orientations
                    orientations = {}
                    for _, _, _, _, orientation in centered_positions:
                        orientations[orientation] = orientations.get(orientation, 0) + 1
                    
                    solution_data = {
                        "container_w": container_w,
                        "container_h": container_h,
                        "tiles_placed": solution.num_tiles,
                        "efficiency": round(solution.efficiency, 2),
                        "used_width": used_width,
                        "used_height": used_height,
                        "is_centered": is_centered,
                        "original_tiles": orientations.get("original", 0),
                        "rotated_tiles": orientations.get("rotated", 0),
                        "solver_used": solution.solver_name,
                        "positions": centered_positions,
                    }
                    
                    solutions.append(solution_data)
                    
            except Exception as e:
                # Continue trying other configurations
                continue
        
        # Sort solutions by efficiency (best first) and limit to top 5
        solutions.sort(key=lambda x: x["efficiency"], reverse=True)
        return solutions[:5]
    
    def flatten_result_for_csv(self, result: Dict[str, Any], max_solutions: int = 5) -> Dict[str, Any]:
        """Flatten result with multiple solutions into a single row with horizontal layout."""
        flat_result = {
            "row_number": result["row_number"],
            "rounded_length": result["rounded_length"],
            "rounded_width": result["rounded_width"],
            "item_count": result["item_count"],
            "processing_time_ms": result["processing_time_ms"],
            "status": result["status"],
            "error_message": result["error_message"],
        }
        
        # Add solution columns horizontally
        solutions = result.get("solutions", [])
        for i in range(max_solutions):
            prefix = f"sol{i+1}_"
            
            if i < len(solutions):
                sol = solutions[i]
                flat_result[f"{prefix}container_w"] = sol["container_w"]
                flat_result[f"{prefix}container_h"] = sol["container_h"]
                flat_result[f"{prefix}tiles_placed"] = sol["tiles_placed"]
                flat_result[f"{prefix}efficiency"] = sol["efficiency"]
                flat_result[f"{prefix}used_width"] = sol["used_width"]
                flat_result[f"{prefix}used_height"] = sol["used_height"]
                flat_result[f"{prefix}is_centered"] = sol["is_centered"]
                flat_result[f"{prefix}original_tiles"] = sol["original_tiles"]
                flat_result[f"{prefix}rotated_tiles"] = sol["rotated_tiles"]
                flat_result[f"{prefix}solver_used"] = sol["solver_used"]
                flat_result[f"{prefix}positions"] = json.dumps(sol["positions"])
            else:
                # Empty solution columns
                flat_result[f"{prefix}container_w"] = ""
                flat_result[f"{prefix}container_h"] = ""
                flat_result[f"{prefix}tiles_placed"] = ""
                flat_result[f"{prefix}efficiency"] = ""
                flat_result[f"{prefix}used_width"] = ""
                flat_result[f"{prefix}used_height"] = ""
                flat_result[f"{prefix}is_centered"] = ""
                flat_result[f"{prefix}original_tiles"] = ""
                flat_result[f"{prefix}rotated_tiles"] = ""
                flat_result[f"{prefix}solver_used"] = ""
                flat_result[f"{prefix}positions"] = ""
        
        return flat_result
    
    def get_all_fieldnames(self, max_solutions: int = 5) -> List[str]:
        """Get all fieldnames including solution columns."""
        base_fields = [
            "row_number", "rounded_length", "rounded_width", "item_count",
            "processing_time_ms", "status", "error_message"
        ]
        
        solution_fields = []
        for i in range(max_solutions):
            prefix = f"sol{i+1}_"
            solution_fields.extend([
                f"{prefix}container_w", f"{prefix}container_h", f"{prefix}tiles_placed",
                f"{prefix}efficiency", f"{prefix}used_width", f"{prefix}used_height",
                f"{prefix}is_centered", f"{prefix}original_tiles", f"{prefix}rotated_tiles",
                f"{prefix}solver_used", f"{prefix}positions"
            ])
        
        return base_fields + solution_fields
    
    def append_result(self, result: Dict[str, Any], fieldnames: List[str]):
        """Append a single result to the output file."""
        try:
            # Flatten the result for horizontal layout
            flat_result = self.flatten_result_for_csv(result)
            
            # Append to CSV file
            with open(self.output_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writerow(flat_result)
            
            return True
        except Exception as e:
            print(f"❌ Error writing result to file: {e}")
            return False
    
    def print_progress(self, row_number: int, result: Dict[str, Any]):
        """Print progress information."""
        elapsed = time.time() - self.start_time
        rate = self.processed_rows / elapsed if elapsed > 0 else 0
        eta_seconds = (self.total_rows - self.processed_rows) / rate if rate > 0 else 0
        
        status = result["status"]
        if status == "success":
            status_emoji = "✅"
        elif status == "no_solution":
            status_emoji = "⚠️"
        elif status == "skipped_too_small":
            status_emoji = "⏭️"
        elif status == "timeout":
            status_emoji = "⏱️"
        else:
            status_emoji = "❌"
        
        solution_count = len(result.get("solutions", []))
        
        print(f"{status_emoji} Row {row_number:,}/{self.total_rows:,} | "
              f"Success: {self.successful_rows:,} | Failed: {self.failed_rows:,} | "
              f"Skipped: {self.skipped_rows:,} | Timeout: {self.timeout_rows:,} | "
              f"Rate: {rate:.1f}/s | ETA: {eta_seconds/60:.1f}m | "
              f"Solutions: {solution_count} | Items: {result.get('item_count', 'N/A')}")
    
    def create_summary_report(self):
        """Create a summary report of the processing."""
        elapsed = time.time() - self.start_time
        
        with open(self.summary_file, "w") as f:
            f.write("# Resilient Batch Packing Results Summary\n\n")
            f.write(f"## Processing Statistics\n\n")
            f.write(f"- **Total Rows**: {self.total_rows:,}\n")
            f.write(f"- **Processed Rows**: {self.processed_rows:,}\n")
            f.write(f"- **Successful**: {self.successful_rows:,} ({self.successful_rows/max(self.processed_rows,1)*100:.1f}%)\n")
            f.write(f"- **Failed**: {self.failed_rows:,} ({self.failed_rows/max(self.processed_rows,1)*100:.1f}%)\n")
            f.write(f"- **Skipped (too small)**: {self.skipped_rows:,} ({self.skipped_rows/max(self.processed_rows,1)*100:.1f}%)\n")
            f.write(f"- **Timeout**: {self.timeout_rows:,} ({self.timeout_rows/max(self.processed_rows,1)*100:.1f}%)\n")
            f.write(f"- **Processing Time**: {elapsed/3600:.2f} hours\n")
            f.write(f"- **Average Rate**: {self.processed_rows/elapsed:.1f} rows/second\n\n")
            
            f.write(f"## Configuration\n\n")
            f.write(f"- **Input File**: `{self.input_file}`\n")
            f.write(f"- **Timeout per Group**: {self.timeout_seconds} seconds\n")
            f.write(f"- **Size Filter**: Groups with length or width < 4 inches are skipped\n")
            f.write(f"- **Max Solutions per Group**: 5 (arranged horizontally)\n\n")
            
            f.write(f"## Files Generated\n\n")
            f.write(f"- **Results CSV**: `{self.output_file}`\n")
            f.write(f"- **Progress File**: `{self.progress_file}`\n")
            f.write(f"- **Summary Report**: `{self.summary_file}`\n\n")
            
            f.write(f"## Resume Information\n\n")
            f.write(f"To resume processing from where it left off, run the same command.\n")
            f.write(f"The script will automatically detect the last processed row and continue.\n")
    
    def process(self):
        """Main processing method."""
        print(f"🚀 Starting resilient batch packing...")
        print(f"   Input: {self.input_file}")
        print(f"   Output: {self.output_file}")
        print(f"   Progress: {self.progress_file}")
        print(f"   Timeout: {self.timeout_seconds} seconds per group")
        
        # Count total rows
        self.total_rows = self.count_total_rows()
        
        # Check for resume
        resume_from = self.get_last_processed_row()
        if resume_from > 0:
            print(f"🔄 Resuming from row {resume_from:,}")
            self.processed_rows = resume_from
            # Count existing stats by reading output file
            if os.path.exists(self.output_file):
                with open(self.output_file, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        status = row.get('status', '')
                        if status == 'success':
                            self.successful_rows += 1
                        elif status == 'skipped_too_small':
                            self.skipped_rows += 1
                        elif status == 'timeout':
                            self.timeout_rows += 1
                        else:
                            self.failed_rows += 1
        else:
            print(f"🆕 Starting fresh processing")
        
        # Setup output file
        fieldnames = self.get_all_fieldnames()
        
        # Create header if starting fresh
        if resume_from == 0:
            with open(self.output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
        
        # Process rows
        try:
            with open(self.input_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                
                # Skip to resume point
                current_row = 0
                for row in reader:
                    current_row += 1
                    
                    # Skip already processed rows
                    if current_row <= resume_from:
                        continue
                    
                    # Process this row
                    try:
                        result = self.solve_group_with_timeout(row, current_row)
                        
                        # Append result immediately
                        if self.append_result(result, fieldnames):
                            self.processed_rows += 1
                            
                            status = result["status"]
                            if status == "success":
                                self.successful_rows += 1
                            elif status == "skipped_too_small":
                                self.skipped_rows += 1
                            elif status == "timeout":
                                self.timeout_rows += 1
                            else:
                                self.failed_rows += 1
                            
                            # Update progress
                            self.update_progress(current_row)
                            
                            # Print progress every 10 rows or if it's the last row
                            if current_row % 10 == 0 or current_row == self.total_rows:
                                self.print_progress(current_row, result)
                        else:
                            print(f"❌ Failed to write result for row {current_row}")
                            
                    except KeyboardInterrupt:
                        print(f"\n🛑 Processing interrupted by user at row {current_row}")
                        break
                    except Exception as e:
                        print(f"❌ Unexpected error processing row {current_row}: {e}")
                        self.failed_rows += 1
                        continue
        
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            return False
        
        # Create summary
        self.create_summary_report()
        
        print(f"\n🎉 Processing completed!")
        print(f"   Total processed: {self.processed_rows:,}/{self.total_rows:,}")
        print(f"   Successful: {self.successful_rows:,}")
        print(f"   Failed: {self.failed_rows:,}")
        print(f"   Skipped (too small): {self.skipped_rows:,}")
        print(f"   Timeout: {self.timeout_rows:,}")
        print(f"   Results saved to: {self.output_file}")
        print(f"   Summary saved to: {self.summary_file}")
        
        return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python csv_batch_packer_resilient.py <input.csv> <output.csv> [progress_file] [timeout_seconds]")
        print("\nFeatures:")
        print("- Processes grouped items CSV one row at a time")
        print("- 2-minute timeout per group computation (configurable)")
        print("- Multiple solutions arranged horizontally in output")
        print("- Appends results immediately (no data loss on crash)")
        print("- Automatic resume capability from last processed row")
        print("- Progress tracking and ETA estimation")
        print("- Detailed error reporting and statistics")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    progress_file = sys.argv[3] if len(sys.argv) > 3 else None
    timeout_seconds = int(sys.argv[4]) if len(sys.argv) > 4 else 120

    # Validate input file
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    # Create and run the packer
    packer = ResilientBatchPacker(input_file, output_file, progress_file, timeout_seconds)
    success = packer.process()
    
    sys.exit(0 if success else 1)