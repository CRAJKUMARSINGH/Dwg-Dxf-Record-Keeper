"""
Box Culvert Generator
=====================
Parametric drawing generator for RCC Box Culverts (Minor Bridges).
"""

from .dxf_builder import DXFBuilder
from models.bridge_schema import BridgeProject

class BoxCulvertGenerator:
    @staticmethod
    def generate_culvert_gad(project: BridgeProject) -> DXFBuilder:
        builder = DXFBuilder()
        geom = project.geometry
        levels = project.levels
        
        # Box Culvert specific parameters (mapped from general schema)
        span = geom.span_lengths[0]
        height = levels.road_level - levels.bed_level
        thickness = geom.slab_thickness
        
        # --- Elevation (Section) ---
        # Bottom Slab
        builder.add_polyline([
            (-thickness, levels.bed_level - thickness),
            (span + thickness, levels.bed_level - thickness),
            (span + thickness, levels.bed_level),
            (-thickness, levels.bed_level)
        ], layer="C-CONC", closed=True)
        
        # Walls
        builder.add_polyline([
            (-thickness, levels.bed_level),
            (0, levels.bed_level),
            (0, levels.road_level - thickness),
            (-thickness, levels.road_level - thickness)
        ], layer="C-CONC", closed=True)
        
        builder.add_polyline([
            (span, levels.bed_level),
            (span + thickness, levels.bed_level),
            (span + thickness, levels.road_level - thickness),
            (span, levels.road_level - thickness)
        ], layer="C-CONC", closed=True)
        
        # Top Slab
        builder.add_polyline([
            (-thickness, levels.road_level - thickness),
            (span + thickness, levels.road_level - thickness),
            (span + thickness, levels.road_level),
            (-thickness, levels.road_level)
        ], layer="C-CONC", closed=True)
        
        # Dirt Wall / Parapet
        builder.add_polyline([
            (-thickness, levels.road_level),
            (0, levels.road_level),
            (0, levels.road_level + 0.6),
            (-thickness, levels.road_level + 0.6)
        ], layer="C-CONC", closed=True)
        
        # Labels
        builder.add_text(f"BOX CULVERT {span:.1f}m x {height:.1f}m", 
                         (span/2, levels.bed_level + height/2), height=0.5)
        
        # Dimensions
        builder.add_staggered_dimension((0, levels.bed_level), (span, levels.bed_level), 
                                         side="above", text=f"SPAN {span:.1f}m")
        
        # Title block
        title_params = project.metadata.model_dump()
        title_params["scale"] = "1:50"
        builder.draw_title_block((-thickness-5, levels.bed_level-5), span+20, height+15, title_params)
        
        return builder
