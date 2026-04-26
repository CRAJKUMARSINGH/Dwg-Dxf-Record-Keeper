# BridgeMaster Pro — User Manual & Documentation (Phase 5)

## Overview
Welcome to **BridgeMaster Pro 2026** (formerly BESS). This system takes engineering parameters (spans, widths, levels, NSL) and programmatically generates pristine, standardized AutoCAD DXF drawings with sloping terrain, professional title blocks, and full substructure detailing. It replaces the fragmented workflow of Excel sheets + Manual CAD with a single integrated professional desktop environment.

### Target Savings
- **Time**: Reduce GAD/Slab drawing time from 2 days to 5 minutes.
- **Accuracy**: Eliminates manual BOQ errors which cost lakhs in site wastage.
- **Cost**: Standardizes PWD/NHAI submissions, reducing rework.

---

## Key Modules

### Module 1: Drawing Generator
Generates high-fidelity DXF drawings for:
- General Arrangement Drawings (GAD) — Longitudinal Section + Foundation Plan with terrain slope
- Pier Details — Pier elevation with cap, shaft, foundation, and rebar
- Deck Slab — Cross-section with rebar, wearing coat, haunches, parapets
- Wing Wall — Wing wall elevation for both abutments with splay angle
- Abutment Details — Standalone left + right abutment with foundation
- Box Culvert Sections & T-Beam Cross Sections

### Module 2: Bridge Types
The software currently supports:
- **RCC Slab Bridge**: Standard minor bridges.
- **T-Beam Bridge**: Girder-based structures.
- **Box Culvert**: For small drainage/cross-drainage works.
- *Coming Soon*: PSC Girder, ROB/RUB, Foot Over Bridge.

### Module 3: Parameter System
- **Project Info**: Manage metadata (Client, Location, Designed By).
- **Geometry**: Define number of spans, lengths, and widths.
- **Levels (NSL)**: Input topography for sloping terrain generation.
- **Substructure**: Choose abutment types (Cantilever/Gravity) and Pier dimensions.
- **Foundation**: Set depth, width, and raft thickness.

### Module 4: BOQ & Design
- **One-Click BOQ**: Calculates Concrete (m3), Steel (MT), and Excavation (m3) instantly.
- **Excel Export**: Export the BOQ directly to a formatted spreadsheet for tendering.
- **Design Checks**: Real-time warnings if L/D ratios or freeboards violate IRC:112 or IRC:SP:13 guidelines.

---

## Operating the Software

### Professional Desktop App (Recommended)
**Installation & Setup (Phase 5)**:
1. Ensure Python 3.10+ is installed.
2. Run `pip install -r requirements.txt` to install all dependencies (`PySide6`, `ezdxf`, `reportlab`, `xlsxwriter`, etc.).
3. To start the app, run `py main_app.py` or launch the built `.exe`.
4. The **HOME** tab allows you to create a **New Project** or **Open** existing `.brg` files (such as `samples/RCC_Slab_Demo.brg`).
2. The **HOME** tab allows you to create a **New Project** or **Open** existing `.brg` files.
3. Select the **Bridge Type** from the dropdown (RCC Slab, T-Beam, etc.).
4. Use the **Sidebar** to navigate through:
   - **Project Info**: Client and location details.
   - **Bridge Geometry**: NSPAN, span length, carriageway width.
   - **Foundation**: Set width, depth, and raft thickness.
   - **Levels & NSL**: Input RTL, HFL, and terrain data for the sloping ground engine.
5. **Real-time Preview**: The central viewport updates instantly as you change parameters.
6. **Design Audit**: The Status Bar displays real-time warnings (e.g., L/D ratio failures).
7. Go to the **DRAWING** tab to:
   - **Generate GAD**: Outputs professional Elevation and Plan.
   - **Generate All Sheets**: Produces GAD, Pier, Deck Slab, and Abutment details in one click.
8. Go to **BOQ / DESIGN** tab to:
   - **Calculate Quantities**: View concrete, steel, and earthwork volumes.
   - **Export to Excel**: Get a formatted bill of quantities.
   - **Export PDF Dossier**: Generate a complete project report with design checks.

### Web Dashboard (Streamlit)
1. Double-click `run_dashboard.bat`.
2. A browser window opens at `http://localhost:8501`.
3. Follow the same parameter input workflow as the desktop app.

### Command Line Usage
**Generate drawings (default parameters)**:
```bash
py src/main.py generate
```

**Build Standalone Windows EXE**:
```bash
py build_exe.py
```
This uses Nuitka to compile the application into a standalone executable in the `dist/` folder.

**Run the full analyzer on COMPONENT_DRAWINGS_SORTED**:
```bash
py src/main.py analyze
```
This produces detailed JSON reports and markdown summaries of reusable CAD blocks.

**Run validation suite**:
```bash
py src/validate.py
```
Tests 6 different bridge configurations.

---

## Autonomous Research (ETERNAL_RESEARCH_CHILD)
The project includes a dedicated background service (`ETERNAL_RESEARCH_CHILD`) that runs periodically to study legacy project files in `COMPONENT_DRAWINGS_SORTED/`. It identifies drafting patterns and proposes refinements to the generative logic to ensure 100% engineering parity with professional office standards. 

See `ETERNAL_RESEARCH_CHILD.md` for technical details.

---

## Pricing Strategy & Support
- **Individual**: ₹45,000 /yr (RCC Slab + Box Culvert)
- **Professional**: ₹1,20,000 /yr (All Types + PDF Reports)
- **Enterprise**: ₹5,00,000 /yr (Multi-user + API)
- **Education**: ₹5,000 /yr (Watermarked)

**Contact for a Demo:** BridgeMaster Software Solutions
*Empowering engineers, building the future.*
