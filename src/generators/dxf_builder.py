"""
DXF Builder
=============
Core builder for creating and saving DXF files with standard AIA/ISO layers,
terrain lines, staggered dimensions, and professional title blocks.
"""

import ezdxf
from ezdxf.document import Drawing
from pathlib import Path
import logging
import math

logger = logging.getLogger(__name__)


class DXFBuilder:
    """Core builder for creating and saving DXF files with standard settings."""

    def __init__(self, version: str = "AC1032"):  # AC1032 = AutoCAD 2018
        self.doc: Drawing = ezdxf.new(version)
        self.msp = self.doc.modelspace()
        self._dim_offset_tracker: dict = {}  # for staggered dimensions
        self._setup_standards()

    def _setup_standards(self):
        """Initializes standard AIA/ISO engineering layers and styles."""

        # Standard Linetypes
        self.doc.linetypes.add("DASHED", pattern=[0.5, 0.25, -0.25])
        self.doc.linetypes.add("CENTER", pattern=[1.25, 0.25, -0.25, 0.125, -0.25])
        self.doc.linetypes.add("HIDDEN", pattern=[0.25, 0.125, -0.125])

        # Standard Text Styles
        self.doc.styles.add("STANDARD_TEXT", font="simplex.shx")
        self.doc.styles.add("TITLE_TEXT", font="romans.shx")

        # Compact Dimension Style (2.0mm text, 1.5mm arrows)
        dimstyle = self.doc.dimstyles.new("COMPACT_ENGINEERING")
        dimstyle.dxf.dimtxt = 0.20  # Text height
        dimstyle.dxf.dimasz = 0.15  # Arrow size
        dimstyle.dxf.dimexe = 0.10  # Extension line extension
        dimstyle.dxf.dimexo = 0.10  # Extension line offset
        dimstyle.dxf.dimgap = 0.05  # Gap between text and dimension line
        dimstyle.dxf.dimtxsty = "STANDARD_TEXT"

        # AIA/ISO Standard Layers
        layers = [
            ("C-CONC", 3),             # Green - Concrete Outlines
            ("S-REBAR-MAIN", 6),       # Magenta - Main Reinforcement
            ("S-REBAR-TIES", 1),       # Red - Distribution / Ties
            ("C-TOPO-NSL", 8, "DASHED"),   # Dark Gray Dashed - NSL
            ("C-TOPO-HFL", 5, "DASHED"),   # Blue Dashed - HFL
            ("C-TOPO-BED", 8),         # Dark Gray - River Bed Level
            ("C-TOPO-TERRAIN", 52, "DASHED"),  # Brown Dashed - Terrain
            ("C-ANNO-DIMS", 2),        # Yellow - Dimensions
            ("C-ANNO-TEXT", 7),        # White/Black - Text
            ("C-ANNO-TTLB", 4),        # Cyan - Title Block
            ("C-FOUND", 30),           # Orange-Brown - Foundation
            ("C-APPR-SLAB", 140),      # Light Blue - Approach Slab
            ("0_CENTERLINE", 1, "CENTER"),
            ("0_HIDDEN", 8, "HIDDEN"),
        ]

        for layer_info in layers:
            name = layer_info[0]
            color = layer_info[1]
            linetype = layer_info[2] if len(layer_info) > 2 else "Continuous"
            self.doc.layers.add(name=name, color=color, linetype=linetype)

        logger.debug("Initialized standard layers and styles.")

    # ── Primitives ───────────────────────────────────────────────────────────

    def add_line(self, p1: tuple, p2: tuple, layer: str = "C-CONC"):
        self.msp.add_line(p1, p2, dxfattribs={"layer": layer})

    def add_polyline(self, points: list, layer: str = "C-CONC", closed: bool = False):
        pline = self.msp.add_lwpolyline(points, dxfattribs={"layer": layer})
        if closed:
            pline.close()

    def add_circle(self, center: tuple, radius: float, layer: str = "C-CONC"):
        self.msp.add_circle(center, radius, dxfattribs={"layer": layer})

    def add_text(self, text: str, insert: tuple, layer: str = "C-ANNO-TEXT",
                 height: float = 0.5, style: str = "STANDARD_TEXT",
                 align="MIDDLE_CENTER"):
        align_enum = getattr(
            ezdxf.enums.TextEntityAlignment, align,
            ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER
        )
        self.msp.add_text(
            text,
            dxfattribs={"layer": layer, "height": height, "style": style}
        ).set_placement(insert, align=align_enum)


    # ── Dimensions ───────────────────────────────────────────────────────────

    def add_dimension(self, p1: tuple, p2: tuple, loc: tuple,
                      text: str = "<>", layer: str = "C-ANNO-DIMS"):
        """Adds a linear dimension with compact style."""
        dim = self.msp.add_linear_dim(
            base=loc, p1=p1, p2=p2, text=text,
            dimstyle="COMPACT_ENGINEERING",
            dxfattribs={"layer": layer}
        )
        dim.render()

    def add_staggered_dimension(self, p1: tuple, p2: tuple, side: str = "above",
                                base_offset: float = 1.2, text: str = "<>",
                                layer: str = "C-ANNO-DIMS"):
        """
        Add a dimension with compact automatic staggering.
        side: 'above' or 'below' relative to the line p1-p2.
        """
        key = f"{side}_{round(p1[1], 1)}"
        count = self._dim_offset_tracker.get(key, 0)
        offset = base_offset + (count * 1.0) # Reduced step
        self._dim_offset_tracker[key] = count + 1

        if side == "above":
            loc_y = max(p1[1], p2[1]) + offset
        else:
            loc_y = min(p1[1], p2[1]) - offset

        loc = ((p1[0] + p2[0]) / 2, loc_y)
        self.add_dimension(p1, p2, loc, text=text, layer=layer)

    # ── Terrain & Slope ──────────────────────────────────────────────────────

    def draw_terrain_line(self, params, x_start: float, x_end: float,
                          num_points: int = 50, layer: str = "C-TOPO-TERRAIN"):
        """
        Draw sloping terrain from NSL values using piecewise interpolation.
        Shows NSL annotations and slope ratios.
        """
        # Build terrain polyline
        points = []
        step = (x_end - x_start) / max(num_points - 1, 1)
        for i in range(num_points):
            x = x_start + i * step
            y = params.nsl_at_x(max(0, min(x, params.total_length)))
            points.append((x, y))
        self.add_polyline(points, layer=layer)

        # Cross-hatch lines below terrain (ground indication)
        hatch_len = 0.4
        hatch_spacing = 2.0
        x = x_start
        while x < x_end:
            y = params.nsl_at_x(max(0, min(x, params.total_length)))
            self.add_line((x, y), (x - hatch_len, y - hatch_len), layer=layer)
            x += hatch_spacing

        # Slope annotations
        total = params.total_length
        if params.number_of_spans > 1:
            mid_x = total / 2.0
            # Left to center slope
            rise_lc = params.nsl_center - params.nsl_left
            if abs(rise_lc) > 0.001:
                pct = abs(rise_lc / mid_x) * 100
                arrow_dir = "↘" if rise_lc < 0 else "↗"
                self.add_text(
                    f"{arrow_dir} Slope {pct:.2f}% (1:{abs(mid_x/rise_lc):.0f})",
                    (mid_x / 2, (params.nsl_left + params.nsl_center) / 2 + 0.8),
                    height=0.35, layer="C-ANNO-TEXT"
                )
            # Center to right slope
            rise_cr = params.nsl_right - params.nsl_center
            run_cr = total - mid_x
            if abs(rise_cr) > 0.001:
                pct = abs(rise_cr / run_cr) * 100
                arrow_dir = "↗" if rise_cr > 0 else "↘"
                self.add_text(
                    f"{arrow_dir} Slope {pct:.2f}% (1:{abs(run_cr/rise_cr):.0f})",
                    (mid_x + run_cr / 2, (params.nsl_center + params.nsl_right) / 2 + 0.8),
                    height=0.35, layer="C-ANNO-TEXT"
                )


    # ── Title Block ──────────────────────────────────────────────────────────

    def draw_title_block(self, insert: tuple, width: float, height: float,
                         params: dict):
        """Draws a professional compact title block (0.25x width factor)."""
        x, y = insert
        layer = "C-ANNO-TTLB"

        scale_str = params.get("scale", "1:100")
        try:
            scale_val = float(scale_str.split(":")[-1])
        except Exception:
            scale_val = 100.0

        # Compacted heights for sheet (2.0mm and 3.5mm)
        h_small = (scale_val * 2.0) / 1000.0
        h_large = (scale_val * 3.5) / 1000.0

        # Main Border
        self.add_polyline(
            [(x, y), (x + width, y), (x + width, y + height), (x, y + height)],
            layer=layer, closed=True
        )

        # Compact Info Box (Bottom Right)
        # Reduced width factor: 180mm -> 45mm
        box_w = (scale_val * 45) / 1000.0
        box_h = (scale_val * 30) / 1000.0
        box_x = x + width - box_w
        box_y = y
        self.add_polyline(
            [(box_x, box_y), (box_x + box_w, box_y),
             (box_x + box_w, box_y + box_h), (box_x, box_y + box_h)],
            layer=layer, closed=True
        )

        row = box_h / 5 # 5 rows for better spacing
        self.add_line((box_x, box_y + row), (box_x + box_w, box_y + row), layer=layer)
        self.add_line((box_x, box_y + row * 2), (box_x + box_w, box_y + row * 2), layer=layer)
        self.add_line((box_x, box_y + row * 3), (box_x + box_w, box_y + row * 3), layer=layer)
        self.add_line((box_x, box_y + row * 4), (box_x + box_w, box_y + row * 4), layer=layer)
        
        pad = box_w * 0.05

        self.add_text("PROJ:", (box_x + pad, box_y + row * 4.5),
                       layer=layer, height=h_small * 0.8, align="MIDDLE_LEFT")
        self.add_text(params.get("project_name", ""),
                       (box_x + pad, box_y + row * 4.1),
                       layer="C-ANNO-TEXT", height=h_small, align="MIDDLE_LEFT")

        self.add_text("CLIENT:", (box_x + pad, box_y + row * 3.5),
                       layer=layer, height=h_small * 0.8, align="MIDDLE_LEFT")
        self.add_text(params.get("client", ""),
                       (box_x + pad, box_y + row * 3.1),
                       layer="C-ANNO-TEXT", height=h_small, align="MIDDLE_LEFT")

        self.add_text("DRG NO:", (box_x + pad, box_y + row * 2.5),
                       layer=layer, height=h_small * 0.8, align="MIDDLE_LEFT")
        self.add_text(params.get("drawing_no", ""),
                       (box_x + pad, box_y + row * 2.1),
                       layer="C-ANNO-TEXT", height=h_small, align="MIDDLE_LEFT")

        self.add_text("SCALE: " + scale_str,
                       (box_x + pad, box_y + row * 1.5),
                       layer=layer, height=h_small, align="MIDDLE_LEFT")
        
        self.add_text("DATE: " + params.get("date", ""),
                       (box_x + pad, box_y + row * 0.5),
                       layer=layer, height=h_small, align="MIDDLE_LEFT")

    def calculate_engineering_scale(self, drawing_width_m: float,
                                    drawing_height_m: float,
                                    target_sheet_width_mm: float = 400) -> str:
        """Calculates the best fit engineering scale (1:100, 1:200, etc.)."""
        drawing_width_mm = drawing_width_m * 1000
        required_scale = drawing_width_mm / target_sheet_width_mm

        standard_scales = [10, 20, 25, 50, 100, 200, 250, 400, 500, 1000, 2000, 2500, 5000]

        selected_scale = standard_scales[-1]
        for s in standard_scales:
            if s >= required_scale:
                selected_scale = s
                break

        return f"1:{selected_scale}"

    def save(self, output_path: Path):
        """Saves the DXF file to the given path."""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            self.doc.saveas(str(output_path))
            logger.info("Saved DXF to %s", output_path)
        except Exception as e:
            logger.error("Failed to save DXF to %s: %s", output_path, e)
