# COLLECTION FROM RECORD — one guide

Python utilities to **analyze** DXF collections and **prototype** bridge drawing structures. Lives beside your main TypeScript DXF studio in `artifacts/bridge-design-suite`.

## Prerequisites

- Python **3.10+** (Windows-friendly)
- Optional: AutoCAD / LibreCAD / any DXF viewer for output

## Quick start

```bash
cd "COLLECTION FROM RECORD"
pip install -r requirements.txt
python quick_start_demo.py
```

Or double-click **`run.bat`** and choose the menu option for the demo.

Demo output DXF files (when the script writes them) go under a folder such as **`output/`** next to these scripts—open in CAD to verify.

## Main scripts

| Script | Role |
|--------|------|
| `dxf_pattern_analyzer.py` | Scan DXF folders for patterns. |
| `common_drawing_forms.py` | Template-style geometry helpers. |
| `dxf_generator.py` | Build DXF content from structured data. |
| `drawing_extractor.py` | Pull drawings from mixed archives. |
| `enhanced_dxf_analyzer.py` | Deeper DXF inspection. |
| `analyze_drawings.py` | Batch analysis entry. |

## Parameters

Use `DrawingParameters` (see `common_drawing_forms.py` and `quick_start_demo.py`) for span, RTL/HFL, pier sizes, slab thickness, etc. Tweak demo functions before batch runs.

## Drawing forms checklist (reference)

Common bridge sheets this collection was designed around include: GAD, pier, abutment, deck rebar, cross section, wing wall, bed protection, anchorage, bearings, foundation, falsework, notes—implementation status varies by script; the **production** nine-sheet generator is in the main web app.

## Legal / engineering note

Generated geometry is for **office automation and drafting assistance**—always engineer-check and stamp per your authority having jurisdiction.
