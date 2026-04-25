# Bridge Engineering Software Suite — User Manual

## 1. Introduction
The **Bridge Engineering Software Suite (BESS)** is a professional desktop application designed for Civil and Bridge Engineers to automate the generation of CAD drawings, quantity estimates (BOQ), and IRC-compliant design checks.

## 2. Key Modules

### Module 1: Drawing Generator
Generates high-fidelity DXF drawings for:
- General Arrangement Drawings (GAD)
- Longitudinal Sections & Plan Views
- Pier & Abutment Details
- Deck Slab Reinforcement
- Box Culvert Sections
- T-Beam Cross Sections

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

## 3. Workflow

1.  **Launch**: Run `main_app.exe`.
2.  **Set Type**: Choose the Bridge Type in the **HOME** tab.
3.  **Input Data**: Navigate the **Sidebar** to enter Geometry, Levels, and Substructure details.
4.  **Live Preview**: Watch the 2D Section update in the center viewport.
5.  **Audit**: Check the **Status Bar** for design warnings.
6.  **Calculate**: Go to the **BOQ** tab and click **Calculate Quantities**.
7.  **Generate**: Go to the **DRAWING** tab and click **Generate All Sheets**.

## 4. Troubleshooting
- **Matplotlib Error**: Ensure your Windows environment has the latest VC++ redistributables.
- **DXF Viewer**: Generated files are standard DXF R12, compatible with AutoCAD, ZWCAD, and BricsCAD.
- **Project Files**: Save your work as `.brg` files to resume later.

---
© 2026 RKS Engineering Suite. Built for the Modern Engineer.
