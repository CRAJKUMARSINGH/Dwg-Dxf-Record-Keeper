# ETERNAL_RESEARCH_CHILD — Bridge Engineering Autonomous Researcher

## Objective
The **Eternal Research Child** is a background automation layer designed to continuously evolve the **BridgeMaster Pro** parametric library. Its primary goal is to study the vast collection of legacy AutoCAD drawings (`.dwg` and `.dxf`) and propose refinements to the generative logic, ensuring the software achieves 100% parity with professional engineering standards.

In the context of the CAD Standardization Project, the daemon acts as a "silent bridge engineer" that identifies missing details, common dimensional patterns, and standard drafting nuances that the main generators might have missed.

## Way of Working

1.  **Continuous Scanning**: The daemon periodically (every 15 minutes) scans the `COMPONENT_DRAWINGS_SORTED/` and `COLLECTION FROM RECORD/` directories.
2.  **CAD Pattern Recognition**: It uses the internal `PatternMatcher` engine to analyze geometry inside legacy drawings, focusing on:
    *   **Geometric Proportions**: How heel/toe lengths vary with abutment height.
    *   **Dimensioning Styles**: Standard text heights and arrow placements used in different PWD circles.
    *   **Layer Usage**: Identifying repeated layer naming conventions for rebar and concrete.
3.  **Knowledge Consolidation**: It cross-references findings from different components (e.g., comparing Pier Cap details across 50 different projects).
4.  **Refinement Proposals**: Instead of automatically changing code, the daemon generates a **Refinement Proposal**.
    *   *Example*: "Proposal: Adjust the default chamfer logic for Pier Caps above 1.5m width to match the 1:3 ratio found in 80% of legacy records."
5.  **Interactive Feedback**: The user is prompted to approve or reject these proposals. Approved changes are queued for integration into the parametric templates (`src/generators/templates.py`).

## Future Roadmap
*   **LLM Integration**: Sending extracted CAD metadata to an LLM to generate improved descriptive text and engineering notes.
*   **Auto-Correction**: Automatically updating the `BridgeParameters` defaults based on statistical modes found in the research.
