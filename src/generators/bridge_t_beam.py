"""
T-Beam Bridge Generator
=======================
Parametric drawing generator for RCC T-Beam and Girder Bridges.
"""

import math
from .dxf_builder import DXFBuilder
from models.bridge_schema import BridgeProject

class TBeamGenerator:
    @staticmethod
    def generate_girder_cross_section(project: BridgeProject) -> DXFBuilder:
        builder = DXFBuilder()
        geom = project.geometry
        
        # T-Beam parameters
        num_girders = 3
        girder_spacing = geom.carriageway_width / (num_girders + 1)
        girder_depth = 1.5 # Standard for 15-25m spans
        web_thickness = 0.3
        flange_thickness = geom.slab_thickness
        
        # 1. Deck Slab (Flange)
        builder.add_polyline([
            (0, 0), 
            (geom.carriageway_width, 0),
            (geom.carriageway_width, flange_thickness),
            (0, flange_thickness)
        ], layer="C-CONC", closed=True)
        
        # 2. Girders (Webs)
        for i in range(num_girders):
            x_center = girder_spacing * (i + 1)
            builder.add_polyline([
                (x_center - web_thickness/2, -girder_depth),
                (x_center + web_thickness/2, -girder_depth),
                (x_center + web_thickness/2, 0),
                (x_center - web_thickness/2, 0)
            ], layer="C-CONC", closed=True)
            
            # Bottom Bulb (Simplified)
            builder.add_polyline([
                (x_center - 0.25, -girder_depth),
                (x_center + 0.25, -girder_depth),
                (x_center + 0.25, -girder_depth + 0.3),
                (x_center - 0.25, -girder_depth + 0.3)
            ], layer="C-CONC", closed=True)

        # 3. Cross Girders (Hidden)
        builder.add_line((0, -girder_depth/2), (geom.carriageway_width, -girder_depth/2), layer="0_HIDDEN")

        builder.add_text(f"CROSS SECTION: {num_girders} GIRDERS", 
                         (geom.carriageway_width/2, flange_thickness + 0.5), height=0.5)

        # Dimensions
        builder.add_staggered_dimension((0, 0), (geom.carriageway_width, 0), 
                                         side="above", text=f"WIDTH {geom.carriageway_width:.1f}m")
        
        # Title block
        title_params = project.metadata.model_dump()
        title_params["scale"] = "1:50"
        builder.draw_title_block((-5, -girder_depth-5), geom.carriageway_width+15, girder_depth+15, title_params)
        
        return builder
