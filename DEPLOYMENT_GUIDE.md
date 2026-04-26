# BridgeMaster Pro 2026 — Deployment & Usage Guide

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Streamlit Dashboard
```bash
python -m streamlit run src/app.py
```
Or use the batch file:
```bash
run_dashboard.bat
```

Dashboard opens at: **http://localhost:8501**

### 3. Generate Your First Drawing
1. Go to **General** tab → Enter Project Name, Client, Engineer
2. Go to **Spans & Deck** tab → Set NSPAN=3, SPAN=14m, CCBR=7.5m
3. Go to **Levels (NSL)** tab → Set NSL_L=100.0, NSL_C=99.5, NSL_R=99.8
4. Go to **Generate Outputs** tab → Click **⚡ Generate ALL Drawings**
5. Download DXF files → Open in AutoCAD/BricsCAD

---

## Features Overview

### Drawing Generator
- **GAD** (General Arrangement Drawing): Longitudinal section + Foundation plan with sloping terrain
- **Pier Details**: Elevation with cap, shaft, foundation, rebar
- **Deck Slab**: Cross-section with rebar, wearing coat, parapets
- **Wing Wall**: Elevation with splay angle
- **Abutment Details**: Left + Right abutment with foundation

### Smart Terrain Engine
- **NSL Sloping**: Automatically interpolates ground level from Left Abutment → Central Pier → Right Abutment
- **Foundation Levels**: Calculates excavation depth from local NSL
- **Terrain Visualization**: Shows slope percentage and 1:V ratio

### Professional Outputs
- **DXF Format**: AutoCAD R2018 (AC1032) compatible
- **Layers**: AIA/ISO standard (C-CONC, S-REBAR-MAIN, C-ANNO-DIMS, etc.)
- **Title Block**: Auto-scaled, dynamic project metadata
- **Dimensions**: Staggered, compact, professional proportions

### Design Checks (IRC Compliant)
- **L/D Ratio**: Span-to-depth validation (IRC:112)
- **Freeboard**: RTL-HFL clearance check (IRC:SP:13)
- **Foundation Depth**: Minimum 1.5m below scour level

---

## Command Line Usage

### Generate Drawings (Default Parameters)
```bash
python src/main.py generate
```
Output: `output/GAD_Generated.dxf`, `output/Pier_Details_Generated.dxf`, etc.

### Analyze COMPONENT_DRAWINGS_SORTED
```bash
python src/main.py analyze
```
Output: `output/analysis_report.json`, `output/analysis_summary.md`

### Run Validation Tests
```bash
python src/validate.py
```
Tests 6 bridge configurations; generates reports in `tests/output/`

---

## Parameter Reference

### General Tab
| Parameter | Default | Description |
|-----------|---------|-------------|
| Project Name | Standard Bridge Project | Project identifier |
| Drawing Number | GAD-001 | Drawing reference |
| Client | Client Name | Commissioning authority |
| Consultant | Consultant Name | Design firm |
| Engineer | Design Engineer | Responsible engineer |

### Spans & Deck Tab
| Parameter | Default | Description |
|-----------|---------|-------------|
| NSPAN | 3 | Number of spans |
| SPAN | 14.0 m | Clear span length |
| CCBR | 7.5 m | Carriageway width |
| SLBTHE | 0.45 m | Slab thickness |
| Wearing Coat | 0.075 m | Wearing coat thickness |
| Skew Angle | 0° | Skew angle |

### Substructure Tab
| Parameter | Default | Description |
|-----------|---------|-------------|
| PIERTW | 1.2 m | Pier top width |
| Pier Cap Width | 2.5 m | Pier cap width |
| Abutment Type | Cantilever | Cantilever / Counterfort / Gravity |
| Stem Thickness | 1.0 m | Abutment stem thickness |
| Toe Length | 1.5 m | Footing toe length |
| Heel Length | 2.5 m | Footing heel length |

### Foundation Tab
| Parameter | Default | Description |
|-----------|---------|-------------|
| Foundation Type | Open Foundation | Open / Pile Cap |
| FUTW | 4.0 m | Foundation width |
| FUTD | 2.0 m | Foundation depth below NSL |
| Foundation Thickness | 1.5 m | Raft/Pile cap thickness |

### Levels (NSL) Tab
| Parameter | Default | Description |
|-----------|---------|-------------|
| RTL | 100.5 m | Road top level |
| HFL | 98.2 m | High flood level |
| NSL_L | 100.0 m | NSL at left abutment |
| NSL_C | 99.5 m | NSL at central pier |
| NSL_R | 99.8 m | NSL at right abutment |
| Assume Linear Slope | ON | Interpolate terrain linearly |

---

## Excel Pre-Fill Format

Upload an Excel file with columns: **VALUE**, **VARIABLE**, **DESCRIPTION**

Example:
```
VALUE          | VARIABLE | DESCRIPTION
3              | NSPAN    | Number of spans
14.0           | SPAN1    | Span length
7.5            | CCBR     | Carriageway width
0.45           | SLBTHE   | Slab thickness
1.2            | PIERTW   | Pier top width
4.0            | FUTW     | Foundation width
2.0            | FUTD     | Foundation depth
100.5          | RTL      | Road top level
85.0           | DATUM    | Reference datum
```

---

## Troubleshooting

### Dashboard Won't Start
```bash
# Clear Streamlit cache
streamlit cache clear

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Run with verbose logging
streamlit run src/app.py --logger.level=debug
```

### DXF File Won't Open in AutoCAD
- Ensure AutoCAD version supports DXF R2018 (AC1032)
- Try opening with BricsCAD or LibreCAD (free alternatives)
- Check file size: should be 50-500 KB depending on complexity

### Dimension Text Overlapping
- This is fixed in Phase 2 revision (base_offset reduced)
- Regenerate with latest code: `git pull`

### NSL Terrain Not Showing
- Ensure "Assume Linear Slope" is checked
- Verify NSL values: NSL_L > NSL_C (downslope to pier)
- Check that NSL values are realistic (within 1-2m range)

---

## File Organization

```
BridgeMaster Pro/
├── src/
│   ├── app.py                    # Streamlit dashboard
│   ├── main.py                   # CLI entry point
│   ├── generators/
│   │   ├── dxf_builder.py        # Core DXF engine
│   │   ├── blocks.py             # Reusable CAD blocks
│   │   └── templates.py          # Drawing generators
│   ├── models/
│   │   └── components.py         # BridgeParameters
│   ├── modules/
│   │   ├── boq_engine.py         # BOQ calculations
│   │   ├── design_checks.py      # IRC checks
│   │   └── export_service.py     # Export handlers
│   ├── analyzer/                 # DXF analysis tools
│   └── reporting/                # Report generation
├── config/
│   ├── app_config.yaml           # Global settings
│   ├── layer_standards.yaml      # Layer definitions
│   └── component_rules.yaml      # Analysis rules
├── docs/
│   ├── USER_MANUAL.md            # Full user guide
│   ├── MARKETING_BROCHURE.md     # Product info
│   ├── PRICING_STRATEGY.md       # Licensing tiers
│   └── PROJECT_HISTORY.md        # Phase log
├── sample_projects/              # Example .brg files
├── output/                       # Generated drawings
├── COMPONENT_DRAWINGS_SORTED/    # Original drawing library
├── requirements.txt              # Python dependencies
├── run_dashboard.bat             # Quick-start batch file
└── README.md                     # Project overview
```

---

## Next Steps

1. **Generate Your First Project**: Follow Quick Start above
2. **Explore Sample Projects**: Open `sample_projects/*.brg` in the app
3. **Customize Parameters**: Adjust spans, widths, levels for your bridge
4. **Export & Use**: Download DXF → Open in AutoCAD → Modify as needed
5. **Validate**: Run `python src/validate.py` to test your parameters

---

## Support & Contact

**BridgeMaster Software Solutions**
- Email: contact@bridgemasterpro.com
- Phone: +91-XXXXXXXXXX
- GitHub: https://github.com/CRAJKUMARSINGH/Dwg-Dxf-Record-Keeper

---

**Version**: 1.0.0 (Release Candidate)  
**Last Updated**: April 2026  
**License**: Commercial (See PRICING_STRATEGY.md)
