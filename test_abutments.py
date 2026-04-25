"""
Abutment Test Script
====================
Generates 3 GAD drawings, each with a different abutment type:
1. Cantilever
2. Gravity
3. Counterfort
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.bridge_schema import BridgeProject, BridgeType
from generators.templates import SheetTemplates

def generate_gad_test(abut_type: str):
    print(f"Generating GAD for Abutment Type: {abut_type}...")
    
    # Setup project
    project = BridgeProject(bridge_type=BridgeType.RCC_SLAB)
    project.metadata.project_name = f"GAD Test - {abut_type}"
    project.substructure.abutment_type = abut_type
    
    # If gravity, set some specific params (if they exist in schema or mapper)
    # The mapper might handle the conversion to the old block params.
    
    try:
        # Generate sheets
        drawings = SheetTemplates.generate_from_project(project)
        
        # We only want the GAD (usually named "GAD_and_Elevation" or similar)
        gad_found = False
        for name, builder in drawings.items():
            if "GAD" in name or "Elevation" in name:
                out_path = Path(f"GAD_{abut_type}.dxf")
                builder.save(out_path)
                print(f"[OK] Saved {out_path}")
                gad_found = True
                break
        
        if not gad_found:
            print(f"[WARN] GAD sheet not found in generated drawings for {abut_type}")
            
    except Exception as e:
        print(f"[FAIL] Error generating {abut_type}: {e}")

if __name__ == "__main__":
    abut_types = ["Cantilever", "Gravity", "Counterfort"]
    
    for at in abut_types:
        generate_gad_test(at)
        
    print("\n[DONE] Check the current directory for GAD_*.dxf files.")
