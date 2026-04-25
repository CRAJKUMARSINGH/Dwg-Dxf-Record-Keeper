# CAD Standardization Project: User Manual

## Overview
Welcome to the Parametric Bridge CAD Generator. This system takes engineering parameters (spans, widths, levels) and programmatically generates pristine, standardized AutoCAD DXF drawings. 

## Quick Start
The easiest way to generate drawings is using the interactive dashboard.

1. Double-click the `run_dashboard.bat` file in the root folder.
2. A browser window will open displaying the Streamlit Dashboard.
3. Enter your project dimensions in the left sidebar (Span, Skew, RTL, etc.).
4. Select the components you want to generate.
5. Click **Generate DXF Drawings**.
6. Click the Download buttons to save the `.dxf` files directly to your machine.

## Folder Structure
- `config/`: Contains `app_config.yaml` and `component_rules.yaml`. You can update paths or rules here.
- `src/`: The core Python source code.
  - `src/models/components.py`: This is where the engineering variables (like `BridgeParameters`) are defined.
  - `src/generators/blocks.py`: Contains the individual parametric routines (Rebar, Bearings).
  - `src/generators/templates.py`: Assembles the blocks into full sheets (GAD, Piers).
- `output/`: Raw DXFs are saved here if you run the tool via command line.
- `COMPONENT_DRAWINGS_SORTED/`: The original collection of manual drawings.

## Command Line Usage
If you prefer automation or batch scripting, you can use the CLI:
```bash
py src/main.py generate
```
*(Note: To change dimensions in CLI mode, edit the default parameters initialized in `src/main.py` -> `run_generation`)*

## Long-Term Maintenance Plan
As a Civil Engineer, your design codes will evolve. Here is how to maintain this library:

**Adding a New Template (e.g., Box Culvert)**
1. **Define the Data:** If the Box Culvert requires new parameters (e.g., `wall_thickness`), add them to `BridgeParameters` in `src/models/components.py`.
2. **Build the Geometry:** Open `src/generators/templates.py`. Add a new static method like `def generate_box_culvert(params) -> DXFBuilder:`.
3. **Assemble Blocks:** Use the `builder.add_polyline()` and `DynamicBlocks.draw_rebar_with_hooks()` functions to code the geometry.
4. **Expose to UI:** Open `src/app.py`, add a new checkbox for the Culvert, and tie it to the download button.

By isolating the geometry drawing into Python functions, you eliminate the risk of CAD layer corruption, block scaling errors, and dimension snapping mistakes common in manual drafting.
