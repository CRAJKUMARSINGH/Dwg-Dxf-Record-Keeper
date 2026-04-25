"""
Enhanced DXF Parser
====================
Robust parser for DXF files using ezdxf with fallback recovery.
Extracts layers, blocks, text, dimensions, text styles, dimension styles,
hatch patterns, and entity counts.
"""

import ezdxf
from ezdxf import recover
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import math

logger = logging.getLogger(__name__)


class DXFParser:
    """Robust parser for DXF files using ezdxf with recovery fallback."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.doc = None
        self.msp = None

    def load(self) -> bool:
        """Load a DXF file with fallback to ezdxf.recover for corrupted files."""
        # Strategy 1: Normal read
        try:
            self.doc = ezdxf.readfile(str(self.file_path))
            self.msp = self.doc.modelspace()
            return True
        except Exception:
            pass

        # Strategy 2: Recover
        try:
            self.doc, auditor = recover.readfile(str(self.file_path))
            self.msp = self.doc.modelspace()
            if auditor and auditor.has_errors:
                logger.warning("DXF recovered with %d errors: %s", len(auditor.errors), self.file_path.name)
            return True
        except Exception as e:
            logger.error("Failed to load DXF %s: %s", self.file_path.name, e)
            return False

    def get_layers(self) -> List[str]:
        if not self.doc:
            return []
        return [layer.dxf.name for layer in self.doc.layers]

    def get_layer_details(self) -> List[Dict[str, Any]]:
        """Get layer details including color, linetype, lineweight."""
        if not self.doc:
            return []
        details = []
        for layer in self.doc.layers:
            dxf = layer.dxf
            details.append({
                "name": dxf.name,
                "color": dxf.color,
                "linetype": dxf.linetype if dxf.hasattr("linetype") else "Continuous",
                "lineweight": dxf.lineweight if dxf.hasattr("lineweight") else -1,
            })
        return details

    def get_blocks(self) -> List[str]:
        if not self.doc:
            return []
        return [block.name for block in self.doc.blocks if not block.name.startswith('*')]

    def get_block_details(self) -> List[Dict[str, Any]]:
        """Get block definitions with entity counts and attribute tags."""
        if not self.doc:
            return []
        details = []
        for block in self.doc.blocks:
            if block.name.startswith('*'):
                continue
            entity_count = sum(1 for _ in block)
            attribs = []
            for entity in block:
                if entity.dxftype() == 'ATTDEF':
                    attribs.append(entity.dxf.tag if entity.dxf.hasattr('tag') else '')
            details.append({
                "name": block.name,
                "entity_count": entity_count,
                "attribute_tags": attribs,
            })
        return details

    def get_text_content(self) -> List[str]:
        if not self.msp:
            return []
        texts = []
        for text in self.msp.query('TEXT MTEXT'):
            try:
                if text.dxftype() == 'TEXT':
                    texts.append(text.dxf.text)
                elif text.dxftype() == 'MTEXT':
                    texts.append(text.text)
            except Exception:
                pass
        return texts

    def get_text_styles(self) -> List[Dict[str, Any]]:
        """Extract all text style definitions from the document."""
        if not self.doc:
            return []
        styles = []
        for style in self.doc.styles:
            try:
                s = {
                    "name": style.dxf.name,
                    "font": style.dxf.font if style.dxf.hasattr("font") else "",
                    "height": style.dxf.height if style.dxf.hasattr("height") else 0.0,
                    "width_factor": style.dxf.width if style.dxf.hasattr("width") else 1.0,
                }
                styles.append(s)
            except Exception:
                pass
        return styles

    def get_dimension_styles(self) -> List[Dict[str, Any]]:
        """Extract all dimension style definitions from the document."""
        if not self.doc:
            return []
        dim_styles = []
        for ds in self.doc.dimstyles:
            try:
                d = {
                    "name": ds.dxf.name,
                    "dimscale": ds.dxf.dimscale if ds.dxf.hasattr("dimscale") else 1.0,
                    "dimtxt": ds.dxf.dimtxt if ds.dxf.hasattr("dimtxt") else 2.5,
                    "dimasz": ds.dxf.dimasz if ds.dxf.hasattr("dimasz") else 2.5,
                    "dimdec": ds.dxf.dimdec if ds.dxf.hasattr("dimdec") else 4,
                }
                dim_styles.append(d)
            except Exception:
                pass
        return dim_styles

    def get_dimension_values(self) -> List[Dict[str, Any]]:
        """Extract dimension entity measurement values from modelspace."""
        if not self.msp:
            return []
        dims = []
        for entity in self.msp:
            if entity.dxftype() in ('DIMENSION', 'LINEAR_DIMENSION', 'ALIGNED_DIMENSION'):
                try:
                    measurement = None
                    if entity.dxf.hasattr('actual_measurement'):
                        measurement = round(entity.dxf.actual_measurement, 4)
                    elif hasattr(entity, 'measurement'):
                        measurement = round(entity.measurement, 4)

                    text_override = entity.dxf.text if entity.dxf.hasattr('text') else ""
                    layer = entity.dxf.layer if entity.dxf.hasattr('layer') else "0"

                    dims.append({
                        "measurement": measurement,
                        "text_override": text_override,
                        "layer": layer,
                        "dim_type": entity.dxftype(),
                    })
                except Exception:
                    pass
        return dims

    def get_hatch_patterns(self) -> List[Dict[str, Any]]:
        """Extract hatch pattern names and properties."""
        if not self.msp:
            return []
        hatches = []
        for entity in self.msp:
            if entity.dxftype() == 'HATCH':
                try:
                    h = {
                        "pattern_name": entity.dxf.pattern_name if entity.dxf.hasattr('pattern_name') else "SOLID",
                        "layer": entity.dxf.layer if entity.dxf.hasattr('layer') else "0",
                        "pattern_scale": entity.dxf.pattern_scale if entity.dxf.hasattr('pattern_scale') else 1.0,
                    }
                    hatches.append(h)
                except Exception:
                    pass
        return hatches

    def get_entity_counts(self) -> Dict[str, int]:
        if not self.msp:
            return {}
        counts = {}
        for entity in self.msp:
            dxftype = entity.dxftype()
            counts[dxftype] = counts.get(dxftype, 0) + 1
        return counts

    def analyze(self) -> Dict[str, Any]:
        """Full analysis of a DXF file — all extractable metadata."""
        if not self.load():
            return {"error": "Failed to load", "filename": self.file_path.name}

        return {
            "filename": self.file_path.name,
            "filepath": str(self.file_path),
            "layers": self.get_layers(),
            "layer_details": self.get_layer_details(),
            "blocks": self.get_blocks(),
            "block_details": self.get_block_details(),
            "texts": self.get_text_content(),
            "text_styles": self.get_text_styles(),
            "dimension_styles": self.get_dimension_styles(),
            "dimension_values": self.get_dimension_values(),
            "hatch_patterns": self.get_hatch_patterns(),
            "entity_counts": self.get_entity_counts(),
        }
