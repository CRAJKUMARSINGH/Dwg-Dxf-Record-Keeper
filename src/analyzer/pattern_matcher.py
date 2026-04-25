"""
Enhanced Pattern Matcher
=========================
Categorises DXF files by component type, tracks frequency of layers/blocks/
dimensions across components, and detects cross-component repeated patterns.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
import logging

from .ezdxf_parser import DXFParser

logger = logging.getLogger(__name__)

# Optional progress bar — graceful fallback if tqdm is missing
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable


class PatternMatcher:
    def __init__(self, rules_file: str):
        self.rules_file = Path(rules_file)
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        if not self.rules_file.exists():
            logger.warning("Rules file %s not found. Using empty rules.", self.rules_file)
            return {"components": []}
        try:
            with open(self.rules_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error("Failed to load rules from %s: %s", self.rules_file, e)
            return {"components": []}

    def categorize(self, analysis_data: Dict[str, Any]) -> str:
        filename = analysis_data.get("filename", "").lower()
        texts = [t.lower() for t in analysis_data.get("texts", [])]
        layers = [l.lower() for l in analysis_data.get("layers", [])]

        combined_text = " ".join(texts)

        for component in self.rules.get("components", []):
            name = component["name"]
            keywords = [k.lower() for k in component.get("keywords", [])]

            if any(k in filename for k in keywords) or any(k in combined_text for k in keywords):
                for sub in component.get("subcategories", []):
                    sub_keywords = [k.lower() for k in sub.get("keywords", [])]
                    if any(k in filename for k in sub_keywords) or any(k in combined_text for k in sub_keywords):
                        return f"{name}_{sub['name']}"
                return name

        return "Unknown"

    def match_patterns(self, input_dir: Path, intermediate_save_dir: Path | None = None) -> Dict[str, Any]:
        """
        Analyse all DXF files in input_dir.  Returns a rich results dict with:
          - summary (file counts, categories)
          - components (per-category aggregated data)
          - frequency (cross-component layer/block/dim frequencies)
          - cross_component_patterns (elements in 3+ categories)
          - raw_data (per-file analysis)
        """
        results: Dict[str, Any] = {
            "summary": {
                "total_files_processed": 0,
                "total_files_failed": 0,
                "categories": {},
            },
            "components": {},
            "frequency": {
                "layers": defaultdict(int),
                "blocks": defaultdict(int),
                "dimension_values": defaultdict(int),
                "text_styles": defaultdict(int),
                "dimension_styles": defaultdict(int),
                "hatch_patterns": defaultdict(int),
            },
            "cross_component_patterns": {},
            "raw_data": [],
        }

        # Track which categories each element appears in (for cross-component detection)
        element_categories: Dict[str, Dict[str, set]] = {
            "layers": defaultdict(set),
            "blocks": defaultdict(set),
        }

        dxf_files = sorted(input_dir.rglob("*.dxf"))
        if not dxf_files:
            logger.warning("No .dxf files found in %s", input_dir)
            return results

        logger.info("Scanning %d DXF files in %s ...", len(dxf_files), input_dir)

        for idx, dxf_file in enumerate(tqdm(dxf_files, desc="Analyzing DXF files", unit="file")):
            parser = DXFParser(str(dxf_file))
            analysis = parser.analyze()

            if "error" in analysis:
                results["summary"]["total_files_failed"] += 1
                continue

            category = self.categorize(analysis)
            analysis["category"] = category

            # Also tag with parent folder name for component grouping
            try:
                rel = dxf_file.relative_to(input_dir)
                analysis["component_folder"] = rel.parts[0] if len(rel.parts) > 1 else "root"
            except ValueError:
                analysis["component_folder"] = "root"

            results["summary"]["total_files_processed"] += 1
            results["summary"]["categories"][category] = \
                results["summary"]["categories"].get(category, 0) + 1

            # Per-category aggregation
            if category not in results["components"]:
                results["components"][category] = {
                    "file_count": 0,
                    "common_layers": {},
                    "common_blocks": {},
                    "entity_types": {},
                    "common_dimensions": {},
                    "common_text_styles": {},
                    "common_dim_styles": {},
                    "common_hatch_patterns": {},
                }

            comp = results["components"][category]
            comp["file_count"] += 1

            # Layers
            for layer in analysis.get("layers", []):
                comp["common_layers"][layer] = comp["common_layers"].get(layer, 0) + 1
                results["frequency"]["layers"][layer] += 1
                element_categories["layers"][layer].add(category)

            # Blocks
            for block in analysis.get("blocks", []):
                comp["common_blocks"][block] = comp["common_blocks"].get(block, 0) + 1
                results["frequency"]["blocks"][block] += 1
                element_categories["blocks"][block].add(category)

            # Entity types
            for etype, count in analysis.get("entity_counts", {}).items():
                comp["entity_types"][etype] = comp["entity_types"].get(etype, 0) + count

            # Dimension values (rounded to 1mm for grouping)
            for dim in analysis.get("dimension_values", []):
                if dim.get("measurement") is not None:
                    rounded = round(dim["measurement"], 3)
                    key = str(rounded)
                    comp["common_dimensions"][key] = comp["common_dimensions"].get(key, 0) + 1
                    results["frequency"]["dimension_values"][key] += 1

            # Text styles
            for ts in analysis.get("text_styles", []):
                name = ts.get("name", "")
                if name:
                    comp["common_text_styles"][name] = comp["common_text_styles"].get(name, 0) + 1
                    results["frequency"]["text_styles"][name] += 1

            # Dimension styles
            for ds in analysis.get("dimension_styles", []):
                name = ds.get("name", "")
                if name:
                    comp["common_dim_styles"][name] = comp["common_dim_styles"].get(name, 0) + 1
                    results["frequency"]["dimension_styles"][name] += 1

            # Hatch patterns
            for hp in analysis.get("hatch_patterns", []):
                pname = hp.get("pattern_name", "")
                if pname:
                    comp["common_hatch_patterns"][pname] = comp["common_hatch_patterns"].get(pname, 0) + 1
                    results["frequency"]["hatch_patterns"][pname] += 1

            results["raw_data"].append(analysis)

            # Intermediate save every 20 files
            if intermediate_save_dir and (idx + 1) % 20 == 0:
                self._save_intermediate(results, intermediate_save_dir, idx + 1)

        # Build cross-component patterns (elements in 3+ categories)
        cross = {}
        for element_type, mapping in element_categories.items():
            cross[element_type] = {}
            for name, cats in mapping.items():
                if len(cats) >= 3:
                    cross[element_type][name] = {
                        "frequency": results["frequency"][element_type][name],
                        "categories": sorted(cats),
                        "spread": len(cats),
                    }
        results["cross_component_patterns"] = cross

        # Convert defaultdicts to regular dicts for JSON serialisation
        for key in results["frequency"]:
            results["frequency"][key] = dict(results["frequency"][key])

        logger.info(
            "Analysis complete: %d files processed, %d failed, %d categories",
            results["summary"]["total_files_processed"],
            results["summary"]["total_files_failed"],
            len(results["summary"]["categories"]),
        )

        return results

    @staticmethod
    def _save_intermediate(results: Dict, save_dir: Path, file_count: int) -> None:
        """Save intermediate results to disk."""
        try:
            save_dir.mkdir(parents=True, exist_ok=True)
            # Make a serialisable copy
            safe = json.loads(json.dumps(results, default=str))
            path = save_dir / f"intermediate_{file_count}.json"
            with open(path, 'w') as f:
                json.dump(safe, f, indent=2)
            logger.debug("Intermediate save: %s", path)
        except Exception as e:
            logger.debug("Intermediate save failed: %s", e)
