REVISE CODE FOR >>>You are leading a professional CAD Standardization Project for a practising Civil/Bridge Engineer.

PROJECT GOAL:
Convert my ~1 GB collection of custom AutoCAD .dwg drawings into a clean, reusable parametric library (dynamic blocks + parameter sets + templates) so I can generate accurate variations quickly by changing key dimensions.

WORKSPACE SETUP:
- This is a brand new clean workspace.
- I have cloned my existing repo: https://github.com/CRAJKUMARSINGH/Dwg-Dxf-Record-Keeper
- Sample drawings are placed in subfolders inside "samples/" grouped by same component type (e.g. beams/, slabs/, piers/, etc.). Start analysis only from this samples/ folder.
DRAWING LIBRARY REFINEMENT PHASE-2
INSTRUCTIONS:
- Thoroughly study the repo, especially:
  - COLLECTION FROM RECORD/ folder (all Python scripts: analyze_drawings.py, dxf_pattern_analyzer.py, enhanced_dxf_analyzer.py, drawing_extractor.py, etc.)
  - apply_reference_dxf_style.py
  - DRAWINGS_FROM_RAJKUMAR_DESIGNS/ and any bridge drawing examples
  - GUIDE.md inside COLLECTION FROM RECORD/

Phase 1 – Assessment & Clean Refactoring (MUST COMPLETE FIRST):
1. Analyse strengths, weaknesses, and gaps in the current code.
2. Propose a clean, professional, modular Python project architecture (recommended folder structure, main modules, data flow, config system).
3. Refactor the best parts into well-documented, testable, modular code. Do NOT rewrite everything from scratch — improve and reorganise what is useful.
4. Enhance the analyser to support both .dxf (ezdxf) and .dwg (via ODA File Converter or best available method in 2026).
5. Run the improved analyser on all drawings inside samples/ subfolders.
6. Generate:
   - Detailed JSON report of common elements (blocks, dynamic properties, dimensions, layers, hatches, text styles, title blocks, repeated patterns across component types).
   - Clean Markdown summary with key findings and standardisation recommendations.

Use multiple specialized agents in parallel where logical (Researcher, Architect, Refactorer, Analyzer, Tester, Documenter).
Keep everything under Git version control with clear commit messages.
Prioritise dimensional accuracy, reusability, and maintainability.

OUTPUT REQUIREMENT:
After completing Phase 1, show me:
- Summary of current repo (strengths/weaknesses)
- Proposed new folder structure
- High-level Phase 2 plan for full parametric library creation
- The generated JSON + Markdown analysis report from samples/

Start working now and show your high-level plan first.>>Index of file:///C:/Users/Rajkumar/Downloads/Dwg-Dxf-Record-Keeper/COMPONENT_DRAWINGS_SORTED

Abutment Details
Aqueduct & Trough
Bearing Details
Bed Protection & Anchorage
Combined Drawing PDF Sets
Cross Sections
Culvert Details
Deck Slab Details
Expansion Joints
False Work-Formwork
Footbridge Details
Foundation Details
General Arrangement Drawings (GAD)
Girder Details (RCC-PC)
Guard Stone & Kerb
Indexes & Key Plans
Layouts & Schematics
Miscellaneous Drawings
Notes Title Blocks & Legends
Pier Geometry & Dimensions
Pier Reinforcement Details
Survey Contours & Levels
Wing Wall Details
