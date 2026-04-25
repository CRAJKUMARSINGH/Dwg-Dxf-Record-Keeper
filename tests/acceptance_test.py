"""
Engineering Acceptance Test
==========================
Automated verification of all bridge types, BOQ, and exports.
"""

import sys
from pathlib import Path
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.bridge_schema import BridgeProject, BridgeType
from generators.templates import SheetTemplates
from modules.boq_engine import BOQEngine
from modules.design_checks import DesignChecker
from modules.export_service import ExportService
from modules.pdf_service import PDFService

def test_bridge_type(b_type: BridgeType, name: str):
    print(f"--- Testing {b_type.value} ---")
    project = BridgeProject(bridge_type=b_type)
    project.metadata.project_name = f"Test {name}"
    
    # 1. Test Drawing Generation
    try:
        drawings = SheetTemplates.generate_from_project(project)
        print(f"[OK] Generated {len(drawings)} drawing sheets.")
    except Exception as e:
        print(f"[FAIL] Drawing Generation Failed: {e}")
        return False

    # 2. Test BOQ
    engine = BOQEngine(project)
    results = engine.calculate_all()
    if results['Concrete_Deck_m3'] > 0:
        print(f"[OK] BOQ Calculated: {results['Concrete_Deck_m3']} m3 Deck Concrete.")
    else:
        print(f"[FAIL] BOQ Calculation Failed or Zero.")
        return False

    # 3. Test Design Checks
    checker = DesignChecker(project)
    warnings = checker.run_all_checks()
    print(f"[INFO] Design Warnings: {len(warnings)}")

    # 4. Test Exports
    test_out = Path("tests/output")
    test_out.mkdir(parents=True, exist_ok=True)
    
    xl_path = test_out / f"{name}_BOQ.xlsx"
    ExportService.export_boq_to_excel(project.to_dict(), results, str(xl_path))
    if xl_path.exists():
        print(f"[OK] Excel Exported: {xl_path}")
    
    pdf_path = test_out / f"{name}_Report.pdf"
    PDFService.generate_design_report(project.to_dict(), results, warnings, str(pdf_path))
    if pdf_path.exists():
        print(f"[OK] PDF Exported: {pdf_path}")
        
    return True

if __name__ == "__main__":
    success = True
    success &= test_bridge_type(BridgeType.RCC_SLAB, "RCC_Slab")
    success &= test_bridge_type(BridgeType.T_BEAM, "T_Beam")
    success &= test_bridge_type(BridgeType.BOX_CULVERT, "Box_Culvert")
    
    if success:
        print("\n[SUCCESS] ALL ENGINEERING ACCEPTANCE TESTS PASSED!")
    else:
        print("\n[ERROR] SOME TESTS FAILED.")
        sys.exit(1)

