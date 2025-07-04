# Resilient Batch Packing Results Summary

## Processing Statistics

- **Total Rows**: 305
- **Processed Rows**: 305
- **Successful**: 288 (94.4%)
- **Failed**: 7 (2.3%)
- **Skipped (too small)**: 10 (3.3%)
- **Timeout**: 0 (0.0%)
- **Processing Time**: 1.40 hours
- **Average Rate**: 0.1 rows/second

## Configuration

- **Input File**: `items_grouped_by_rounded_len_width.csv`
- **Timeout per Group**: 120 seconds
- **Size Filter**: Groups with length or width < 4 inches are skipped
- **Max Solutions per Group**: 5 (arranged horizontally)

## Files Generated

- **Results CSV**: `results_pallet_40x48.csv`
- **Progress File**: `results_pallet_40x48.csv.progress`
- **Summary Report**: `results_pallet_40x48_summary.md`

## Resume Information

To resume processing from where it left off, run the same command.
The script will automatically detect the last processed row and continue.
