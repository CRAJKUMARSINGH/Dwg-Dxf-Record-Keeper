"""
Quick Start Demo - Complete Bridge Drawing Generation
Demonstrates the full workflow from parameters to DXF files.

Author: For Rajkumar Singh Chauhan
Date: 2026-04-18
"""

from pathlib import Path
from common_drawing_forms import CommonDrawingForms, DrawingParameters
from dxf_generator import DXFGenerator


def generate_complete_bridge_set():
    """Generate a complete set of bridge drawings."""
    
    print("=" * 80)
    print("BRIDGE DRAWING GENERATION - QUICK START DEMO")
    print("=" * 80)
    
    # Step 1: Define bridge parameters
    print("\n📝 Step 1: Defining bridge parameters...")
    
    params = DrawingParameters(
        # Bridge geometry
        span_length=14.0,              # meters
        number_of_spans=3,             # number of spans
        carriage_width=7.5,            # meters (2 lanes)
        footpath_width=1.5,            # meters (each side)
        
        # Levels (in meters)
        rtl=100.500,                   # Road Top Level
        hfl=98.200,                    # High Flood Level
        bed_level=95.000,              # River bed level
        foundation_level=90.000,       # Foundation level
        agl=96.500,                    # Average Ground Level
        
        # Pier parameters (in meters)
        pier_width=1.2,
        pier_depth=8.0,
        pier_cap_height=0.5,
        pier_cap_width=2.0,
        
        # Abutment parameters (in meters)
        abutment_width=1.5,
        abutment_base_width=3.0,
        abutment_height=6.0,
        
        # Slab parameters (in meters)
        slab_thickness=0.45,
        wearing_coat_thickness=0.075,
        
        # Materials
        concrete_grade="M35",
        steel_grade="Fe500",
        
        # Project info
        project_name="Bridge over River Yamuna",
        drawing_no="BR-YMN-001"
    )
    
    print(f"   ✓ Project: {params.project_name}")
    print(f"   ✓ Drawing No: {params.drawing_no}")
    print(f"   ✓ Span: {params.number_of_spans} x {params.span_length}m")
    print(f"   ✓ Width: {params.carriage_width}m + 2 x {params.footpath_width}m footpath")
    print(f"   ✓ RTL: {params.rtl}m, HFL: {params.hfl}m")
    
    # Step 2: Initialize generators
    print("\n🔧 Step 2: Initializing drawing generators...")
    
    forms = CommonDrawingForms()
    generator = DXFGenerator()
    
    # Step 3: Create output directory
    print("\n📁 Step 3: Creating output directory...")
    
    output_dir = Path(__file__).parent / "output" / params.drawing_no
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"   ✓ Output directory: {output_dir}")
    
    # Step 4: Generate drawing forms
    print("\n📐 Step 4: Generating drawing forms...")
    
    drawings = {
        "01_GAD_Elevation.dxf": {
            'form': forms.create_gad_elevation(params),
            'description': 'General Arrangement Drawing - Elevation View'
        },
        "02_Pier_Details.dxf": {
            'form': forms.create_pier_details(params),
            'description': 'Pier Details - Elevation & Cross-Section'
        },
        "03_Abutment_Details.dxf": {
            'form': forms.create_abutment_details(params),
            'description': 'Abutment Details - Elevation & Plan'
        },
        "04_Deck_Slab_Reinforcement.dxf": {
            'form': forms.create_deck_slab_reinforcement(params),
            'description': 'Deck Slab Reinforcement Details'
        },
        "05_Cross_Section.dxf": {
            'form': forms.create_cross_section(params),
            'description': 'Typical Cross Section'
        }
    }
    
    print(f"   ✓ Generated {len(drawings)} drawing forms")
    
    # Step 5: Export to DXF files
    print("\n💾 Step 5: Exporting to DXF files...")
    
    for filename, drawing_info in drawings.items():
        output_path = output_dir / filename
        generator.save_dxf(drawing_info['form'], str(output_path))
        print(f"   ✓ {filename} - {drawing_info['description']}")
    
    # Step 6: Summary
    print("\n" + "=" * 80)
    print("GENERATION COMPLETE!")
    print("=" * 80)
    print(f"\n📊 Summary:")
    print(f"   • Project: {params.project_name}")
    print(f"   • Drawing Set: {params.drawing_no}")
    print(f"   • Files Generated: {len(drawings)}")
    print(f"   • Output Location: {output_dir}")
    print(f"\n📁 Generated Files:")
    
    for file in sorted(output_dir.glob("*.dxf")):
        size_kb = file.stat().st_size / 1024
        print(f"   • {file.name} ({size_kb:.1f} KB)")
    
    print(f"\n✅ Next Steps:")
    print(f"   1. Open DXF files in AutoCAD, DraftSight, or LibreCAD")
    print(f"   2. Review and adjust as needed")
    print(f"   3. Add annotations, title blocks, and project details")
    print(f"   4. Print or export to PDF for submission")
    
    print("\n" + "=" * 80)
    
    return output_dir


def generate_custom_bridge():
    """Example: Generate a custom bridge with different parameters."""
    
    print("\n" + "=" * 80)
    print("CUSTOM BRIDGE EXAMPLE")
    print("=" * 80)
    
    # Different bridge configuration
    params = DrawingParameters(
        span_length=16.0,              # Longer spans
        number_of_spans=4,             # More spans
        carriage_width=10.5,           # Wider (3 lanes)
        footpath_width=2.0,            # Wider footpaths
        
        rtl=150.750,
        hfl=148.500,
        bed_level=145.000,
        foundation_level=138.000,
        agl=149.000,
        
        pier_width=1.5,
        pier_depth=10.0,
        pier_cap_height=0.6,
        pier_cap_width=2.5,
        
        abutment_width=2.0,
        abutment_base_width=4.0,
        abutment_height=8.0,
        
        slab_thickness=0.50,
        wearing_coat_thickness=0.080,
        
        concrete_grade="M40",
        steel_grade="Fe500D",
        project_name="Major Bridge on NH-44",
        drawing_no="BR-NH44-002"
    )
    
    forms = CommonDrawingForms()
    generator = DXFGenerator()
    
    output_dir = Path(__file__).parent / "output" / params.drawing_no
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate just GAD for this example
    gad = forms.create_gad_elevation(params)
    output_path = output_dir / "GAD_Elevation.dxf"
    generator.save_dxf(gad, str(output_path))
    
    print(f"\n✅ Custom bridge GAD generated: {output_path}")
    print(f"   • {params.number_of_spans} spans x {params.span_length}m = {params.span_length * params.number_of_spans}m total")
    print(f"   • Carriageway: {params.carriage_width}m (3 lanes)")
    
    return output_dir


if __name__ == "__main__":
    # Run the complete demo
    output1 = generate_complete_bridge_set()
    
    # Run custom example
    output2 = generate_custom_bridge()
    
    print("\n" + "=" * 80)
    print("ALL DEMOS COMPLETE!")
    print("=" * 80)
    print(f"\nOutput directories:")
    print(f"   1. {output1}")
    print(f"   2. {output2}")
    print("\nOpen these DXF files in your CAD software to view the drawings!")
    print("=" * 80 + "\n")
