# CAD Standardization Project: User Manual

## Overview
Welcome to the **Parametric Bridge CAD Generator**. This system takes engineering parameters (spans, widths, levels, NSL) and programmatically generates pristine, standardized AutoCAD DXF drawings with sloping terrain, professional title blocks, and full substructure detailing.

## Available Components
| Component | Description |
|-----------|-------------|
| **GAD** | General Arrangement Drawing — Longitudinal Section + Foundation Plan with terrain slope |
| **Pier Details** | Pier elevation with cap, shaft, foundation, and rebar |
| **Deck Slab** | Cross-section with rebar, wearing coat, haunches, parapets |
| **Wing Wall** | Wing wall elevation for both abutments with splay angle |
| **Abutment Details** | Standalone left + right abutment with foundation |

## Quick Start (Dashboard)

1. Double-click `run_dashboard.bat` in the root folder.
2. A browser window opens at `http://localhost:8501`.
3. Fill in parameters across the 6 tabs:
   - **General**: Project name, client, engineer
   - **Spans & Deck**: NSPAN, span length, carriageway width, slab thickness
   - **Substructure**: Pier width, abutment type (Cantilever/Counterfort/Gravity), wing wall
   - **Foundation**: Foundation type, width, depth, PCC offset
   - **Levels (NSL)**: RTL, HFL, NSL at Left/Center/Right abutments, terrain slope toggle
   - **Generate Outputs**: Select components or click "Generate ALL"
4. Click **Generate** → download the `.dxf` files.

### Excel Upload
You can pre-fill the dashboard from an Excel file (same format as `Bridge_GAD_Yogendra_Borse`):
- File should have columns: VALUE, VARIABLE, DESCRIPTION
- Supported variables: NSPAN, SPAN1, CCBR, SLBTHE, PIERTW, FUTW, FUTD, RTL, DATUM

## Command Line Usage

### Generate drawings (default parameters)
```bash
py src/main.py generate
```

### Run the full analyzer on COMPONENT_DRAWINGS_SORTED
```bash
py src/main.py analyze
```
This produces:
- `output/analysis_report.json` — detailed JSON with frequency tables
- `output/analysis_summary.md` — Markdown report with top-20 reusable details

### Run validation suite
```bash
py src/validate.py
```
Tests 6 different bridge configurations and generates a validation report.

### Apply reference styles to generated DXF
```bash
py apply_reference_dxf_style.py DRAWINGS_FROM_RAJKUMAR_DESIGNS output/dashboard
```

## Folder Structure
```
config/                          YAML configuration files
  app_config.yaml                Global paths & settings
  component_rules.yaml           Categorization rules
  layer_standards.yaml           Standard layer definitions
src/
  analyzer/                      DXF/DWG analysis engine
    ezdxf_parser.py              Enhanced parser (text/dim/hatch styles)
    pattern_matcher.py           Frequency counting & cross-component detection
    top20_identifier.py          Reusable detail ranking
    dwg_converter.py             ODA / odafc DWG conversion
  generators/                    Parametric drawing generators
    dxf_builder.py               Core DXF primitives + terrain + title block
    blocks.py                    Reusable blocks (bearing, pier cap, rebar, wing wall)
    templates.py                 Full-sheet assembly (GAD, Pier, Deck, Wing, Abutment)
  models/
    components.py                BridgeParameters Pydantic model
  reporting/
    reporter.py                  JSON + Markdown report generation
  app.py                         Streamlit dashboard
  main.py                        CLI entry point
  validate.py                    Validation suite
output/                          Generated reports & drawings
COMPONENT_DRAWINGS_SORTED/       Original drawing collection (23 categories)
DRAWINGS_FROM_RAJKUMAR_DESIGNS/  Reference style archive
```

## Key Features
- **Sloping Terrain**: NSL values at Left Abutment, Central Pier, and Right Abutment create a piecewise linear ground profile in the GAD Longitudinal Section.
- **Dynamic Abutment Types**: Switch between Cantilever, Counterfort, and Gravity abutments with automatic parameter show/hide.
- **Foundation Visibility**: Foundation depth, PCC layer, and pile caps are fully rendered below NSL.
- **Professional Title Block**: Auto-scaled with Project, Client, Engineer, Date, Drawing No, and realistic engineering scale.
- **Staggered Dimensions**: Automatic offset stacking prevents dimension text overlaps at large spans.
- **Standard Layers**: AIA/ISO compliant layer system (C-CONC, S-REBAR-MAIN, C-ANNO-DIMS, etc.)

## Adding a New Template

1. **Define Parameters**: Add new fields to `BridgeParameters` in `src/models/components.py`.
2. **Build Geometry**: Create a new static method in `src/generators/templates.py` (e.g., `generate_box_culvert(params)`).
3. **Use Blocks**: Leverage `DynamicBlocks` for rebar, bearings, foundations.
4. **Add to Dashboard**: In `src/app.py`, add a checkbox and wire it to the generator.
5. **Add to generate_all()**: Include in the `SheetTemplates.generate_all()` dict.

## Long-Term Maintenance
- **Layer Standards**: Update `config/layer_standards.yaml` when adopting new layer conventions.
- **Component Rules**: Update `config/component_rules.yaml` when adding new analysis categories.
- **Re-run Analyzer**: After adding drawings to `COMPONENT_DRAWINGS_SORTED/`, run `py src/main.py analyze` to refresh reports.
