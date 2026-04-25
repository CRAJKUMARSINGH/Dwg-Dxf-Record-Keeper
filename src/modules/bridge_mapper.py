"""
Bridge Mapper
=============
Converts the new nested BridgeProject model to the legacy flat BridgeParameters model.
This allows reuse of existing DXF generation templates.
"""

from models.bridge_schema import BridgeProject
from models.components import BridgeParameters

class BridgeMapper:
    @staticmethod
    def project_to_params(project: BridgeProject) -> BridgeParameters:
        """Maps BridgeProject (Phase 4) to BridgeParameters (Phase 2/3)."""
        geom = project.geometry
        sub = project.substructure
        found = project.foundation
        levels = project.levels
        meta = project.metadata
        
        # Determine average span for the legacy model
        avg_span = sum(geom.span_lengths) / len(geom.span_lengths) if geom.span_lengths else 14.0
        
        return BridgeParameters(
            project_name=meta.project_name,
            drawing_no=meta.drawing_no,
            client=meta.client,
            consultant=meta.designed_by, # Mapping designed_by to consultant for now
            engineer_name=meta.designed_by,
            scale=meta.scale,
            
            number_of_spans=geom.number_of_spans,
            span_length=avg_span,
            carriage_width=geom.carriageway_width,
            slab_thickness=geom.slab_thickness,
            
            pier_width=sub.pier_width,
            pier_cap_width=sub.pier_cap_width,
            pier_cap_height=sub.pier_cap_height,
            
            abutment_type=sub.abutment_type,
            
            foundation_type=found.type.value,
            futw=found.width,
            futd=found.depth_below_nsl,
            foundation_thickness=found.thickness,
            pcc_offset=found.pcc_offset,
            
            rtl=levels.road_level,
            hfl=levels.hfl,
            datum=levels.datum,
            nsl_left=levels.nsl_left,
            nsl_center=levels.nsl_pier,
            nsl_right=levels.nsl_right,
            
            # Use defaults for missing fields in the new schema
            skew_angle=0.0,
            haunch_size=0.3,
            parapet_width=0.45,
            parapet_height=1.1,
            concrete_cover=0.05,
            wearing_coat_thickness=geom.wearing_coat,
            
            wing_wall_length=3.0,
            wing_wall_thickness=0.45,
            wing_wall_splay_angle=45.0
        )
