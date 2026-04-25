import ezdxf
from ezdxf.document import Drawing
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class DXFBuilder:
    """Core builder for creating and saving DXF files with standard settings."""
    
    def __init__(self, version: str = "AC1032"): # AC1032 is AutoCAD 2018
        self.doc: Drawing = ezdxf.new(version)
        self.msp = self.doc.modelspace()
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
        
        # AIA/ISO Standard Layers
        layers = [
            ("C-CONC", 3),          # Green - Concrete Outlines
            ("S-REBAR-MAIN", 6),    # Magenta - Main Reinforcement
            ("S-REBAR-TIES", 1),    # Red - Distribution / Ties
            ("C-TOPO-NSL", 8, "DASHED"), # Dark Gray Dashed - Natural Surface Level
            ("C-TOPO-HFL", 5, "DASHED"), # Blue Dashed - High Flood Level
            ("C-TOPO-BED", 8),      # Dark Gray - River Bed Level
            ("C-ANNO-DIMS", 2),     # Yellow - Dimensions
            ("C-ANNO-TEXT", 7),     # White/Black - Text
            ("C-ANNO-TTLB", 4),     # Cyan - Title Block
            ("0_CENTERLINE", 1, "CENTER"),
            ("0_HIDDEN", 8, "HIDDEN")
        ]
        
        for layer_info in layers:
            name = layer_info[0]
            color = layer_info[1]
            linetype = layer_info[2] if len(layer_info) > 2 else "Continuous"
            
            self.doc.layers.add(
                name=name,
                color=color,
                linetype=linetype
            )
            
        logger.info("Initialized standard layers and styles.")
        
    def add_line(self, p1: tuple, p2: tuple, layer: str = "C-CONC"):
        self.msp.add_line(p1, p2, dxfattribs={"layer": layer})
        
    def add_polyline(self, points: list, layer: str = "C-CONC", closed: bool = False):
        pline = self.msp.add_lwpolyline(points, dxfattribs={"layer": layer})
        if closed:
            pline.close()
            
    def add_circle(self, center: tuple, radius: float, layer: str = "C-CONC"):
        self.msp.add_circle(center, radius, dxfattribs={"layer": layer})
        
    def add_text(self, text: str, insert: tuple, layer: str = "C-ANNO-TEXT", height: float = 0.5, style: str = "STANDARD_TEXT", align="MIDDLE_CENTER"):
        align_enum = getattr(ezdxf.enums.TextEntityAlignment, align, ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
        self.msp.add_text(
            text, 
            dxfattribs={
                "layer": layer,
                "height": height,
                "style": style
            }
        ).set_placement(insert, align=align_enum)
        
    def add_dimension(self, p1: tuple, p2: tuple, loc: tuple, text: str = "<>", layer: str = "C-ANNO-DIMS"):
        """Adds a linear dimension. Automatically handles overlaps if logic is passed in caller."""
        dim = self.msp.add_linear_dim(
            base=loc,
            p1=p1,
            p2=p2,
            text=text,
            dxfattribs={"layer": layer}
        )
        dim.render()

    def draw_title_block(self, insert: tuple, width: float, height: float, params: dict):
        """Draws a professional dynamic title block with scale-aware text heights."""
        x, y = insert
        layer = "C-ANNO-TTLB"
        
        # Determine scale value for text sizing
        scale_str = params.get("scale", "1:100")
        try:
            scale_val = float(scale_str.split(":")[-1])
        except:
            scale_val = 100.0
            
        # Target 2.5mm and 5mm heights on the physical sheet
        h_small = (scale_val * 2.5) / 1000.0 
        h_large = (scale_val * 5.0) / 1000.0
        
        # Main Border
        self.add_polyline([(x, y), (x+width, y), (x+width, y+height), (x, y+height)], layer=layer, closed=True)
        
        # Info Box (Bottom Right) - Scaled proportionally
        box_w = (scale_val * 180) / 1000.0 # 180mm on sheet
        box_h = (scale_val * 60) / 1000.0 # 60mm on sheet
        box_x = x + width - box_w
        box_y = y
        self.add_polyline([(box_x, box_y), (box_x+box_w, box_y), (box_x+box_w, box_y+box_h), (box_x, box_y+box_h)], layer=layer, closed=True)
        
        # Row heights
        row = box_h / 4
        self.add_line((box_x, box_y + row*1), (box_x + box_w, box_y + row*1), layer=layer)
        self.add_line((box_x, box_y + row*2), (box_x + box_w, box_y + row*2), layer=layer)
        self.add_line((box_x, box_y + row*3), (box_x + box_w, box_y + row*3), layer=layer)
        self.add_line((box_x + box_w*0.6, box_y), (box_x + box_w*0.6, box_y + row*2), layer=layer)
        
        # Text Fields
        pad = box_w * 0.02
        self.add_text("PROJECT:", (box_x + pad, box_y + row*3.5), layer=layer, height=h_small, align="MIDDLE_LEFT")
        self.add_text(params.get("project_name", ""), (box_x + pad*5, box_y + row*3.5), layer="C-ANNO-TEXT", height=h_large, style="TITLE_TEXT", align="MIDDLE_LEFT")
        
        self.add_text("CLIENT:", (box_x + pad, box_y + row*2.5), layer=layer, height=h_small, align="MIDDLE_LEFT")
        self.add_text(params.get("client", ""), (box_x + pad*5, box_y + row*2.5), layer="C-ANNO-TEXT", height=h_small*1.2, align="MIDDLE_LEFT")
        
        self.add_text("CONSULTANT:", (box_x + pad, box_y + row*1.5), layer=layer, height=h_small, align="MIDDLE_LEFT")
        self.add_text(params.get("consultant", ""), (box_x + pad*5, box_y + row*1.5), layer="C-ANNO-TEXT", height=h_small*1.2, align="MIDDLE_LEFT")
        
        self.add_text("DRG NO:", (box_x + box_w*0.6 + pad, box_y + row*1.5), layer=layer, height=h_small, align="MIDDLE_LEFT")
        self.add_text(params.get("drawing_no", ""), (box_x + box_w*0.6 + pad*5, box_y + row*1.5), layer="C-ANNO-TEXT", height=h_small*1.2, align="MIDDLE_LEFT")
        
        self.add_text("ENGINEER:", (box_x + pad, box_y + row*0.5), layer=layer, height=h_small, align="MIDDLE_LEFT")
        self.add_text(params.get("engineer_name", ""), (box_x + pad*5, box_y + row*0.5), layer="C-ANNO-TEXT", height=h_small*1.2, align="MIDDLE_LEFT")
        
        self.add_text("DATE: " + params.get("date", ""), (box_x + box_w*0.6 + pad, box_y + row*0.7), layer=layer, height=h_small, align="MIDDLE_LEFT")
        self.add_text("SCALE: " + scale_str, (box_x + box_w*0.6 + pad, box_y + row*0.3), layer=layer, height=h_small, align="MIDDLE_LEFT")


    def calculate_engineering_scale(self, drawing_width_m: float, drawing_height_m: float, target_sheet_width_mm: float = 400) -> str:
        """Calculates the best fit engineering scale (1:100, 1:200, etc.)"""
        # Drawing is in meters, sheet is in mm.
        # Scale = (Drawing_Width_mm) / Sheet_Width_mm
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
            logger.info(f"Saved DXF to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save DXF to {output_path}: {e}")
