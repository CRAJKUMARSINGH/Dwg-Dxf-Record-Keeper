import math
from typing import Tuple
from .dxf_builder import DXFBuilder

class DynamicBlocks:
    """Library of reusable parametric bridge CAD blocks."""
    
    @staticmethod
    def draw_elastomeric_bearing(builder: DXFBuilder, insert: Tuple[float, float], width: float, thickness: float, layer: str = "C-CONC"):
        """Draws an elastomeric bearing pad."""
        x, y = insert
        points = [
            (x - width/2, y),
            (x + width/2, y),
            (x + width/2, y + thickness),
            (x - width/2, y + thickness)
        ]
        builder.add_polyline(points, layer=layer, closed=True)
        # Add diagonal cross lines for bearing indication
        builder.add_line((x - width/2, y), (x + width/2, y + thickness), layer=layer)
        builder.add_line((x + width/2, y), (x - width/2, y + thickness), layer=layer)
        
    @staticmethod
    def draw_pier_cap_elevation(builder: DXFBuilder, insert: Tuple[float, float], 
                                width: float, height: float, overhang: float, 
                                layer: str = "C-CONC"):
        """Draws a proportional pier cap elevation."""
        x, y = insert # y is the bottom center of the cap
        
        # Scaling the chamfer based on the height so it doesn't distort
        chamfer = height * 0.4
        
        points = [
            (x - width/2, y + chamfer),
            (x - width/2 + chamfer, y),
            (x + width/2 - chamfer, y),
            (x + width/2, y + chamfer),
            (x + width/2, y + height),
            (x - width/2, y + height)
        ]
        builder.add_polyline(points, layer=layer, closed=True)

    @staticmethod
    def draw_rebar_with_hooks(builder: DXFBuilder, p1: Tuple[float, float], p2: Tuple[float, float], 
                              diameter: float, layer: str = "S-REBAR-MAIN"):
        """Draws a reinforcement bar with standard 90-degree hooks at both ends."""
        builder.add_line(p1, p2, layer=layer)
        
        hook_length = 12 * diameter
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.hypot(dx, dy)
        
        if length > 0:
            ux, uy = dx/length, dy/length
            nx, ny = -uy, ux
            builder.add_line(p1, (p1[0] + nx * hook_length, p1[1] + ny * hook_length), layer=layer)
            builder.add_line(p2, (p2[0] + nx * hook_length, p2[1] + ny * hook_length), layer=layer)

    @staticmethod
    def draw_water_level(builder: DXFBuilder, y_level: float, start_x: float, end_x: float, text: str, layer="C-TOPO-HFL"):
        """Draws a water level indicator with text."""
        builder.add_line((start_x, y_level), (end_x, y_level), layer=layer)
        
        x_tri = start_x + 1
        points = [
            (x_tri, y_level),
            (x_tri - 0.2, y_level + 0.3),
            (x_tri + 0.2, y_level + 0.3)
        ]
        builder.add_polyline(points, layer=layer, closed=True)
        for i in range(1, 4):
            w = 0.4 - (i * 0.1)
            builder.add_line((x_tri - w/2, y_level - i*0.1), (x_tri + w/2, y_level - i*0.1), layer=layer)
            
        builder.add_text(text, (x_tri, y_level + 0.6), layer="C-ANNO-TEXT", height=0.25)

    @staticmethod
    def draw_foundation_profile(builder: DXFBuilder, insert: Tuple[float, float], params, is_left_abut: bool = False, is_right_abut: bool = False):
        """Draws the foundation block and optional piles below the insertion point."""
        x, y = insert # y is the top of the foundation (NSL - FUTD)
        
        ft_thick = params.foundation_thickness
        futw = params.futw
        
        # Open Foundation / Raft
        # If abutment, usually offset. Heel is land-side, Toe is river-side.
        if is_left_abut:
            # Land is to the left, River is to the right
            if params.abutment_type in ["Cantilever", "Counterfort"]:
                x_left = x - params.abutment_heel_length - params.abutment_stem_thickness
                x_right = x + params.abutment_toe_length
            else:
                x_left = x - futw + params.abutment_top_width
                x_right = x + params.abutment_top_width
        elif is_right_abut:
            # Land is to the right, River is to the left
            if params.abutment_type in ["Cantilever", "Counterfort"]:
                x_left = x - params.abutment_toe_length
                x_right = x + params.abutment_stem_thickness + params.abutment_heel_length
            else:
                x_left = x - params.abutment_top_width
                x_right = x + futw - params.abutment_top_width
        else: # Pier (Centered)
            x_left = x - futw/2
            x_right = x + futw/2
            
        builder.add_polyline([
            (x_left, y),
            (x_right, y),
            (x_right, y - ft_thick),
            (x_left, y - ft_thick)
        ], layer="C-CONC", closed=True)
        
        # PCC Layer below foundation
        pcc = params.pcc_offset
        if pcc > 0:
            builder.add_polyline([
                (x_left - pcc, y - ft_thick),
                (x_right + pcc, y - ft_thick),
                (x_right + pcc, y - ft_thick - 0.15), # 150mm thick PCC
                (x_left - pcc, y - ft_thick - 0.15)
            ], layer="C-CONC", closed=True)
            builder.add_text("PCC", (x_left - pcc - 1, y - ft_thick - 0.07), height=0.3)
        
        # Piles
        if params.foundation_type == "Pile Cap":
            pile_d = params.pile_diameter
            pile_depth = params.pile_depth
            
            # Simple 2-pile representation in elevation
            for px in [x_left + pile_d, x_right - pile_d]:
                builder.add_line((px - pile_d/2, y - ft_thick), (px - pile_d/2, y - ft_thick - pile_depth), layer="0_HIDDEN")
                builder.add_line((px + pile_d/2, y - ft_thick), (px + pile_d/2, y - ft_thick - pile_depth), layer="0_HIDDEN")
                builder.add_line((px - pile_d/2, y - ft_thick - pile_depth), (px + pile_d/2, y - ft_thick - pile_depth), layer="0_HIDDEN")
                
    @staticmethod
    def draw_abutment_profile(builder: DXFBuilder, insert: Tuple[float, float], params, is_left: bool = True):
        """Draws the abutment stem/body. insert is at top inner corner (bearing seat)."""
        x, y = insert
        y_bottom = params.nsl_left - params.futd if is_left else params.nsl_right - params.futd
        
        dir_mult = -1 if is_left else 1
        
        if params.abutment_type == "Gravity":
            w_top = params.abutment_top_width
            h_off = params.gravity_heel_offset
            t_off = params.gravity_toe_offset
            
            # x is the inner bearing seat corner
            pts = [
                (x, y), # Top Inner
                (x + dir_mult * w_top, y), # Top Outer
                (x + dir_mult * (w_top + h_off), y_bottom), # Bottom Outer
                (x - dir_mult * t_off, y_bottom) # Bottom Inner (Toe side)
            ]
            builder.add_polyline(pts, layer="C-CONC", closed=True)
            
        elif params.abutment_type in ["Cantilever", "Counterfort"]:
            t_stem = params.abutment_stem_thickness
            
            pts = [
                (x, y),
                (x + dir_mult * t_stem, y),
                (x + dir_mult * t_stem, y_bottom),
                (x, y_bottom)
            ]
            builder.add_polyline(pts, layer="C-CONC", closed=True)
            
            if params.abutment_type == "Counterfort":
                # Draw dashed counterfort triangle on heel side (land side)
                cf_pts = [
                    (x + dir_mult * t_stem, y),
                    (x + dir_mult * (t_stem + params.abutment_heel_length), y_bottom),
                    (x + dir_mult * t_stem, y_bottom)
                ]
                builder.add_polyline(cf_pts, layer="0_HIDDEN", closed=True)
