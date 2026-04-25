"""
Dynamic Blocks
================
Library of reusable parametric bridge CAD blocks.
"""

import math
from typing import Tuple
from .dxf_builder import DXFBuilder


class DynamicBlocks:
    """Library of reusable parametric bridge CAD blocks."""

    @staticmethod
    def draw_elastomeric_bearing(builder: DXFBuilder, insert: Tuple[float, float],
                                 width: float, thickness: float,
                                 layer: str = "C-CONC"):
        """Draws an elastomeric bearing pad."""
        x, y = insert
        points = [
            (x - width / 2, y), (x + width / 2, y),
            (x + width / 2, y + thickness), (x - width / 2, y + thickness)
        ]
        builder.add_polyline(points, layer=layer, closed=True)
        builder.add_line((x - width / 2, y), (x + width / 2, y + thickness), layer=layer)
        builder.add_line((x + width / 2, y), (x - width / 2, y + thickness), layer=layer)

    @staticmethod
    def draw_pier_cap_elevation(builder: DXFBuilder, insert: Tuple[float, float],
                                width: float, height: float, overhang: float,
                                layer: str = "C-CONC"):
        """Draws a proportional pier cap elevation with clamped chamfer."""
        x, y = insert
        # Clamp chamfer so it never exceeds half the height or half the overhang
        chamfer = min(height * 0.4, overhang * 0.5, height * 0.5)
        chamfer = max(chamfer, 0.05)  # minimum 50mm chamfer

        points = [
            (x - width / 2, y + chamfer),
            (x - width / 2 + chamfer, y),
            (x + width / 2 - chamfer, y),
            (x + width / 2, y + chamfer),
            (x + width / 2, y + height),
            (x - width / 2, y + height)
        ]
        builder.add_polyline(points, layer=layer, closed=True)

    @staticmethod
    def draw_rebar_with_hooks(builder: DXFBuilder, p1: Tuple[float, float],
                              p2: Tuple[float, float], diameter: float,
                              layer: str = "S-REBAR-MAIN"):
        """Draws a reinforcement bar with standard 90-degree hooks at both ends."""
        builder.add_line(p1, p2, layer=layer)
        hook_length = 12 * diameter
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.hypot(dx, dy)
        if length > 0:
            ux, uy = dx / length, dy / length
            nx, ny = -uy, ux
            builder.add_line(p1, (p1[0] + nx * hook_length, p1[1] + ny * hook_length), layer=layer)
            builder.add_line(p2, (p2[0] + nx * hook_length, p2[1] + ny * hook_length), layer=layer)

    @staticmethod
    def draw_water_level(builder: DXFBuilder, y_level: float,
                         start_x: float, end_x: float, text: str,
                         layer="C-TOPO-HFL"):
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
            builder.add_line(
                (x_tri - w / 2, y_level - i * 0.1),
                (x_tri + w / 2, y_level - i * 0.1),
                layer=layer
            )
        builder.add_text(text, (x_tri, y_level + 0.6), layer="C-ANNO-TEXT", height=0.25)

    @staticmethod
    def draw_foundation_profile(builder: DXFBuilder, insert: Tuple[float, float],
                                params, is_left_abut: bool = False,
                                is_right_abut: bool = False):
        """
        Draws the foundation footing and PCC as distinct structural elements.
        """
        x, y = insert
        ft_thick = params.foundation_thickness
        futw = params.futw

        # Compute foundation bounds
        if is_left_abut:
            if params.abutment_type in ["Cantilever", "Counterfort"]:
                x_left = x - params.abutment_heel_length - params.abutment_stem_thickness
                x_right = x + params.abutment_toe_length
            else:
                x_left = x - futw + params.abutment_top_width
                x_right = x + params.abutment_top_width
        elif is_right_abut:
            if params.abutment_type in ["Cantilever", "Counterfort"]:
                x_left = x - params.abutment_toe_length
                x_right = x + params.abutment_stem_thickness + params.abutment_heel_length
            else:
                x_left = x - params.abutment_top_width
                x_right = x + futw - params.abutment_top_width
        else:
            x_left = x - futw / 2
            x_right = x + futw / 2

        # 1. Footing Raft (Primary structural outline)
        builder.add_polyline([
            (x_left, y), (x_right, y),
            (x_right, y - ft_thick), (x_left, y - ft_thick)
        ], layer="C-FOUND", closed=True)

        # 2. PCC Layer (Distinct separate element)
        pcc = params.pcc_offset
        if pcc > 0:
            builder.add_polyline([
                (x_left - pcc, y - ft_thick),
                (x_right + pcc, y - ft_thick),
                (x_right + pcc, y - ft_thick - 0.15),
                (x_left - pcc, y - ft_thick - 0.15)
            ], layer="C-CONC", closed=True)
            builder.add_text("PCC", (x_left - pcc - 1, y - ft_thick - 0.07), height=0.3)

        # Labels
        builder.add_text(
            f"FDN {ft_thick:.2f}m",
            ((x_left + x_right) / 2, y - ft_thick / 2),
            height=0.25, layer="C-ANNO-TEXT"
        )


        # Piles
        if params.foundation_type == "Pile Cap":
            pile_d = params.pile_diameter
            pile_depth = params.pile_depth
            for px in [x_left + pile_d, x_right - pile_d]:
                builder.add_line(
                    (px - pile_d / 2, y - ft_thick),
                    (px - pile_d / 2, y - ft_thick - pile_depth),
                    layer="0_HIDDEN"
                )
                builder.add_line(
                    (px + pile_d / 2, y - ft_thick),
                    (px + pile_d / 2, y - ft_thick - pile_depth),
                    layer="0_HIDDEN"
                )
                builder.add_line(
                    (px - pile_d / 2, y - ft_thick - pile_depth),
                    (px + pile_d / 2, y - ft_thick - pile_depth),
                    layer="0_HIDDEN"
                )

    @staticmethod
    def draw_abutment_profile(builder: DXFBuilder, insert: Tuple[float, float],
                              params, is_left: bool = True):
        """
        Draws the abutment stem/body. insert is at top inner corner (bearing seat).

        Orientation:
          - Left abutment: stem extends to the LEFT (land side)
          - Right abutment: stem extends to the RIGHT (land side)
        """
        x, y = insert
        y_bottom = params.nsl_left - params.futd if is_left else params.nsl_right - params.futd

        # dir_mult: LEFT abutment body extends LEFTWARD (-1), RIGHT extends RIGHTWARD (+1)
        dir_mult = -1 if is_left else 1

        if params.abutment_type == "Gravity":
            w_top = params.abutment_top_width
            h_off = params.gravity_heel_offset
            t_off = params.gravity_toe_offset

            pts = [
                (x, y),                                    # Top inner (bearing seat)
                (x + dir_mult * w_top, y),                 # Top outer (land side)
                (x + dir_mult * (w_top + h_off), y_bottom),  # Bottom outer
                (x - dir_mult * t_off, y_bottom)           # Bottom inner (river side)
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
                cf_pts = [
                    (x + dir_mult * t_stem, y),
                    (x + dir_mult * (t_stem + params.abutment_heel_length), y_bottom),
                    (x + dir_mult * t_stem, y_bottom)
                ]
                builder.add_polyline(cf_pts, layer="0_HIDDEN", closed=True)

    @staticmethod
    def draw_anchor_bolt(builder: DXFBuilder, insert: Tuple[float, float],
                         height: float = 0.4, diameter: float = 0.032):
        """Draws a deck anchorage / anchor bolt in the pier cap."""
        x, y = insert
        # Bolt body
        builder.add_line((x, y), (x, y - height), layer="S-REBAR-MAIN")
        # Plate / Nut
        builder.add_polyline([
            (x - 0.05, y), (x + 0.05, y),
            (x + 0.05, y + 0.02), (x - 0.05, y + 0.02)
        ], layer="S-REBAR-TIES", closed=True)
        # Hook at bottom
        builder.add_line((x, y - height), (x + 0.1, y - height), layer="S-REBAR-MAIN")

    @staticmethod
    def draw_wing_wall(builder: DXFBuilder, insert: Tuple[float, float],

                       params, is_left: bool = True):
        """
        Draws a wing wall from the abutment face.
        Wing walls splay outward from the abutment at the specified angle.

        insert: top of wing wall at abutment junction
        is_left: True for left abutment, False for right
        """
        x, y = insert
        length = params.wing_wall_length
        thickness = params.wing_wall_thickness
        angle_deg = params.wing_wall_splay_angle
        angle_rad = math.radians(angle_deg)

        # Wing wall direction: away from bridge center (land side)
        dir_mult = -1 if is_left else 1

        # Wing wall extends perpendicular to bridge axis then splays
        dx = dir_mult * length * math.cos(angle_rad)
        dy = -length * math.sin(angle_rad)  # downward splay

        y_bottom = params.nsl_left - params.futd if is_left else params.nsl_right - params.futd

        # Outer face
        pts_outer = [
            (x, y),
            (x + dx, y + dy),
            (x + dx, y_bottom),
            (x, y_bottom)
        ]
        builder.add_polyline(pts_outer, layer="C-CONC", closed=True)

        # Inner face (offset by thickness)
        t_dx = dir_mult * thickness * math.cos(angle_rad)
        t_dy = -thickness * math.sin(angle_rad)
        pts_inner = [
            (x + t_dx, y),
            (x + dx + t_dx, y + dy),
        ]
        builder.add_line(pts_inner[0], pts_inner[1], layer="0_HIDDEN")

        # Label
        builder.add_text(
            f"Wing Wall L={length:.1f}m",
            ((x + x + dx) / 2, (y + y + dy) / 2 + 0.5),
            height=0.3, layer="C-ANNO-TEXT"
        )
