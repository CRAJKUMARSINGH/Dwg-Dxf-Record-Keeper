import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path("src")))

try:
    from modules.project_manager import ProjectManager
    from models.bridge_schema import BridgeType

    pm = ProjectManager()
    pm.new_project()
    project = pm.current_project

    # Populate Sample Data
    project.metadata.project_name = "Demo RCC Slab Bridge"
    project.metadata.client = "Demo Client"
    project.bridge_type = BridgeType.RCC_SLAB
    project.geometry.span_lengths = [15.0, 15.0]

    Path("samples").mkdir(exist_ok=True)
    out_path = "samples/RCC_Slab_Demo.brg"
    pm.save_project(out_path)
    print(f"Sample project created successfully at {out_path}!")
except Exception as e:
    import traceback
    traceback.print_exc()
