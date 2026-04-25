"""
Validation Suite
=================
Generates test drawings at multiple scales and produces a validation report.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from models.components import BridgeParameters
from generators.templates import SheetTemplates


def validate_components():
    base_dir = Path(__file__).resolve().parent.parent
    output_dir = base_dir / "output" / "validation"
    output_dir.mkdir(parents=True, exist_ok=True)

    test_cases = [
        {"name": "Standard_14m", "span": 14.0, "width": 7.5, "pier_width": 1.2,
         "nsl_l": 100.0, "nsl_c": 99.5, "nsl_r": 99.8},
        {"name": "Long_Span_24m", "span": 24.0, "width": 8.5, "pier_width": 1.5,
         "nsl_l": 102.0, "nsl_c": 100.5, "nsl_r": 101.0},
        {"name": "Short_Span_8m", "span": 8.0, "width": 5.5, "pier_width": 1.0,
         "nsl_l": 98.0, "nsl_c": 97.5, "nsl_r": 97.8},
        {"name": "Steep_Slope", "span": 12.0, "width": 7.5, "pier_width": 1.2,
         "nsl_l": 105.0, "nsl_c": 100.0, "nsl_r": 103.0},
        {"name": "Gravity_Abutment", "span": 10.0, "width": 7.5, "pier_width": 1.0,
         "nsl_l": 99.0, "nsl_c": 98.5, "nsl_r": 99.0,
         "abut_type": "Gravity"},
        {"name": "Counterfort_Abutment", "span": 16.0, "width": 8.5, "pier_width": 1.5,
         "nsl_l": 101.0, "nsl_c": 99.0, "nsl_r": 100.5,
         "abut_type": "Counterfort"},
    ]

    results = []
    report_lines = ["# Validation Report\n"]

    for case in test_cases:
        params = BridgeParameters(
            project_name=f"Validation - {case['name']}",
            span_length=case["span"],
            carriage_width=case["width"],
            pier_width=case["pier_width"],
            nsl_left=case["nsl_l"],
            nsl_center=case["nsl_c"],
            nsl_right=case["nsl_r"],
            abutment_type=case.get("abut_type", "Cantilever"),
        )

        report_lines.append(f"\n## {case['name']}\n")
        report_lines.append(f"- Span: {case['span']}m, Width: {case['width']}m")
        report_lines.append(f"- NSL: L={case['nsl_l']}, C={case['nsl_c']}, R={case['nsl_r']}")
        report_lines.append(f"- Abutment: {case.get('abut_type', 'Cantilever')}")

        errors = []

        # Generate all drawings for this test case
        try:
            builders = SheetTemplates.generate_all(params)
            for drg_name, builder in builders.items():
                path = output_dir / f"{drg_name}_{case['name']}.dxf"
                builder.save(path)
            report_lines.append(f"- ✅ Generated {len(builders)} drawings successfully")
            results.append(f"✅ {case['name']}: {len(builders)} drawings OK")
        except Exception as e:
            errors.append(str(e))
            report_lines.append(f"- ❌ Generation FAILED: {e}")
            results.append(f"❌ {case['name']}: FAILED - {e}")

        # Dimensional checks
        total_length = params.total_length
        expected_total = case["span"] * params.number_of_spans
        if abs(total_length - expected_total) > 0.001:
            errors.append(f"Total length mismatch: {total_length} vs {expected_total}")
            report_lines.append(f"- ⚠️ Length mismatch: {total_length:.3f} vs {expected_total:.3f}")
        else:
            report_lines.append(f"- ✅ Total length: {total_length:.1f}m (correct)")

        # NSL interpolation check
        nsl_mid = params.nsl_at_x(total_length / 2)
        report_lines.append(f"- NSL at midpoint: {nsl_mid:.3f}m")

        # Slope check
        if params.number_of_spans > 1:
            slope_lc = params.slope_left_to_center
            slope_cr = params.slope_center_to_right
            report_lines.append(f"- Slope L→C: {slope_lc:.4f}, C→R: {slope_cr:.4f}")

        if errors:
            report_lines.append(f"- **Issues found:** {len(errors)}")
        else:
            report_lines.append("- **No issues found**")

    # Write validation report
    report_path = output_dir / "validation_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))

    print(f"\nValidation report saved to: {report_path}")
    return results


if __name__ == "__main__":
    print("Running validation suite...")
    print("=" * 60)
    res = validate_components()
    print("=" * 60)
    for r in res:
        print(r)
    print("Validation complete.")
