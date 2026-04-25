"""
Enhanced Reporter
==================
Generates JSON and Markdown reports with frequency tables, cross-component
patterns, top-20 reusable details, and standardisation recommendations.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class Reporter:
    """Generates JSON and Markdown reports from analysis data."""

    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_json_report(self, data: Dict[str, Any], filename: str = "analysis_report.json") -> Path:
        output_path = self.output_dir / filename
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info("JSON report saved to %s", output_path)
            return output_path
        except Exception as e:
            logger.error("Failed to save JSON report: %s", e)
            return None

    def generate_markdown_report(
        self,
        data: Dict[str, Any],
        top20: List[Dict[str, Any]] | None = None,
        filename: str = "analysis_summary.md",
    ) -> Path:
        output_path = self.output_dir / filename
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                self._write_header(f, data)
                self._write_category_summary(f, data)
                self._write_component_details(f, data)
                self._write_frequency_tables(f, data)
                self._write_cross_component(f, data)
                if top20:
                    self._write_top20(f, top20)
                self._write_recommendations(f, data, top20)
            logger.info("Markdown report saved to %s", output_path)
            return output_path
        except Exception as e:
            logger.error("Failed to save Markdown report: %s", e)
            return None

    # ── private writers ──────────────────────────────────────────────────

    def _write_header(self, f, data):
        summary = data.get("summary", {})
        f.write("# CAD Standardization Analysis Report\n\n")
        f.write("## Overview\n")
        f.write(f"- **Total Files Processed:** {summary.get('total_files_processed', 0)}\n")
        f.write(f"- **Total Files Failed:** {summary.get('total_files_failed', 0)}\n")
        f.write(f"- **Categories Identified:** {len(summary.get('categories', {}))}\n\n")

    def _write_category_summary(self, f, data):
        summary = data.get("summary", {})
        f.write("### Categories\n")
        f.write("| Category | File Count |\n|----------|------------|\n")
        for cat, count in sorted(summary.get("categories", {}).items(), key=lambda x: x[1], reverse=True):
            f.write(f"| {cat} | {count} |\n")
        f.write("\n")

    def _write_component_details(self, f, data):
        f.write("## Component Patterns\n\n")
        components = data.get("components", {})
        for cat, comp in sorted(components.items()):
            f.write(f"### {cat} ({comp.get('file_count', 0)} files)\n")
            # Top layers
            layers = comp.get("common_layers", {})
            top_layers = sorted(layers.items(), key=lambda x: x[1], reverse=True)[:10]
            if top_layers:
                f.write("#### Most Common Layers\n")
                for layer, count in top_layers:
                    f.write(f"- `{layer}` ({count})\n")
            # Top blocks
            blocks = comp.get("common_blocks", {})
            top_blocks = sorted(blocks.items(), key=lambda x: x[1], reverse=True)[:10]
            if top_blocks:
                f.write("\n#### Most Common Blocks\n")
                for block, count in top_blocks:
                    f.write(f"- `{block}` ({count})\n")
            # Top dimensions
            dims = comp.get("common_dimensions", {})
            top_dims = sorted(dims.items(), key=lambda x: x[1], reverse=True)[:10]
            if top_dims:
                f.write("\n#### Most Common Dimensions\n")
                for dim, count in top_dims:
                    f.write(f"- `{dim}` m ({count})\n")
            f.write("\n")

    def _write_frequency_tables(self, f, data):
        freq = data.get("frequency", {})
        f.write("## Global Frequency Tables\n\n")

        for element_type, label in [
            ("layers", "Layers"), ("blocks", "Blocks"),
            ("text_styles", "Text Styles"), ("dimension_styles", "Dimension Styles"),
            ("hatch_patterns", "Hatch Patterns"),
        ]:
            items = freq.get(element_type, {})
            if not items:
                continue
            top = sorted(items.items(), key=lambda x: x[1], reverse=True)[:15]
            f.write(f"### {label} (Top 15)\n")
            f.write("| Name | Frequency |\n|------|----------|\n")
            for name, count in top:
                f.write(f"| `{name}` | {count} |\n")
            f.write("\n")

        # Dimension values — top 20
        dim_freq = freq.get("dimension_values", {})
        if dim_freq:
            top_dims = sorted(dim_freq.items(), key=lambda x: x[1], reverse=True)[:20]
            f.write("### Recurring Dimension Values (Top 20)\n")
            f.write("| Value (m) | Frequency |\n|-----------|----------|\n")
            for val, count in top_dims:
                f.write(f"| {val} | {count} |\n")
            f.write("\n")

    def _write_cross_component(self, f, data):
        cross = data.get("cross_component_patterns", {})
        if not any(cross.values()):
            return
        f.write("## Cross-Component Patterns (≥3 categories)\n\n")
        for etype, items in cross.items():
            if not items:
                continue
            f.write(f"### {etype.title()}\n")
            f.write("| Name | Frequency | Spread | Categories |\n|------|-----------|--------|------------|\n")
            for name, info in sorted(items.items(), key=lambda x: x[1]["frequency"], reverse=True)[:15]:
                cats = ", ".join(info["categories"][:5])
                f.write(f"| `{name}` | {info['frequency']} | {info['spread']} | {cats} |\n")
            f.write("\n")

    def _write_top20(self, f, top20):
        f.write("## Top 20 Reusable Standard Details\n\n")
        f.write("| # | Name | Type | Score | Freq | Spread | Recommendation |\n")
        f.write("|---|------|------|-------|------|--------|----------------|\n")
        for i, item in enumerate(top20, 1):
            f.write(f"| {i} | `{item['name']}` | {item['element_type']} "
                    f"| {item['score']} | {item['frequency']} | {item['spread']} "
                    f"| {item['recommendation']} |\n")
        f.write("\n")
        # Parameter suggestions
        f.write("### Suggested Variable Parameters\n\n")
        for i, item in enumerate(top20, 1):
            if item["suggested_parameters"]:
                params = ", ".join(f"`{p}`" for p in item["suggested_parameters"])
                f.write(f"**{i}. {item['name']}**: {params}\n\n")

    def _write_recommendations(self, f, data, top20):
        f.write("## Recommendations for Standardization\n\n")
        f.write("1. **Layer Standardization:** Adopt the most common layers as the unified standard.\n")
        f.write("2. **Block Parameterization:** Convert frequently occurring static blocks into dynamic blocks.\n")
        f.write("3. **Template Assembly:** Use identified layer structures for strict drawing templates.\n")
        f.write("4. **Dimension Style Unification:** Standardize dimension styles across all component types.\n")
        f.write("5. **Text Style Consolidation:** Reduce to 2-3 standard text styles.\n")
        if top20:
            dyn = [t for t in top20 if t["recommendation"] == "Dynamic Block"]
            script = [t for t in top20 if t["recommendation"] == "Script Generator"]
            if dyn:
                f.write(f"\n### Recommended for Dynamic Blocks ({len(dyn)} items)\n")
                for t in dyn:
                    f.write(f"- `{t['name']}` (score: {t['score']})\n")
            if script:
                f.write(f"\n### Recommended for Script Generators ({len(script)} items)\n")
                for t in script:
                    f.write(f"- `{t['name']}` (score: {t['score']})\n")
