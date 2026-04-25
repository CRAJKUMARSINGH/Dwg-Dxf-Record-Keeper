import sys
import yaml
import logging
import argparse
from pathlib import Path

# Add current dir to sys.path so analyzer and reporting modules can be found
sys.path.insert(0, str(Path(__file__).resolve().parent))

from analyzer.dwg_converter import DWGConverter
from analyzer.pattern_matcher import PatternMatcher
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
        logger.error(f"Failed to load config {config_path}: {e}")
        return {}

def run_analysis(app_config, config_dir, base_dir):
    logger.info("Starting CAD Standardization Analysis (Phase 1)...")
    
    input_dir = base_dir / app_config.get("input_dir", "COMPONENT_DRAWINGS_SORTED").replace("../", "")
    output_dir = base_dir / app_config.get("output_dir", "output").replace("../", "")
    oda_path = app_config.get("oda_file_converter_path", "")
    
    converter = DWGConverter(oda_path)
    matcher = PatternMatcher(str(config_dir / "component_rules.yaml"))
    
    logger.info(f"Scanning for DXF files in {input_dir}")
    analysis_results = matcher.match_patterns(input_dir)
    
    reporter = Reporter(str(output_dir))
    json_path = reporter.generate_json_report(analysis_results)
    md_path = reporter.generate_markdown_report(analysis_results)
    
    logger.info("Analysis Complete.")
    if json_path: logger.info(f"JSON Report: {json_path}")
    if md_path: logger.info(f"Markdown Report: {md_path}")

def run_generation(app_config, base_dir):
    logger.info("Starting CAD Generation (Phase 2)...")
    output_dir = base_dir / app_config.get("output_dir", "output").replace("../", "")
    
    # In a full CLI, we'd parse parameters from a file or args.
    # For now, we'll use the default test parameters.
    params = BridgeParameters()
    logger.info(f"Loaded Bridge Parameters for: {params.project_name}")
    
    # Generate GAD
    gad_builder = SheetTemplates.generate_gad(params)
    gad_path = output_dir / "GAD_Generated.dxf"
    gad_builder.save(gad_path)
    
    # Generate Pier Details
    pier_builder = SheetTemplates.generate_pier_details(params)
    pier_path = output_dir / "Pier_Details_Generated.dxf"
    pier_builder.save(pier_path)
    
    # Generate Deck Slab Details
    deck_slab_builder = SheetTemplates.generate_deck_slab_details(params)
    deck_slab_path = output_dir / "Deck_Slab_Generated.dxf"
    deck_slab_builder.save(deck_slab_path)
    
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
