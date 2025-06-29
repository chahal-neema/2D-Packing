# 🚀 How to Run the 2D Packing Visualizer

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Streamlit GUI
```bash
streamlit run streamlit_app_fixed.py
```

Or with custom settings:
```bash
streamlit run streamlit_app_fixed.py --server.port=8501 --server.address=0.0.0.0
```

### 3. Open in Browser
Navigate to: **http://localhost:8501**

---

## 🎯 Using the Interface

### Input Parameters
- **Container Dimensions**: Width and height of the container
- **Tile Dimensions**: Width and height of the tiles to pack
- **Allow Rotation**: Enable/disable tile rotation
- **Time Limit**: Maximum solving time (5-120 seconds)

### Preset Examples
- **40×40 with 24×16 (Pinwheel)**: Classic non-guillotine pattern
- **40×48 with 12×16**: Rectangular optimization 
- **40×48 with 10×10**: Square tile packing

### Multiple Solutions
Check **"Find All Optimal Solutions"** to discover different arrangements that achieve the same optimal tile count. Note:
- **Simple cases**: Often have only one optimal arrangement
- **Complex cases**: May have multiple equivalent solutions with different tile placements
- **Small problems**: More likely to have multiple optimal configurations

### Features
- 🎨 **Enhanced Visualization**: Color-coded tiles with labels
- 📊 **Detailed Metrics**: Efficiency, utilization, solve time
- 📜 **Solver Logs**: Real-time algorithm progress
- 📋 **Tile Positions**: Exact coordinates and orientations
- 🔄 **Multiple Solutions**: Find all optimal arrangements (when they exist)
- 🎯 **Solution Selector**: Browse through different optimal configurations

---

## 🧪 Testing Without GUI

Run the test script to verify components:
```bash
python3 test_streamlit_components.py
```

---

## 🔧 Technical Details

### Solvers Used
1. **Mathematical Solver**: Fast guillotine patterns
2. **Greedy Solver**: Heuristic placement strategies  
3. **Backtracking Solver**: Exhaustive small-scale search
4. **ILP Solver (OR-Tools)**: Optimal non-guillotine patterns

### Key Features
- **Pinwheel Pattern Detection**: Finds complex non-guillotine arrangements
- **Multi-tier Optimization**: Automatically escalates to more powerful solvers
- **Real-time Visualization**: Interactive matplotlib plots
- **Performance Metrics**: Comprehensive efficiency analysis

---

## 📦 Example Results

- **Case 1**: 40×48 with 12×16 tiles → **10/10 tiles (100% efficiency)**
- **Case 2**: 40×48 with 10×10 tiles → **16/19 tiles (83% efficiency)**  
- **Case 3**: 40×40 with 24×16 tiles → **4/4 tiles (96% efficiency) - PINWHEEL!**

The GUI successfully finds optimal solutions including complex pinwheel arrangements!