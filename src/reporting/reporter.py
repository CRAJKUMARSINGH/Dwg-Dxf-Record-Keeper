import json
import yaml
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class Reporter:
    """Generates JSON and Markdown reports from analysis data."""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_json_report(self, data: Dict[str, Any], filename: str = "analysis_report.json") -> Path:
        """Saves analysis data to a JSON file."""
        output_path = self.output_dir / filename
        try:
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"JSON report saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to save JSON report: {e}")
            return None
            
    def generate_markdown_report(self, data: Dict[str, Any], filename: str = "analysis_summary.md") -> Path:
        """Generates a Markdown summary of the analysis."""
        output_path = self.output_dir / filename
        try:
            with open(output_path, 'w') as f:
                f.write("# CAD Standardization Analysis Report\n\n")
                
                # Summary Section
                summary = data.get("summary", {})
                f.write("## Overview\n")
                f.write(f"- **Total Files Processed:** {summary.get('total_files_processed', 0)}\n\n")
                
                f.write("### Categories Identified\n")
                for cat, count in summary.get("categories", {}).items():
                    f.write(f"- **{cat}:** {count} files\n")
                f.write("\n")
                
                # Component Details
                f.write("## Component Patterns\n\n")
                components = data.get("components", {})
                
                for cat, comp_data in components.items():
                    f.write(f"### {cat}\n")
                    
                    # Top Layers
                    layers = comp_data.get("common_layers", {})
                    top_layers = sorted(layers.items(), key=lambda x: x[1], reverse=True)[:10]
                    if top_layers:
                        f.write("#### Most Common Layers\n")
                        for layer, count in top_layers:
                            f.write(f"- `{layer}` ({count} occurrences)\n")
                            
                    # Top Blocks
                    blocks = comp_data.get("common_blocks", {})
                    top_blocks = sorted(blocks.items(), key=lambda x: x[1], reverse=True)[:10]
                    if top_blocks:
                        f.write("\n#### Most Common Blocks\n")
                        for block, count in top_blocks:
                            f.write(f"- `{block}` ({count} occurrences)\n")
                    f.write("\n")
                    
                # Recommendations
                f.write("## Recommendations for Standardization\n")
                f.write("1. **Layer Standardization:** Adopt the most common layers found across components as the unified standard.\n")
                f.write("2. **Block Parameterization:** Convert the frequently occurring static blocks into dynamic blocks with parametric properties.\n")
                f.write("3. **Template Assembly:** Use the identified layer structures to generate strict drawing templates for each component type.\n")
                
            logger.info(f"Markdown report saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to save Markdown report: {e}")
            return None
