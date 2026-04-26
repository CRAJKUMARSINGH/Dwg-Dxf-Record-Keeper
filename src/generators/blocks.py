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
        if width > 2.0:
            chamfer = 0.15
        else:
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

        NOTE: For Cantilever/Counterfort abutments the footing geometry is already
        drawn by draw_abutment_profile (which includes heel/toe/stem explicitly).
        This function only draws the PCC blinding layer and pile elements in that case.
        For Gravity abutments and piers it draws the full footing raft.
        """
        x, y = insert
        ft_thick = params.foundation_thickness
        futw = params.futw
        is_cantilever_abut = (
            (is_left_abut or is_right_abut) and
            params.abutment_type in ["Cantilever", "Counterfort"]
        )

        # Compute foundation bounds
        if is_left_abut:
            if params.abutment_type in ["Cantilever", "Counterfort"]:
                x_left = x - params.abutment_toe_length
                x_right = x + params.abutment_stem_thickness + params.abutment_heel_length
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

        # For Cantilever/Counterfort abutments: footing already drawn — only add PCC + piles
        if not is_cantilever_abut:
            # 1. Footing Raft (Primary structural outline)
            builder.add_polyline([
                (x_left, y), (x_right, y),
                (x_right, y - ft_thick), (x_left, y - ft_thick)
            ], layer="C-FOUND", closed=True)

            # Foundation label
            builder.add_text(
                f"FDN {ft_thick:.2f}m",
                ((x_left + x_right) / 2, y - ft_thick / 2),
                height=0.25, layer="C-ANNO-TEXT"
            )

        # 2. PCC Layer (always shown — distinct separate element below footing)
        pcc = params.pcc_offset
        if pcc > 0:
            builder.add_polyline([
                (x_left - pcc, y - ft_thick),
                (x_right + pcc, y - ft_thick),
                (x_right + pcc, y - ft_thick - 0.15),
                (x_left - pcc, y - ft_thick - 0.15)
            ], layer="C-CONC", closed=True)
            builder.add_text("PCC", (x_left - pcc - 1, y - ft_thick - 0.07), height=0.3)

        # 3. Piles (if Pile Cap)
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
        Draws the abutment stem/body + base slab (footing) with heel, toe, and shear key.
        insert is at top inner corner (bearing seat level = deck_y_bot).

        Orientation:
          - Left abutment: stem extends to the LEFT (land side), river side is RIGHT
          - Right abutment: stem extends to the RIGHT (land side), river side is LEFT

        For Cantilever/Counterfort:
          - Stem sits on the base slab
          - Heel is on the land side (behind stem)
          - Toe is on the river side (in front of stem)
          - Footing (base slab) is drawn explicitly as a separate rectangle
        """
        x, y = insert
        nsl_here = params.nsl_left if is_left else params.nsl_right
        y_found = nsl_here - params.futd

        # dir_mult: LEFT abutment body extends LEFTWARD (-1), RIGHT extends RIGHTWARD (+1)
        dir_mult = -1 if is_left else 1

        if params.abutment_type == "Gravity":
            w_top = params.abutment_top_width
            h_off = params.gravity_heel_offset
            t_off = params.gravity_toe_offset

            pts = [
                (x, y),                                       # Top inner (bearing seat)
                (x + dir_mult * w_top, y),                    # Top outer (land side)
                (x + dir_mult * (w_top + h_off), y_found),   # Bottom outer
                (x - dir_mult * t_off, y_found)               # Bottom inner (river side)
            ]
            builder.add_polyline(pts, layer="C-CONC", closed=True)
            builder.add_text("GRAVITY ABUTMENT",
                             (x + dir_mult * w_top / 2, y + 0.5), height=0.3, layer="C-ANNO-TEXT")

        elif params.abutment_type in ["Cantilever", "Counterfort"]:
            t_stem = params.abutment_stem_thickness
            toe_len = params.abutment_toe_length
            heel_len = params.abutment_heel_length
            ft_thick = params.foundation_thickness

            # ── Footing base slab (drawn explicitly) ──
            # River side (toe) is opposite to dir_mult, land side (heel) is dir_mult
            # x_toe_end: river-side edge of footing
            # x_heel_end: land-side edge of footing
            x_toe_end = x - dir_mult * toe_len          # river side
            x_heel_end = x + dir_mult * (t_stem + heel_len)  # land side

            # Footing top = y_found, footing bottom = y_found - ft_thick
            footing_top = y_found
            footing_bot = y_found - ft_thick

            builder.add_polyline([
                (x_toe_end, footing_top),
                (x_heel_end, footing_top),
                (x_heel_end, footing_bot),
                (x_toe_end, footing_bot)
            ], layer="C-FOUND", closed=True)

            # ── Stem ──
            # Stem sits on top of footing, from footing_top up to bearing seat y
            x_stem_river = x                              # river face of stem
            x_stem_land = x + dir_mult * t_stem          # land face of stem

            builder.add_polyline([
                (x_stem_river, footing_top),
                (x_stem_land, footing_top),
                (x_stem_land, y),
                (x_stem_river, y)
            ], layer="C-CONC", closed=True)

            # ── Shear key (small projection below footing center) ──
            sk_w = t_stem * 0.4
            sk_h = 0.3
            sk_cx = (x_stem_river + x_stem_land) / 2
            builder.add_polyline([
                (sk_cx - sk_w / 2, footing_bot),
                (sk_cx + sk_w / 2, footing_bot),
                (sk_cx + sk_w / 2, footing_bot - sk_h),
                (sk_cx - sk_w / 2, footing_bot - sk_h)
            ], layer="C-CONC", closed=True)

            # ── Counterfort bracing ──
            if params.abutment_type == "Counterfort":
                cf_pts = [
                    (x_stem_land, y),
                    (x_heel_end, footing_top),
                    (x_stem_land, footing_top)
                ]
                builder.add_polyline(cf_pts, layer="0_HIDDEN", closed=True)

            # ── Dimension lines ──
            dim_y_above = y + 0.5   # above bearing seat
            dim_y_below = footing_bot - 0.5  # below footing

            # Toe length
            builder.add_staggered_dimension(
                (x_toe_end, footing_top), (x_stem_river, footing_top),
                side="below", base_offset=0.6,
                text=f"TOE {toe_len:.2f}m"
            )
            # Stem thickness
            builder.add_staggered_dimension(
                (x_stem_river, footing_top), (x_stem_land, footing_top),
                side="below", base_offset=0.6,
                text=f"STEM {t_stem:.2f}m"
            )
            # Heel length
            builder.add_staggered_dimension(
                (x_stem_land, footing_top), (x_heel_end, footing_top),
                side="below", base_offset=0.6,
                text=f"HEEL {heel_len:.2f}m"
            )
            # Total footing width
            total_fw = toe_len + t_stem + heel_len
            builder.add_staggered_dimension(
                (x_toe_end, footing_top), (x_heel_end, footing_top),
                side="above", base_offset=0.5,
                text=f"TOTAL FTG {total_fw:.2f}m"
            )
            # Footing thickness
            builder.add_staggered_dimension(
                (x_heel_end, footing_top), (x_heel_end, footing_bot),
                side="below", base_offset=0.4,
                text=f"FTG THK {ft_thick:.2f}m"
            )
            # Stem height
            stem_height = y - footing_top
            builder.add_staggered_dimension(
                (x_stem_river, footing_top), (x_stem_river, y),
                side="below", base_offset=0.4,
                text=f"STEM H {stem_height:.2f}m"
            )

            # ── Labels / callouts (Increased height for readability) ──
            label_h = 0.30
            # Toe label
            builder.add_text("TOE",
                             ((x_toe_end + x_stem_river) / 2,
                              footing_top + ft_thick / 4),
                             height=label_h, layer="C-ANNO-TEXT")
            # Heel label
            builder.add_text("HEEL",
                             ((x_stem_land + x_heel_end) / 2,
                              footing_top + ft_thick / 4),
                             height=label_h, layer="C-ANNO-TEXT")
            # Footing label
            builder.add_text("FOOTING",
                             ((x_toe_end + x_heel_end) / 2,
                              footing_top - ft_thick / 2),
                             height=label_h, layer="C-ANNO-TEXT")
            # Stem label
            builder.add_text("STEM",
                             ((x_stem_river + x_stem_land) / 2,
                              (footing_top + y) / 2),
                             height=label_h, layer="C-ANNO-TEXT")
            # Shear key label
            builder.add_text("S.KEY",
                             (sk_cx + sk_w / 2 + 0.25,
                              footing_bot - sk_h / 2),
                             height=label_h * 0.8, layer="C-ANNO-TEXT")

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
