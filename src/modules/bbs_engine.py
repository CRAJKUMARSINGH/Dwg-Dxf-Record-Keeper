"""
BBS Engine
==========
Calculates Bar Bending Schedules (BBS) for bridge components.
Outputs cutting lengths, weights, and shape codes according to Indian standards.
"""

from typing import List, Dict
from models.bridge_schema import BridgeProject

class BBSEntry:
    def __init__(self, mark: str, description: str, diameter: int, length: float, quantity: int):
        self.mark = mark
        self.description = description
        self.diameter = diameter
        self.length = length
        self.quantity = quantity
        
    @property
    def total_length(self) -> float:
        return self.length * self.quantity
    
    @property
    def unit_weight(self) -> float:
        # standard formula: d^2 / 162 (kg/m)
        return (self.diameter ** 2) / 162.0
    
    @property
    def total_weight(self) -> float:
        return self.total_length * self.unit_weight

class BBSEngine:
    def __init__(self, project: BridgeProject):
        self.project = project

    def calculate_pier_bbs(self) -> List[BBSEntry]:
        """Calculates reinforcement for the selected pier type."""
        sub = self.project.substructure
        h = sub.pier_height
        w = sub.pier_width
        l = sub.pier_length
        cover = self.project.materials.clear_cover_pier
        
        entries = []
        
        # 1. Main Vertical Bars
        # Assumed 1 bar every 200mm around perimeter
        perimeter = 2 * (w + l)
        count = int(perimeter / 0.2)
        v_len = h + 1.5 # including development length into footing
        entries.append(BBSEntry("P1", "Main Vertical Bars", 20, v_len, count))
        
        # 2. Stirrups (Ties)
        # Assumed 10mm stirrups @ 150 c/c
        s_count = int(h / 0.15)
        s_len = 2 * (w - 2*cover + l - 2*cover) + 0.2 # including hooks
        entries.append(BBSEntry("P2", "Horizontal Stirrups", 10, s_len, s_count))
        
        return entries

    def get_summary(self, entries: List[BBSEntry]) -> Dict[str, float]:
        """Returns total weight per diameter."""
        summary = {}
        for entry in entries:
            d_key = f"{entry.diameter}mm"
            summary[d_key] = summary.get(d_key, 0) + entry.total_weight
        
        summary["Total Weight (kg)"] = sum(summary.values())
        return summary
