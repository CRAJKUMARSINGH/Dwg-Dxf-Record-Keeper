"""
Bridge Suite Schema
===================
Pydantic models for all bridge types, quantity metadata, and project settings.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class BridgeType(str, Enum):
    RCC_SLAB = "RCC Slab Bridge"
    T_BEAM = "T-Beam Bridge"
    PSC_GIRDER = "PSC Girder Bridge"
    BOX_CULVERT = "Box Culvert"
    MINOR_BRIDGE = "Minor Bridge"
    CAUSEWAY = "Causeway"

class FoundationType(str, Enum):
    OPEN = "Open Foundation"
    PILE = "Pile Foundation"
    WELL = "Well Foundation"

class SeismicZone(str, Enum):
    ZONE_II = "Zone II"
    ZONE_III = "Zone III"
    ZONE_IV = "Zone IV"
    ZONE_V = "Zone V"

class IRCLoadClass(str, Enum):
    CLASS_70R = "IRC Class 70R"
    CLASS_A = "IRC Class A"
    CLASS_70R_A = "IRC Class 70R + Class A"
    CLASS_B = "IRC Class B"

class ConcreteGrade(str, Enum):
    M25 = "M25"
    M30 = "M30"
    M35 = "M35"
    M40 = "M40"
    M45 = "M45"
    M50 = "M50"

class SteelGrade(str, Enum):
    FE415 = "Fe415"
    FE500 = "Fe500"
    FE500D = "Fe500D"
    FE550 = "Fe550"

class PierType(str, Enum):
    WALL = "Wall Type"
    HAMMERHEAD = "Hammerhead"
    SINGLE_COLUMN = "Single Column"
    TWIN_COLUMN = "Twin Column"
    PORTAL = "Portal"
    CIRCULAR = "Circular"

class CrossingType(str, Enum):
    RIVER = "River Crossing"
    ROAD = "Road Crossing"
    RAILWAY = "Railway Crossing"


class ProjectMetadata(BaseModel):
    project_name: str = "BridgeMaster Pro Project"
    client: str = "PWD / NHAI"
    location: str = "India"
    seismic_zone: SeismicZone = SeismicZone.ZONE_III
    wind_zone: str = "33 m/s"
    load_class: IRCLoadClass = IRCLoadClass.CLASS_70R
    crossing_type: CrossingType = CrossingType.RIVER

class MaterialParams(BaseModel):
    concrete_grade_deck: ConcreteGrade = ConcreteGrade.M35
    concrete_grade_sub: ConcreteGrade = ConcreteGrade.M30
    steel_grade: SteelGrade = SteelGrade.FE500D
    clear_cover_slab: float = 0.050
    clear_cover_pier: float = 0.075


class GeometryParams(BaseModel):
    number_of_spans: int = 3
    span_lengths: List[float] = [14.0, 14.0, 14.0]
    carriageway_width: float = 7.5
    footpath_width: float = 1.5
    kerb_width: float = 0.45
    wearing_coat: float = 0.075
    slab_thickness: float = 0.45

class SubstructureParams(BaseModel):
    pier_type: PierType = PierType.WALL
    pier_height: float = 8.0
    pier_width: float = 1.2
    pier_length: float = 8.5
    number_of_columns: int = 1
    stem_thickness: float = 0.6
    cap_beam_width: float = 1.5
    cap_beam_depth: float = 1.2
    bearing_type: str = "Elastomeric"
    
    # Abutment details (for GAD)
    abutment_type: str = "Cantilever"
    abutment_stem_thickness: float = 0.6
    abutment_heel_length: float = 2.5
    abutment_toe_length: float = 1.0
    gravity_heel_offset: float = 0.6
    gravity_toe_offset: float = 0.3
    
    wing_wall_type: str = "Splayed"
    wing_wall_length: float = 4.0
    wing_wall_thickness: float = 0.4
    wing_wall_splay_angle: float = 30.0



class FoundationParams(BaseModel):
    type: FoundationType = FoundationType.OPEN
    width: float = 4.0
    depth_below_nsl: float = 2.0
    thickness: float = 1.5
    pcc_offset: float = 0.15

class LevelsParams(BaseModel):
    datum: float = 85.0
    nsl_left: float = 100.0
    nsl_pier: float = 99.5
    nsl_right: float = 99.8
    hfl: float = 98.2
    bed_level: float = 95.0
    road_level: float = 100.5

class DeckParams(BaseModel):
    crash_barrier_height: float = 1.0
    railing_height: float = 1.1
    expansion_gap: float = 0.04

class BridgeProject(BaseModel):
    """Root project model for .brg files"""
    version: str = "1.0.0"
    bridge_type: BridgeType = BridgeType.RCC_SLAB
    metadata: ProjectMetadata = Field(default_factory=ProjectMetadata)
    materials: MaterialParams = Field(default_factory=MaterialParams)
    geometry: GeometryParams = Field(default_factory=GeometryParams)
    substructure: SubstructureParams = Field(default_factory=SubstructureParams)
    foundation: FoundationParams = Field(default_factory=FoundationParams)
    levels: LevelsParams = Field(default_factory=LevelsParams)
    deck: DeckParams = Field(default_factory=DeckParams)
    
    # BOQ Summary Cache
    boq_summary: Dict[str, float] = {}

    def to_dict(self):
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    @property
    def total_length(self) -> float:
        return sum(self.geometry.span_lengths) if hasattr(self.geometry, "span_lengths") else 0.0

