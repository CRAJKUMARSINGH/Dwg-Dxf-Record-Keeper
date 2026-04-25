import sys
import yaml
import logging
import argparse
from pathlib import Path

# Add current dir to sys.path so analyzer and reporting modules can be found
sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyzer.dwg_converter import DWGConverter
from analyzer.pattern_matcher import PatternMatcher
from analyzer.top20_identifier import identify_top20
from reporting.reporter import Reporter
from models.components import BridgeParameters
from generators.templates import SheetTemplates

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main")

def load_config(config_path: str) -> dict:
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error("Failed to load config %s: %s", config_path, e)
        return {}

def run_analysis(app_config, config_dir, base_dir):
    logger.info("Starting CAD Standardization Analysis (Phase 1)...")

    input_dir = base_dir / app_config.get("input_dir", "COMPONENT_DRAWINGS_SORTED").replace("../", "")
    output_dir = base_dir / app_config.get("output_dir", "output").replace("../", "")
    oda_path = app_config.get("oda_file_converter_path", "")

    # Convert any DWG files first
    converter = DWGConverter(oda_path)
    if converter.available:
        dwg_output = output_dir / "converted_dxf"
        converter.convert_directory(input_dir, dwg_output)

    # Run pattern matching analysis
    matcher = PatternMatcher(str(config_dir / "component_rules.yaml"))
    intermediate_dir = output_dir / "intermediate"

    logger.info("Scanning for DXF files in %s", input_dir)
    analysis_results = matcher.match_patterns(input_dir, intermediate_save_dir=intermediate_dir)

    # Identify top 20 reusable details
    top20 = identify_top20(analysis_results)
    analysis_results["top20_reusable_details"] = top20

    # Generate reports
    reporter = Reporter(str(output_dir))
    json_path = reporter.generate_json_report(analysis_results)
    md_path = reporter.generate_markdown_report(analysis_results, top20=top20)

    logger.info("Analysis Complete.")
    if json_path:
        logger.info("JSON Report: %s", json_path)
    if md_path:
        logger.info("Markdown Report: %s", md_path)

def run_generation(app_config, base_dir):
    logger.info("Starting CAD Generation (Phase 2)...")
    output_dir = base_dir / app_config.get("output_dir", "output").replace("../", "")

    params = BridgeParameters()
    logger.info("Loaded Bridge Parameters for: %s", params.project_name)

    # Generate all drawings
    builders = SheetTemplates.generate_all(params)
    for name, builder in builders.items():
        path = output_dir / f"{name}_Generated.dxf"
        builder.save(path)
        logger.info("Generated: %s", path)

    logger.info("Generation Complete. DXF files saved to output directory.")

def main():
    parser = argparse.ArgumentParser(description="CAD Standardization Engine")
    parser.add_argument("mode", choices=["analyze", "generate"], help="Mode of operation")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent.parent
    config_dir = base_dir / "config"
    app_config = load_config(config_dir / "app_config.yaml")

    if args.mode == "analyze":
        run_analysis(app_config, config_dir, base_dir)
    elif args.mode == "generate":
        run_generation(app_config, base_dir)

if __name__ == "__main__":
    main()
