"""
Sheet Templates
================
High-level templates that assemble blocks into standard bridge drawings.
Includes GAD (with terrain slope), Pier, Deck Slab, Wing Wall, Abutment Detail.
"""

from .dxf_builder import DXFBuilder
from .blocks import DynamicBlocks
from models.components import BridgeParameters
from models.bridge_schema import BridgeProject, BridgeType
from modules.bridge_mapper import BridgeMapper
from .bridge_box_culvert import BoxCulvertGenerator
from .bridge_t_beam import TBeamGenerator


class SheetTemplates:
    """High-level templates that assemble blocks into standard bridge drawings."""

    @staticmethod
    def generate_from_project(project: BridgeProject) -> dict:
        """Main entry point for generating drawings from a Phase 4 project."""
        if project.bridge_type == BridgeType.BOX_CULVERT:
            return {
                "Box_Culvert_GAD": BoxCulvertGenerator.generate_culvert_gad(project)
            }
        elif project.bridge_type == BridgeType.T_BEAM:
            # Map to legacy for common sheets, use T-Beam for specific ones
            params = BridgeMapper.project_to_params(project)
            drawings = SheetTemplates.generate_all(params)
            drawings["T_Beam_Cross_Section"] = TBeamGenerator.generate_girder_cross_section(project)
            return drawings
        else:
            # Default to RCC Slab logic
            params = BridgeMapper.project_to_params(project)
            return SheetTemplates.generate_all(params)


    @staticmethod
    def generate_gad(params: BridgeParameters) -> DXFBuilder:
        """Generates a General Arrangement Drawing (Elevation + Plan)."""
        builder = DXFBuilder()
        total_length = params.total_length
        total_width = params.total_width
        bearing_thickness = 0.05
        as_len = params.approach_slab_length
        as_thick = params.approach_slab_thickness
        gap = 0.02  # 20mm expansion joint gap

        # --- VIEW 1: ELEVATION (LONGITUDINAL SECTION) ---
        deck_y_bot = params.rtl - params.slab_thickness
        deck_y_top = params.rtl

        # Deck spans
        for i in range(params.number_of_spans):
            span_start = i * params.span_length
            span_end = (i + 1) * params.span_length
            draw_start = span_start + gap / 2
            draw_end = span_end - gap / 2
            builder.add_polyline([
                (draw_start, deck_y_bot), (draw_end, deck_y_bot),
                (draw_end, deck_y_top), (draw_start, deck_y_top)
            ], layer="C-CONC", closed=True)
            if i < params.number_of_spans - 1:
                builder.add_line(
                    (span_end, deck_y_bot), (span_end, deck_y_top),
                    layer="0_HIDDEN"
                )

        # Approach Slabs in Elevation
        builder.add_polyline([
            (-as_len - gap / 2, params.rtl - as_thick),
            (-gap / 2, params.rtl - as_thick),
            (-gap / 2, params.rtl),
            (-as_len - gap / 2, params.rtl)
        ], layer="C-APPR-SLAB", closed=True)
        builder.add_text("APPROACH SLAB", (-as_len / 2, params.rtl - as_thick / 2),
                         height=0.25, layer="C-ANNO-TEXT")

        builder.add_polyline([
            (total_length + gap / 2, params.rtl - as_thick),
            (total_length + as_len + gap / 2, params.rtl - as_thick),
            (total_length + as_len + gap / 2, params.rtl),
            (total_length + gap / 2, params.rtl)
        ], layer="C-APPR-SLAB", closed=True)
        builder.add_text("APPROACH SLAB",
                         (total_length + as_len / 2, params.rtl - as_thick / 2),
                         height=0.25, layer="C-ANNO-TEXT")

        # Approach slab dimensions
        builder.add_staggered_dimension(
            (-as_len - gap / 2, params.rtl), (-gap / 2, params.rtl),
            side="above", text=f"{as_len:.1f}m"
        )
        builder.add_staggered_dimension(
            (total_length + gap / 2, params.rtl),
            (total_length + as_len + gap / 2, params.rtl),
            side="above", text=f"{as_len:.1f}m"
        )

        # ── Substructure ──

        # Left Abutment
        abut_left_found = params.nsl_left - params.futd
        DynamicBlocks.draw_abutment_profile(builder, (0, deck_y_bot), params, is_left=True)
        DynamicBlocks.draw_foundation_profile(builder, (0, abut_left_found), params, is_left_abut=True)

        # Right Abutment
        abut_right_found = params.nsl_right - params.futd
        DynamicBlocks.draw_abutment_profile(builder, (total_length, deck_y_bot), params, is_left=False)
        DynamicBlocks.draw_foundation_profile(builder, (total_length, abut_right_found), params, is_right_abut=True)

        # Piers
        pier_top = deck_y_bot - bearing_thickness - params.pier_cap_height
        for i in range(1, params.number_of_spans):
            x_pos = i * params.span_length
            pier_found = params.nsl_at_x(x_pos) - params.futd

            # Pier shaft
            builder.add_polyline([
                (x_pos - params.pier_width / 2, pier_found),
                (x_pos - params.pier_width / 2, pier_top),
                (x_pos + params.pier_width / 2, pier_top),
                (x_pos + params.pier_width / 2, pier_found)
            ], layer="C-CONC", closed=True)

            DynamicBlocks.draw_foundation_profile(builder, (x_pos, pier_found), params)
            DynamicBlocks.draw_pier_cap_elevation(
                builder, (x_pos, pier_top), params.pier_cap_width,
                params.pier_cap_height, (params.pier_cap_width - params.pier_width) / 2
            )
            DynamicBlocks.draw_elastomeric_bearing(
                builder, (x_pos - params.pier_width / 4, deck_y_bot - bearing_thickness),
                0.4, bearing_thickness
            )
            DynamicBlocks.draw_elastomeric_bearing(
                builder, (x_pos + params.pier_width / 4, deck_y_bot - bearing_thickness),
                0.4, bearing_thickness
            )

        # ── Terrain Line (Sloping Ground) ──
        builder.draw_terrain_line(params, -as_len - 2, total_length + as_len + 2)

        # NSL Indicators at supports
        # Left Abutment
        builder.add_text(f"NSL {params.nsl_left:.3f}",
                         (-as_len, params.nsl_left + 0.5), height=0.4)
        # Vertical dimension: NSL to foundation
        builder.add_staggered_dimension(
            (0, params.nsl_left), (0, abut_left_found),
            side="below", base_offset=2.0,
            text=f"FUTD {params.futd:.2f}m"
        )

        # Central Piers
        for i in range(1, params.number_of_spans):
            x_p = i * params.span_length
            nsl_here = params.nsl_at_x(x_p)
            builder.add_text(f"NSL {nsl_here:.3f}", (x_p + 1, nsl_here + 0.5), height=0.4)
            pier_found_here = nsl_here - params.futd
            builder.add_staggered_dimension(
                (x_p, nsl_here), (x_p, pier_found_here),
                side="below", base_offset=2.0,
                text=f"FUTD {params.futd:.2f}m"
            )

        # Right Abutment
        builder.add_text(f"NSL {params.nsl_right:.3f}",
                         (total_length + as_len, params.nsl_right + 0.5), height=0.4)
        builder.add_staggered_dimension(
            (total_length, params.nsl_right), (total_length, abut_right_found),
            side="below", base_offset=2.0,
            text=f"FUTD {params.futd:.2f}m"
        )

        # HFL line
        DynamicBlocks.draw_water_level(
            builder, params.hfl, -as_len - 2, total_length + as_len + 2,
            f"HFL {params.hfl:.3f}"
        )

        # Span dimensions
        for i in range(params.number_of_spans):
            s_start = i * params.span_length
            s_end = (i + 1) * params.span_length
            builder.add_staggered_dimension(
                (s_start, deck_y_top), (s_end, deck_y_top),
                side="above", base_offset=1.2,
                text=f"SPAN {params.span_length:.1f}m"
            )

        # Total length dimension
        builder.add_staggered_dimension(
            (-as_len, deck_y_top), (total_length + as_len, deck_y_top),
            side="above", base_offset=2.2,
            text=f"TOTAL {total_length + 2 * as_len:.1f}m"
        )

        # --- VIEW 2: FOUNDATION PLAN ---
        # Rule: Plan top line sits at 1.0m below the controlling foundation level datum
        min_found_y = min(abut_left_found, abut_right_found)
        for i in range(1, params.number_of_spans):
            x_p = i * params.span_length
            pier_found_y = params.nsl_at_x(x_p) - params.futd
            min_found_y = min(min_found_y, pier_found_y)
            
        plan_top_y = min_found_y - 1.0
        # Rule: Shift the entire plan 2.0m downward for better spacing
        plan_y_center = plan_top_y - (total_width / 2) - 2.0

        # Centerline (Extended to full deck + approach slabs)
        builder.add_line(
            (-as_len, plan_y_center),
            (total_length + as_len, plan_y_center),
            layer="0_CENTERLINE"
        )

        # Deck Outline (Hidden)
        builder.add_polyline([
            (-gap / 2, plan_y_center - total_width / 2),
            (total_length + gap / 2, plan_y_center - total_width / 2),
            (total_length + gap / 2, plan_y_center + total_width / 2),
            (-gap / 2, plan_y_center + total_width / 2)
        ], layer="0_HIDDEN", closed=True)

        # Approach Slabs (Plan)
        builder.add_polyline([
            (-as_len - gap / 2, plan_y_center - total_width / 2),
            (-gap / 2, plan_y_center - total_width / 2),
            (-gap / 2, plan_y_center + total_width / 2),
            (-as_len - gap / 2, plan_y_center + total_width / 2)
        ], layer="C-APPR-SLAB", closed=True)
        builder.add_polyline([
            (total_length + gap / 2, plan_y_center - total_width / 2),
            (total_length + as_len + gap / 2, plan_y_center - total_width / 2),
            (total_length + as_len + gap / 2, plan_y_center + total_width / 2),
            (total_length + gap / 2, plan_y_center + total_width / 2)
        ], layer="C-APPR-SLAB", closed=True)

        # Foundations (Plan)
        fl = total_width + 1.0
        fw = params.futw

        # Pier Foundations
        for i in range(1, params.number_of_spans):
            x_p = i * params.span_length
            builder.add_polyline([
                (x_p - fw / 2, plan_y_center - fl / 2),
                (x_p + fw / 2, plan_y_center - fl / 2),
                (x_p + fw / 2, plan_y_center + fl / 2),
                (x_p - fw / 2, plan_y_center + fl / 2)
            ], layer="C-FOUND", closed=True)
            builder.add_polyline([
                (x_p - params.pier_width / 2, plan_y_center - total_width / 4),
                (x_p + params.pier_width / 2, plan_y_center - total_width / 4),
                (x_p + params.pier_width / 2, plan_y_center + total_width / 4),
                (x_p - params.pier_width / 2, plan_y_center + total_width / 4)
            ], layer="C-CONC", closed=True)

        # Abutment Foundations (Plan)
        builder.add_polyline([
            (-fw, plan_y_center - fl / 2), (0, plan_y_center - fl / 2),
            (0, plan_y_center + fl / 2), (-fw, plan_y_center + fl / 2)
        ], layer="C-FOUND", closed=True)
        builder.add_polyline([
            (total_length, plan_y_center - fl / 2),
            (total_length + fw, plan_y_center - fl / 2),
            (total_length + fw, plan_y_center + fl / 2),
            (total_length, plan_y_center + fl / 2)
        ], layer="C-FOUND", closed=True)

        # Labels
        builder.add_text("LONGITUDINAL SECTION",
                         (total_length / 2, deck_y_top + 5), height=1.0)
        
        # Foundation Plan Label (Bottom Centered)
        builder.add_text("FOUNDATION PLAN",
                         (total_length / 2, plan_y_center - fl / 2 - 4.0), height=1.0)

        # Title Block
        width_ext = total_length + (as_len * 2) + 25
        height_ext = params.rtl - (plan_y_center - fl / 2) + 15
        calculated_scale = builder.calculate_engineering_scale(width_ext, height_ext)
        title_params = params.model_dump()
        title_params["scale"] = calculated_scale
        builder.draw_title_block(
            (-as_len - 12, plan_y_center - fl / 2 - 12),
            width_ext, height_ext, title_params
        )


        return builder

    @staticmethod
    def generate_pier_details(params: BridgeParameters) -> DXFBuilder:
        """Generates professional Pier drawing based on Deep Dive standards."""
        builder = DXFBuilder()
        x_center = 0
        y_base = params.nsl_center - params.futd
        y_top = params.rtl - params.slab_thickness - 0.05 - params.pier_cap_height
        cover = params.concrete_cover
        
        # --- VIEW 1: ELEVATION ---
        # Concrete Outline (st-obj layer)
        builder.add_polyline([
            (x_center - params.pier_width / 2, y_base),
            (x_center - params.pier_width / 2, y_top),
            (x_center + params.pier_width / 2, y_top),
            (x_center + params.pier_width / 2, y_base)
        ], layer="st-obj", closed=True)

        DynamicBlocks.draw_foundation_profile(builder, (x_center, y_base), params)
        DynamicBlocks.draw_pier_cap_elevation(
            builder, (x_center, y_top), params.pier_cap_width,
            params.pier_cap_height, (params.pier_cap_width - params.pier_width) / 2
        )

        # Rebar (st-rf layer)
        ft_w = params.futw
        ft_t = params.foundation_thickness
        builder.add_line(
            (x_center - ft_w/2 + cover, y_base - ft_t + cover),
            (x_center + ft_w/2 - cover, y_base - ft_t + cover),
            layer="st-rf"
        )
        
        # Pier Shaft Verticals
        num_bars = 8
        spacing = (params.pier_width - 2 * cover) / (num_bars - 1)
        for i in range(num_bars):
            bx = x_center - params.pier_width/2 + cover + i * spacing
            DynamicBlocks.draw_rebar_with_hooks(
                builder, (bx, y_base + cover), (bx, y_top + params.pier_cap_height - cover),
                diameter=0.020, layer="st-rf"
            )

        # Deck Anchorage & Seismic Strainers
        cap_y_top = y_top + params.pier_cap_height
        DynamicBlocks.draw_anchor_bolt(builder, (x_center - params.pier_cap_width/4, cap_y_top))
        DynamicBlocks.draw_anchor_bolt(builder, (x_center + params.pier_cap_width/4, cap_y_top))
        
        # Professional Labels (%%U for underline)
        builder.add_text("%%UELEVATION", (x_center, cap_y_top + 2.5), height=0.8, layer="st-txt")

        # --- VIEW 2: SECTIONAL PLAN A-A (AT SHAFT) ---
        y_plan_a = y_base - ft_t - 6.0
        builder.add_polyline([
            (x_center - params.pier_width/2, y_plan_a - 0.5), (x_center + params.pier_width/2, y_plan_a - 0.5),
            (x_center + params.pier_width/2, y_plan_a + 0.5), (x_center - params.pier_width/2, y_plan_a + 0.5)
        ], layer="st-obj", closed=True)
        # Internal rebar dots for shaft
        for dx in range(num_bars):
            bx = x_center - params.pier_width/2 + cover + dx * spacing
            builder.add_circle((bx, y_plan_a), 0.015, layer="st-rf")
        
        builder.add_text("%%UPLAN SECTION A-A", (x_center, y_plan_a - 1.5), height=0.5, layer="st-txt")

        # --- VIEW 3: SECTIONAL PLAN B-B (AT FOUNDATION) ---
        y_plan_b = y_plan_a - ft_w - 5.0
        builder.add_polyline([
            (x_center - ft_w/2, y_plan_b - ft_w/2), (x_center + ft_w/2, y_plan_b - ft_w/2),
            (x_center + ft_w/2, y_plan_b + ft_w/2), (x_center - ft_w/2, y_plan_b + ft_w/2)
        ], layer="st-obj", closed=True)
        
        builder.add_text("%%UPLAN SECTION B-B (FOOTING)", (x_center, y_plan_b - ft_w/2 - 2.0), height=0.5, layer="st-txt")

        # Title Block
        width_ext = params.pier_cap_width + 15
        height_ext = 30.0
        calculated_scale = builder.calculate_engineering_scale(width_ext, height_ext)
        title_params = params.model_dump()
        title_params["scale"] = calculated_scale
        builder.draw_title_block((x_center - width_ext/2, y_plan_b - 12), width_ext, height_ext, title_params)

        return builder


    @staticmethod
    def generate_deck_slab_details(params: BridgeParameters) -> DXFBuilder:
        """Generates Deck Slab cross-section with rebar, wearing coat, and parapets."""
        builder = DXFBuilder()
        length = params.span_length
        width = params.carriage_width
        cover = params.concrete_cover

        # Slab outline
        builder.add_polyline(
            [(0, 0), (length, 0), (length, width), (0, width)],
            layer="C-CONC", closed=True
        )

        # Haunches
        hx = params.haunch_size
        builder.add_polyline(
            [(0, 0), (hx, 0), (hx, hx), (0, hx)],
            layer="0_HIDDEN", closed=True
        )
        builder.add_polyline(
            [(length - hx, 0), (length, 0), (length, hx), (length - hx, hx)],
            layer="0_HIDDEN", closed=True
        )

        # Wearing coat
        wc = params.wearing_coat_thickness
        builder.add_polyline(
            [(0, width), (length, width), (length, width + wc), (0, width + wc)],
            layer="0_HIDDEN", closed=True
        )
        builder.add_text(f"WC {wc * 1000:.0f}mm",
                         (length / 2, width + wc / 2), height=0.2)

        # Slab thickness label
        builder.add_text(f"SLAB THK {params.slab_thickness * 1000:.0f}mm",
                         (length / 2, width / 2), height=0.3)

        # Parapets
        pw, ph = params.parapet_width, params.parapet_height
        builder.add_polyline(
            [(-pw, width), (0, width), (0, width + ph), (-pw, width + ph)],
            layer="C-CONC", closed=True
        )
        builder.add_polyline(
            [(length, width), (length + pw, width), (length + pw, width + ph), (length, width + ph)],
            layer="C-CONC", closed=True
        )

        # Rebar
        spacing = 0.15
        num_bars = int(width / spacing)
        for i in range(num_bars + 1):
            y_pos = i * spacing
            if y_pos <= width - cover:
                DynamicBlocks.draw_rebar_with_hooks(
                    builder,
                    p1=(cover, y_pos), p2=(length - cover, y_pos),
                    diameter=0.016, layer="S-REBAR-MAIN"
                )

        # Title block
        width_ext = length + (pw * 2) + 10
        height_ext = width + ph + 10
        calculated_scale = builder.calculate_engineering_scale(width_ext, height_ext)
        title_params = params.model_dump()
        title_params["scale"] = calculated_scale
        builder.draw_title_block((-pw - 5, -5), width_ext, height_ext, title_params)

        return builder

    @staticmethod
    def generate_wing_wall_details(params: BridgeParameters) -> DXFBuilder:
        """Generates Wing Wall elevation for both abutments."""
        builder = DXFBuilder()

        # Left abutment wing wall
        y_top = params.rtl - params.slab_thickness
        DynamicBlocks.draw_wing_wall(builder, (0, y_top), params, is_left=True)

        # Right abutment wing wall (offset for clarity)
        offset_x = params.wing_wall_length + 5
        DynamicBlocks.draw_wing_wall(builder, (offset_x, y_top), params, is_left=False)

        builder.add_text("LEFT WING WALL", (0, y_top + 2), height=0.5)
        builder.add_text("RIGHT WING WALL", (offset_x, y_top + 2), height=0.5)

        # Title block
        width_ext = offset_x + params.wing_wall_length + 10
        height_ext = y_top - (min(params.nsl_left, params.nsl_right) - params.futd) + 10
        calculated_scale = builder.calculate_engineering_scale(width_ext, height_ext)
        title_params = params.model_dump()
        title_params["scale"] = calculated_scale
        builder.draw_title_block((-5, min(params.nsl_left, params.nsl_right) - params.futd - 5),
                                 width_ext, height_ext, title_params)

        return builder

    @staticmethod
    def generate_abutment_details(params: BridgeParameters) -> DXFBuilder:
        """Generates standalone Abutment Detail drawing."""
        builder = DXFBuilder()

        y_top = params.rtl - params.slab_thickness
        y_found_l = params.nsl_left - params.futd
        y_found_r = params.nsl_right - params.futd

        # Left abutment
        DynamicBlocks.draw_abutment_profile(builder, (0, y_top), params, is_left=True)
        DynamicBlocks.draw_foundation_profile(builder, (0, y_found_l), params, is_left_abut=True)
        builder.add_line((-5, params.nsl_left), (5, params.nsl_left), layer="C-TOPO-NSL")
        builder.add_text(f"NSL {params.nsl_left:.3f}", (-5, params.nsl_left + 0.5), height=0.3)
        builder.add_text("LEFT ABUTMENT", (0, y_top + 2), height=0.5)

        # Right abutment (offset)
        offset = 15
        DynamicBlocks.draw_abutment_profile(builder, (offset, y_top), params, is_left=False)
        DynamicBlocks.draw_foundation_profile(builder, (offset, y_found_r), params, is_right_abut=True)
        builder.add_line((offset - 5, params.nsl_right), (offset + 5, params.nsl_right), layer="C-TOPO-NSL")
        builder.add_text(f"NSL {params.nsl_right:.3f}", (offset + 5, params.nsl_right + 0.5), height=0.3)
        builder.add_text("RIGHT ABUTMENT", (offset, y_top + 2), height=0.5)

        builder.add_text(f"TYPE: {params.abutment_type.upper()}", (offset / 2, y_top + 4), height=0.5)

        # Title block
        width_ext = offset + 15
        height_ext = y_top - min(y_found_l, y_found_r) + 15
        calculated_scale = builder.calculate_engineering_scale(width_ext, height_ext)
        title_params = params.model_dump()
        title_params["scale"] = calculated_scale
        builder.draw_title_block((-5, min(y_found_l, y_found_r) - 5),
                                 width_ext, height_ext, title_params)

        return builder

    @staticmethod
    def generate_all(params: BridgeParameters) -> dict:
        """Generate all standard drawings. Returns dict of {name: DXFBuilder}."""
        return {
            "GAD": SheetTemplates.generate_gad(params),
            "Pier_Details": SheetTemplates.generate_pier_details(params),
            "Deck_Slab": SheetTemplates.generate_deck_slab_details(params),
            "Wing_Wall": SheetTemplates.generate_wing_wall_details(params),
            "Abutment_Details": SheetTemplates.generate_abutment_details(params),
        }
