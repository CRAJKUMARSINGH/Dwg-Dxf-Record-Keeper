"""
Design Checks - IRC Compliance
==============================
Validates bridge parameters against IRC:112, IRC:SP:13, and general engineering rules.
"""

from models.bridge_schema import BridgeProject

class DesignChecker:
    def __init__(self, project: BridgeProject):
        self.project = project

    def run_all_checks(self):
        """Runs all validation rules and returns a list of warnings."""
        warnings = []
        
        warnings.extend(self.check_span_depth_ratio())
        warnings.extend(self.check_min_thickness())
        warnings.extend(self.check_freeboard())
        warnings.extend(self.check_road_width())
        
        return warnings

    def check_span_depth_ratio(self):
        """Checks if slab thickness is reasonable for the span (L/D ~ 12-15)."""
        geom = self.project.geometry
        max_span = max(geom.span_lengths)
        ratio = max_span / geom.slab_thickness
        
        if ratio > 18:
            return [f"⚠️ SLENDER SLAB: L/D ratio is {ratio:.1f}. Recommendation: Increase slab thickness to > {max_span/15:.2f}m."]
        elif ratio < 8:
            return [f"ℹ️ HEAVY SLAB: L/D ratio is {ratio:.1f}. Slab may be over-designed for this span."]
        return []

    def check_min_thickness(self):
        """Minimum slab thickness check as per IRC."""
        if self.project.geometry.slab_thickness < 0.40:
            return ["❌ MIN THICKNESS: RCC slab thickness should be at least 400mm for structural integrity."]
        return []

    def check_freeboard(self):
        """Vertical clearance between HFL and Deck bottom."""
        levels = self.project.levels
        geom = self.project.geometry
        deck_bot = levels.road_level - geom.slab_thickness
        freeboard = deck_bot - levels.hfl
        
        if freeboard < 0.6:
            return [f"❌ LOW FREEBOARD: Clearance ({freeboard:.2f}m) is below recommended 0.6m. Risk of flooding/impact."]
        return []

    def check_road_width(self):
        """Check for standard carriageway widths."""
        w = self.project.geometry.carriageway_width
        if w < 7.5 and w != 3.75:
            return [f"ℹ️ NON-STANDARD WIDTH: Carriageway ({w}m) is not standard (3.75m Single, 7.5m Double)."]
        return []
