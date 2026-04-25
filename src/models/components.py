from pydantic import BaseModel, Field
from typing import Optional
import datetime

class BridgeParameters(BaseModel):
    """Parameters for bridge drawing generation, mapped to Bridge_GAD_Yogendra_Borse standards."""
    
    # General Project Info
    project_name: str = Field("Standard Bridge Project", description="Name of the project")
    drawing_no: str = Field("GAD-001", description="Drawing reference number")
    client: str = Field("Client Name", description="Client name")
    consultant: str = Field("Consultant Name", description="Consultant name")
    engineer_name: str = Field("Design Engineer", description="Engineer Name")
    date: str = Field(default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d"))
    scale: str = Field("1:100", description="Drawing Scale")
    
    # Bridge Geometry & Spans
    number_of_spans: int = Field(3, description="NSPAN - Total number of spans")
    span_length: float = Field(14.0, description="SPAN - Clear/Effective Span Length in meters")
    carriage_width: float = Field(7.5, description="CCBR - Carriageway Width in meters")
    footpath_width: float = Field(1.5, description="Footpath Width in meters")
    skew_angle: float = Field(0.0, description="Skew angle in degrees")
    
    # Deck Slab Details
    slab_thickness: float = Field(0.45, description="SLBTHE - Thickness of deck slab")
    wearing_coat_thickness: float = Field(0.075, description="Thickness of wearing coat")
    parapet_height: float = Field(1.0, description="Height of crash barrier/parapet")
    parapet_width: float = Field(0.45, description="Width of crash barrier/parapet at base")
    haunch_size: float = Field(0.15, description="Haunch dimension (x and y)")
    approach_slab_length: float = Field(3.5, description="Length of approach slabs on both ends")
    approach_slab_thickness: float = Field(0.3, description="Thickness of approach slab")
    
    # Pier Details
    pier_width: float = Field(1.2, description="PIERTW - Pier shaft width/diameter")
    pier_cap_width: float = Field(2.5, description="Width of pier cap")
    pier_cap_height: float = Field(0.5, description="Height of pier cap straight portion")
    
    # Abutment Details
    abutment_type: str = Field("Cantilever", description="Type of abutment (Gravity, Cantilever, Counterfort)")
    abutment_top_width: float = Field(1.5, description="Top width of abutment wall / stem")
    abutment_bottom_width: float = Field(2.0, description="Bottom width of abutment wall (Gravity)")
    abutment_stem_thickness: float = Field(1.0, description="Thickness of stem (Cantilever/Counterfort)")
    abutment_toe_length: float = Field(1.5, description="Toe length of base slab")
    abutment_heel_length: float = Field(2.5, description="Heel length of base slab")
    abutment_counterfort_spacing: float = Field(3.0, description="Spacing between counterforts")
    abutment_front_batter: float = Field(10.0, description="Front face batter (1 in X) for Gravity")
    gravity_heel_offset: float = Field(0.5, description="Bottom offset on heel side for Gravity")
    gravity_toe_offset: float = Field(0.5, description="Bottom offset on toe side for Gravity")
    pcc_offset: float = Field(0.150, description="PCC offset beyond foundation edges")
    
    # Levels (Elevations & NSL)
    rtl: float = Field(100.500, description="RTL - Road Top Level")
    hfl: float = Field(98.200, description="HFL - High Flood Level")
    bed_level: float = Field(95.000, description="River Bed Level")
    datum: float = Field(85.000, description="DATUM - Reference datum for drawing")
    
    nsl_left: float = Field(100.000, description="NSL_L - Natural Surface Level at Left Abutment")
    nsl_center: float = Field(99.500, description="NSL_C - Natural Surface Level at Central Pier")
    nsl_right: float = Field(99.800, description="NSL_R - Natural Surface Level at Right Abutment")
    
    # Foundation Details
    foundation_type: str = Field("Open Foundation", description="Type of foundation (Open Foundation, Pile Cap)")
    futw: float = Field(4.0, description="FUTW - Foundation Width")
    futd: float = Field(2.0, description="FUTD - Foundation Depth below NSL")
    foundation_thickness: float = Field(1.5, description="Thickness of the Raft/Pile Cap")
    pile_depth: float = Field(15.0, description="Depth of piles (if Pile Cap)")
    pile_diameter: float = Field(1.0, description="Diameter of piles (if Pile Cap)")
    
    # Material Specifications
    concrete_grade: str = Field("M35", description="Grade of concrete")
    steel_grade: str = Field("Fe500", description="Grade of reinforcing steel")
    concrete_cover: float = Field(0.050, description="Concrete clear cover in meters")

    @property
    def total_length(self) -> float:
        """Calculate total length of the bridge deck."""
        return self.span_length * self.number_of_spans
    
    @property
    def total_width(self) -> float:
        """Calculate total width of the bridge."""
        return self.carriage_width + (2 * self.footpath_width)
