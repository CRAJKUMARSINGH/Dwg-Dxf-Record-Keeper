import yaml
from pathlib import Path
from typing import Dict, List, Any
import logging
from .ezdxf_parser import DXFParser

logger = logging.getLogger(__name__)

class PatternMatcher:
    def __init__(self, rules_file: str):
        self.rules_file = Path(rules_file)
        self.rules = self._load_rules()
        
    def _load_rules(self) -> Dict[str, Any]:
        if not self.rules_file.exists():
            logger.warning(f"Rules file {self.rules_file} not found. Using empty rules.")
            return {"components": []}
        try:
            with open(self.rules_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load rules from {self.rules_file}: {e}")
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

    def match_patterns(self, input_dir: Path) -> Dict[str, Any]:
        results = {
            "summary": {
                "total_files_processed": 0,
                "categories": {}
            },
            "components": {},
            "raw_data": []
        }
        
        for dxf_file in input_dir.rglob("*.dxf"):
            logger.info(f"Analyzing {dxf_file.name}...")
            parser = DXFParser(str(dxf_file))
            analysis = parser.analyze()
            
            if "error" in analysis:
                continue
                
            category = self.categorize(analysis)
            analysis["category"] = category
            
            results["summary"]["total_files_processed"] += 1
            results["summary"]["categories"][category] = results["summary"]["categories"].get(category, 0) + 1
            
            if category not in results["components"]:
                results["components"][category] = {
                    "common_layers": {},
                    "common_blocks": {},
                    "entity_types": {}
                }
                
            comp_data = results["components"][category]
            
            for layer in analysis.get("layers", []):
                comp_data["common_layers"][layer] = comp_data["common_layers"].get(layer, 0) + 1
                
            for block in analysis.get("blocks", []):
                comp_data["common_blocks"][block] = comp_data["common_blocks"].get(block, 0) + 1
                
            for etype, count in analysis.get("entity_counts", {}).items():
                comp_data["entity_types"][etype] = comp_data["entity_types"].get(etype, 0) + count
                
            results["raw_data"].append(analysis)
            
        return results
