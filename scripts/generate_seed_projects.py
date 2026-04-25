# scripts/generate_seed_projects.py
import json
import os
from pathlib import Path

# Mock BridgeType for standalone use
class BridgeType:
    RCC_SLAB = "RCC Slab Bridge"
    T_BEAM = "T-Beam Bridge"
    BOX_CULVERT = "Box Culvert"

samples = {
    "01_Standard_Slab_Cantilever.brg": {
        "bridge_type": BridgeType.RCC_SLAB,
        "substructure": {"abutment_type": "Cantilever", "abutment_heel_length": 2.5, "abutment_toe_length": 1.0},
        "geometry": {"span_lengths": [12.0, 12.0], "slab_thickness": 0.85}
    },
    "02_Masonry_Style_Gravity.brg": {
        "bridge_type": BridgeType.RCC_SLAB,
        "substructure": {
            "abutment_type": "Gravity", 
            "abutment_top_width": 0.9, 
            "gravity_heel_offset": 0.6, 
            "gravity_toe_offset": 0.3
        },
        "geometry": {"span_lengths": [10.0], "slab_thickness": 0.75}
    },
    "03_High_Counterfort_Bridge.brg": {
        "bridge_type": BridgeType.T_BEAM,
        "substructure": {
            "abutment_type": "Counterfort", 
            "abutment_heel_length": 3.5, 
            "counterfort_spacing": 3.0,
            "counterfort_thickness": 0.45
        },
        "geometry": {"span_lengths": [25.0, 25.0], "slab_thickness": 1.8}
    },
    "04_Standard_Box_Culvert.brg": {
        "bridge_type": BridgeType.BOX_CULVERT,
        "geometry": {"span_lengths": [4.0, 4.0], "slab_thickness": 0.45}
    }
}

os.makedirs("sample_projects", exist_ok=True)
for filename, data in samples.items():
    with open(f"sample_projects/{filename}", "w") as f:
        json.dump(data, f, indent=4)
    print(f"Generated: {filename}")
