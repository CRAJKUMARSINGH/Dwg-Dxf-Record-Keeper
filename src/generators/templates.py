from .dxf_builder import DXFBuilder
from .blocks import DynamicBlocks
from models.components import BridgeParameters

class SheetTemplates:
    """High-level templates that assemble blocks into standard bridge drawings."""
    
    @staticmethod
    def generate_gad(params: BridgeParameters) -> DXFBuilder:
        """Generates a General Arrangement Drawing (Elevation + Plan)."""
        builder = DXFBuilder()
        total_length = params.total_length
        total_width = params.total_width
        bearing_thickness = 0.05
        as_len = params.approach_slab_length
        as_thick = params.approach_slab_thickness
        gap = 0.02 # 20mm expansion joint gap
        
        # --- VIEW 1: ELEVATION (LONGITUDINAL SECTION) ---
        deck_y_bot = params.rtl - params.slab_thickness
        deck_y_top = params.rtl
        
        for i in range(params.number_of_spans):
            span_start = i * params.span_length
            span_end = (i + 1) * params.span_length
            
            # 20mm gap centered on pier and at ends
            draw_start = span_start + gap/2
            draw_end = span_end - gap/2
            
            builder.add_polyline([
                (draw_start, deck_y_bot),
                (draw_end, deck_y_bot),
                (draw_end, deck_y_top),
                (draw_start, deck_y_top)
            ], layer="C-CONC", closed=True)
            
            if i < params.number_of_spans - 1:
                builder.add_line((span_end, deck_y_bot), (span_end, deck_y_top), layer="0_HIDDEN")
        
        # Approach Slabs in Elevation
        builder.add_polyline([
            (-as_len - gap/2, params.rtl - as_thick),
            (-gap/2, params.rtl - as_thick),
            (-gap/2, params.rtl),
            (-as_len - gap/2, params.rtl)
        ], layer="C-CONC", closed=True)
        
        builder.add_polyline([
            (total_length + gap/2, params.rtl - as_thick),
            (total_length + as_len + gap/2, params.rtl - as_thick),
            (total_length + as_len + gap/2, params.rtl),
            (total_length + gap/2, params.rtl)
        ], layer="C-CONC", closed=True)
        
        # Abutments & Piers (Elevation)
        abut_left_found = params.nsl_left - params.futd
        DynamicBlocks.draw_abutment_profile(builder, (0, deck_y_bot), params, is_left=True)
        DynamicBlocks.draw_foundation_profile(builder, (0, abut_left_found), params, is_left_abut=True)
        
        abut_right_found = params.nsl_right - params.futd
        DynamicBlocks.draw_abutment_profile(builder, (total_length, deck_y_bot), params, is_left=False)
        DynamicBlocks.draw_foundation_profile(builder, (total_length, abut_right_found), params, is_right_abut=True)
            
        pier_found = params.nsl_center - params.futd
        pier_top = deck_y_bot - bearing_thickness - params.pier_cap_height
        for i in range(1, params.number_of_spans):
            x_pos = i * params.span_length
            builder.add_polyline([(x_pos - params.pier_width/2, pier_found), (x_pos - params.pier_width/2, pier_top), (x_pos + params.pier_width/2, pier_top), (x_pos + params.pier_width/2, pier_found)], layer="C-CONC", closed=True)
            DynamicBlocks.draw_foundation_profile(builder, (x_pos, pier_found), params)
            DynamicBlocks.draw_pier_cap_elevation(builder, (x_pos, pier_top), params.pier_cap_width, params.pier_cap_height, (params.pier_cap_width - params.pier_width)/2)
            DynamicBlocks.draw_elastomeric_bearing(builder, (x_pos - params.pier_width/4, deck_y_bot - bearing_thickness), 0.4, bearing_thickness)
            DynamicBlocks.draw_elastomeric_bearing(builder, (x_pos + params.pier_width/4, deck_y_bot - bearing_thickness), 0.4, bearing_thickness)
            
        # 4. NSL Indicators (Horizontal Lines)
        # Abutment Left
        builder.add_line((-as_len - 5, params.nsl_left), (5, params.nsl_left), layer="C-TOPO-NSL")
        builder.add_text(f"NSL {params.nsl_left:.3f}", (-as_len, params.nsl_left + 0.5), height=0.5)
        
        # Central Piers
        for i in range(1, params.number_of_spans):
            x_p = i * params.span_length
            builder.add_line((x_p - 5, params.nsl_center), (x_p + 5, params.nsl_center), layer="C-TOPO-NSL")
            builder.add_text(f"NSL {params.nsl_center:.3f}", (x_p + 1, params.nsl_center + 0.5), height=0.5)
            
        # Abutment Right
        builder.add_line((total_length - 5, params.nsl_right), (total_length + as_len + 5, params.nsl_right), layer="C-TOPO-NSL")
        builder.add_text(f"NSL {params.nsl_right:.3f}", (total_length + as_len, params.nsl_right + 0.5), height=0.5)
        DynamicBlocks.draw_water_level(builder, params.hfl, -as_len - 2, total_length + as_len + 2, f"HFL {params.hfl:.3f}")
        
        # --- VIEW 2: FOUNDATION PLAN ---
        plan_y_center = params.datum - 12 # Offset below elevation reduced to minimize distance
        
        # Centerline
        builder.add_line((-as_len - 2, plan_y_center), (total_length + as_len + 2, plan_y_center), layer="0_CENTERLINE")
        
        # Deck Outlines (Hidden)
        builder.add_polyline([(-gap/2, plan_y_center - total_width/2), (total_length + gap/2, plan_y_center - total_width/2), (total_length + gap/2, plan_y_center + total_width/2), (-gap/2, plan_y_center + total_width/2)], layer="0_HIDDEN", closed=True)
        
        # Approach Slabs (Plan)
        builder.add_polyline([(-as_len - gap/2, plan_y_center - total_width/2), (-gap/2, plan_y_center - total_width/2), (-gap/2, plan_y_center + total_width/2), (-as_len - gap/2, plan_y_center + total_width/2)], layer="C-CONC", closed=True)
        builder.add_polyline([(total_length + gap/2, plan_y_center - total_width/2), (total_length + as_len + gap/2, plan_y_center - total_width/2), (total_length + as_len + gap/2, plan_y_center + total_width/2), (total_length + gap/2, plan_y_center + total_width/2)], layer="C-CONC", closed=True)
        
        # Foundations (Plan)
        fl = total_width + 1.0 # Foundation Length (transverse)
        fw = params.futw
        
        # Pier Foundations
        for i in range(1, params.number_of_spans):
            x_p = i * params.span_length
            builder.add_polyline([(x_p - fw/2, plan_y_center - fl/2), (x_p + fw/2, plan_y_center - fl/2), (x_p + fw/2, plan_y_center + fl/2), (x_p - fw/2, plan_y_center + fl/2)], layer="C-CONC", closed=True)
            # Pier Shaft Outline
            builder.add_polyline([(x_p - params.pier_width/2, plan_y_center - total_width/4), (x_p + params.pier_width/2, plan_y_center - total_width/4), (x_p + params.pier_width/2, plan_y_center + total_width/4), (x_p - params.pier_width/2, plan_y_center + total_width/4)], layer="C-CONC", closed=True)

        # Abutment Foundations (Plan)
        # Simplified: rectangles representing the base slab
        builder.add_polyline([(-fw, plan_y_center - fl/2), (0, plan_y_center - fl/2), (0, plan_y_center + fl/2), (-fw, plan_y_center + fl/2)], layer="C-CONC", closed=True)
        builder.add_polyline([(total_length, plan_y_center - fl/2), (total_length + fw, plan_y_center - fl/2), (total_length + fw, plan_y_center + fl/2), (total_length, plan_y_center + fl/2)], layer="C-CONC", closed=True)
        
        # Labels
        builder.add_text("LONGITUDINAL SECTION", (total_length/2, deck_y_top + 5), height=1.0)
        builder.add_text("FOUNDATION PLAN", (total_length/2, plan_y_center + fl/2 + 3), height=1.0)
        
        # Final Scale and Title Block
        width_ext = total_length + (as_len * 2) + 25
        height_ext = params.rtl - (plan_y_center - fl/2) + 15
        
        calculated_scale = builder.calculate_engineering_scale(width_ext, height_ext)
        title_params = params.model_dump()
        title_params["scale"] = calculated_scale
        builder.draw_title_block((-as_len - 12, plan_y_center - fl/2 - 10), width_ext, height_ext, title_params)
            
        return builder

    @staticmethod
    def generate_pier_details(params: BridgeParameters) -> DXFBuilder:
        builder = DXFBuilder()
        x_center, y_base = 0, params.nsl_center - params.futd
        y_top = params.rtl - params.slab_thickness - 0.05 - params.pier_cap_height
        builder.add_polyline([(x_center - params.pier_width/2, y_base), (x_center - params.pier_width/2, y_top), (x_center + params.pier_width/2, y_top), (x_center + params.pier_width/2, y_base)], layer="C-CONC", closed=True)
        DynamicBlocks.draw_foundation_profile(builder, (x_center, y_base), params)
        DynamicBlocks.draw_pier_cap_elevation(builder, (x_center, y_top), params.pier_cap_width, params.pier_cap_height, (params.pier_cap_width - params.pier_width)/2)
        DynamicBlocks.draw_rebar_with_hooks(builder, p1=(x_center - params.pier_width/2 + params.concrete_cover, y_base + params.concrete_cover), p2=(x_center - params.pier_width/2 + params.concrete_cover, y_top + params.pier_cap_height - params.concrete_cover), diameter=0.016)
        DynamicBlocks.draw_rebar_with_hooks(builder, p1=(x_center + params.pier_width/2 - params.concrete_cover, y_base + params.concrete_cover), p2=(x_center + params.pier_width/2 - params.concrete_cover, y_top + params.pier_cap_height - params.concrete_cover), diameter=0.016)
        builder.add_line((-params.pier_cap_width, params.nsl_center), (params.pier_cap_width, params.nsl_center), layer="C-TOPO-NSL")
        width_ext, height_ext = params.pier_cap_width + 10, (y_top - y_base) + 15
        calculated_scale = builder.calculate_engineering_scale(width_ext, height_ext)
        title_params = params.model_dump(); title_params["scale"] = calculated_scale
        builder.draw_title_block((-width_ext/2, y_base - 5), width_ext, height_ext, title_params)
        return builder

    @staticmethod
    def generate_deck_slab_details(params: BridgeParameters) -> DXFBuilder:
        builder = DXFBuilder()
        length, width, cover = params.span_length, params.carriage_width, params.concrete_cover
        builder.add_polyline([(0, 0), (length, 0), (length, width), (0, width)], layer="C-CONC", closed=True)
        hx = params.haunch_size
        builder.add_polyline([(0,0), (hx, 0), (hx, hx), (0, hx)], layer="0_HIDDEN", closed=True)
        builder.add_polyline([(length-hx,0), (length, 0), (length, hx), (length-hx, hx)], layer="0_HIDDEN", closed=True)
        wc = params.wearing_coat_thickness
        builder.add_polyline([(0, width), (length, width), (length, width + wc), (0, width + wc)], layer="0_HIDDEN", closed=True)
        pw, ph = params.parapet_width, params.parapet_height
        builder.add_polyline([(-pw, width), (0, width), (0, width + ph), (-pw, width + ph)], layer="C-CONC", closed=True)
        builder.add_polyline([(length, width), (length+pw, width), (length+pw, width + ph), (length, width + ph)], layer="C-CONC", closed=True)
        spacing = 0.15
        num_bars_width = int(width / spacing)
        for i in range(num_bars_width + 1):
            y_pos = i * spacing
            if y_pos <= width - cover: DynamicBlocks.draw_rebar_with_hooks(builder, p1=(cover, y_pos), p2=(length - cover, y_pos), diameter=0.016, layer="S-REBAR-MAIN")
        width_ext, height_ext = length + (pw * 2) + 10, width + ph + 10
        calculated_scale = builder.calculate_engineering_scale(width_ext, height_ext)
        title_params = params.model_dump(); title_params["scale"] = calculated_scale
        builder.draw_title_block((-pw - 5, -5), width_ext, height_ext, title_params)
        return builder
