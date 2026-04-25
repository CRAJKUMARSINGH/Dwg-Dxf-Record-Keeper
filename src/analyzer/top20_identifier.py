"""
Top-20 Reusable Detail Identifier
===================================
Ranks drawing elements by reusability score and recommends Dynamic Block vs Script.
"""
from __future__ import annotations
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

_PARAM_MAP = {
    "pier": ["pier_width", "pier_height", "pier_cap_width", "pier_cap_height"],
    "abutment": ["abutment_height", "stem_thickness", "toe_length", "heel_length"],
    "deck": ["span_length", "slab_thickness", "carriageway_width"],
    "slab": ["span_length", "slab_thickness", "reinforcement_spacing"],
    "wing": ["wing_wall_length", "wing_wall_angle", "wall_thickness"],
    "foundation": ["foundation_width", "foundation_depth", "foundation_thickness"],
    "bearing": ["bearing_width", "bearing_thickness", "bearing_type"],
    "rebar": ["bar_diameter", "spacing", "cover", "hook_length"],
    "girder": ["girder_depth", "flange_width", "web_thickness", "span_length"],
    "culvert": ["clear_span", "height", "wall_thickness", "slab_thickness"],
    "guard": ["height", "width", "spacing"],
    "parapet": ["parapet_height", "parapet_width"],
    "title": ["project_name", "drawing_no", "scale", "date"],
    "dim": ["text_height", "arrow_size", "dimscale"],
}


def identify_top20(analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Produce ranked list of top 20 most reusable standard details."""
    candidates: List[Dict[str, Any]] = []
    cross = analysis_results.get("cross_component_patterns", {})
    freq = analysis_results.get("frequency", {})

    # Blocks
    block_cross = cross.get("blocks", {})
    block_freq = freq.get("blocks", {})
    for name, info in block_cross.items():
        candidates.append(_make(name, "Block", info["frequency"], info["categories"], info["spread"], 1.0))
    for name, count in block_freq.items():
        if name not in block_cross and count >= 5:
            candidates.append(_make(name, "Block", count, _find_cats(name, "blocks", analysis_results), 1, 1.0))

    # Layers
    layer_cross = cross.get("layers", {})
    for name, info in layer_cross.items():
        if name in ("0", "Defpoints", "defpoints"):
            continue
        candidates.append(_make(name, "Layer Standard", info["frequency"], info["categories"], info["spread"], 0.7))

    # Dimensions
    dim_freq = freq.get("dimension_values", {})
    top_dims = sorted(dim_freq.items(), key=lambda x: x[1], reverse=True)[:30]
    for dim_val, count in top_dims:
        if count >= 3:
            candidates.append(_make(f"Dim={dim_val}m", "Recurring Dimension", count, [], 1, 0.5))

    candidates.sort(key=lambda c: c["score"], reverse=True)
    top20 = candidates[:20]
    for item in top20:
        item["suggested_parameters"] = _suggest(item)
        item["recommendation"] = _recommend(item)
    return top20


def _make(name, etype, frequency, categories, spread, factor):
    return {"name": name, "element_type": etype, "frequency": frequency,
            "categories": categories, "spread": spread,
            "score": round(frequency * max(spread, 1) * factor, 2),
            "suggested_parameters": [], "recommendation": ""}


def _find_cats(element_name, element_type, results):
    cats = set()
    key_map = {"blocks": "common_blocks", "layers": "common_layers"}
    data_key = key_map.get(element_type, "")
    for cat, comp in results.get("components", {}).items():
        if data_key and element_name in comp.get(data_key, {}):
            cats.add(cat)
    return sorted(cats)


def _suggest(item):
    name_lower = item["name"].lower()
    params = set()
    for kw, plist in _PARAM_MAP.items():
        if kw in name_lower:
            params.update(plist)
    if not params:
        if item["element_type"] == "Block":
            params = {"length", "width", "thickness", "scale_factor"}
        elif item["element_type"] == "Recurring Dimension":
            params = {"dimension_value", "tolerance"}
        else:
            params = {"name_override"}
    return sorted(params)


def _recommend(item):
    if item["element_type"] == "Block":
        return "Script Generator" if len(item["suggested_parameters"]) >= 4 else "Dynamic Block"
    elif item["element_type"] == "Layer Standard":
        return "Template Standard"
    elif item["element_type"] == "Recurring Dimension":
        return "Dimension Style Preset"
    return "Script Generator"
