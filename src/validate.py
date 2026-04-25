import sys
from pathlib import Path

# Add current dir to sys.path so modules can be found
sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.components import BridgeParameters
from generators.templates import SheetTemplates

def validate_components():
    base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / "output" / "validation"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    test_cases = [
        {"name": "Standard_14m", "span": 14.0, "width": 7.5, "pier_width": 1.2},
        {"name": "Long_Span_24m", "span": 24.0, "width": 8.5, "pier_width": 1.5},
        {"name": "Short_Span_8m", "span": 8.0, "width": 5.5, "pier_width": 1.0},
    ]
    
    results = []
    
    for case in test_cases:
        params = BridgeParameters(
            project_name=f"Validation - {case['name']}",
            span_length=case["span"],
            carriage_width=case["width"],
            pier_width=case["pier_width"]
        )
        
        # Validate Pier
        pier_builder = SheetTemplates.generate_pier_details(params)
        pier_path = output_dir / f"Pier_{case['name']}.dxf"
        pier_builder.save(pier_path)
        
        # Validate Deck Slab
        deck_builder = SheetTemplates.generate_deck_slab_details(params)
        deck_path = output_dir / f"DeckSlab_{case['name']}.dxf"
        deck_builder.save(deck_path)
        
        results.append(f"- Generated {case['name']} successfully (Span: {case['span']}m, Pier Width: {case['pier_width']}m)")
        
    return results

if __name__ == "__main__":
    print("Running validation...")
    res = validate_components()
    for r in res:
        print(r)
    print("Validation complete.")
