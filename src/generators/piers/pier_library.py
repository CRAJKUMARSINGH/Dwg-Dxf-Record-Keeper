"""
Pier Library Base
=================
Abstract base and common logic for all intelligent pier generators.
"""

from typing import Tuple
from abc import ABC, abstractmethod
from ..dxf_builder import DXFBuilder
from ...models.bridge_schema import BridgeProject, PierType

class PierGenerator(ABC):
    """Base class for all parametric pier types."""
    
    def __init__(self, builder: DXFBuilder):
        self.builder = builder

    @abstractmethod
    def draw_elevation(self, project: BridgeProject, insert: Tuple[float, float]):
        """Draw the pier elevation view."""
        pass

    @abstractmethod
    def draw_plan(self, project: BridgeProject, insert: Tuple[float, float]):
        """Draw the pier sectional plan view."""
        pass

    def add_standard_dimensions(self, project: BridgeProject):
        """Add common dimensions based on reference styles."""
        pass

class WallPierGenerator(PierGenerator):
    """Standard Wall-type pier logic."""
    
    def draw_elevation(self, project: BridgeProject, insert: Tuple[float, float]):
        sub = project.substructure
        x, y = insert
        h, w = sub.pier_height, sub.pier_width
        
        # Main stem
        self.builder.add_polyline([
            (x - w/2, y), (x + w/2, y),
            (x + w/2, y + h), (x - w/2, y + h)
        ], layer="st-obj", closed=True)

    def draw_plan(self, project: BridgeProject, insert: Tuple[float, float]):
        sub = project.substructure
        x, y = insert
        w, l = sub.pier_width, sub.pier_length
        self.builder.add_polyline([
            (x - w/2, y - l/2), (x + w/2, y - l/2),
            (x + w/2, y + l/2), (x - w/2, y + l/2)
        ], layer="st-obj", closed=True)

class HammerheadPierGenerator(PierGenerator):
    """Professional Hammerhead pier with chamfered cap logic."""
    
    def draw_elevation(self, project: BridgeProject, insert: Tuple[float, float]):
        sub = project.substructure
        x, y = insert
        h, w = sub.pier_height, sub.pier_width
        cw, cd = sub.cap_beam_width, sub.cap_beam_depth
        
        # Stem
        self.builder.add_polyline([
            (x - w/2, y), (x + w/2, y),
            (x + w/2, y + h - cd), (x - w/2, y + h - cd)
        ], layer="st-obj", closed=True)
        
        # Hammerhead Cap (Chamfered)
        overhang = (cw - w) / 2
        pts = [
            (x - w/2, y + h - cd),
            (x - cw/2, y + h - cd + 0.5), # Chamfer start
            (x - cw/2, y + h),
            (x + cw/2, y + h),
            (x + cw/2, y + h - cd + 0.5),
            (x + w/2, y + h - cd)
        ]
        self.builder.add_polyline(pts, layer="st-obj", closed=True)

    def draw_plan(self, project: BridgeProject, insert: Tuple[float, float]):
        # Plan at shaft level
        sub = project.substructure
        x, y = insert
        w, l = sub.pier_width, sub.pier_length
        self.builder.add_polyline([
            (x - w/2, y - l/2), (x + w/2, y - l/2),
            (x + w/2, y + l/2), (x - w/2, y + l/2)
        ], layer="st-obj", closed=True)
