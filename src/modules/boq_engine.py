"""
BOQ Engine
==========
Calculates quantities (Concrete, Steel, Earthwork) for the bridge project.
"""

from models.bridge_schema import BridgeProject

class BOQEngine:
    def __init__(self, project: BridgeProject):
        self.project = project

    def calculate_all(self):
        """Returns a dictionary of calculated quantities."""
        results = {
            "Concrete_Deck_m3": self.calc_deck_concrete(),
            "Concrete_Piers_m3": self.calc_pier_concrete(),
            "Concrete_Abutments_m3": self.calc_abutment_concrete(),
            "Concrete_Foundations_m3": self.calc_found_concrete(),
            "Steel_Total_MT": 0.0,
            "Excavation_m3": self.calc_excavation(),
        }
        
        # Simple steel estimation (approx 120kg/m3 for bridge structure)
        total_conc = (results["Concrete_Deck_m3"] + results["Concrete_Piers_m3"] + 
                      results["Concrete_Abutments_m3"] + results["Concrete_Foundations_m3"])
        results["Steel_Total_MT"] = (total_conc * 120) / 1000.0
        
        return results

    def calc_deck_concrete(self):
        geom = self.project.geometry
        total_len = sum(geom.span_lengths)
        # Slab + Kerbs
        volume = total_len * geom.carriageway_width * geom.slab_thickness
        volume += total_len * (geom.kerb_width * 2) * 0.3 # Approx kerb height
        return round(volume, 2)

    def calc_pier_concrete(self):
        geom = self.project.geometry
        sub = self.project.substructure
        levels = self.project.levels
        
        num_piers = geom.number_of_spans - 1
        if num_piers <= 0: return 0.0
        
        # Approx height from bed to deck bottom
        avg_h = (levels.road_level - geom.slab_thickness) - levels.bed_level
        
        # Shaft volume (approx rectangular)
        shaft_vol = sub.pier_width * geom.carriageway_width * avg_h
        
        # Pier Cap volume
        cap_vol = sub.pier_cap_width * geom.carriageway_width * sub.pier_cap_height
        
        return round((shaft_vol + cap_vol) * num_piers, 2)

    def calc_abutment_concrete(self):
        geom = self.project.geometry
        sub = self.project.substructure
        levels = self.project.levels
        
        # Stem height
        h_l = (levels.road_level - geom.slab_thickness) - levels.nsl_left
        h_r = (levels.road_level - geom.slab_thickness) - levels.nsl_right
        
        # Approx stem volume (2 abutments)
        # width x thickness x height
        stem_vol = geom.carriageway_width * 1.0 * (h_l + h_r)
        return round(stem_vol, 2)

    def calc_found_concrete(self):
        geom = self.project.geometry
        found = self.project.foundation
        
        num_supports = geom.number_of_spans + 1
        # Foundation block: Width x Width (square) x Thickness
        vol_per_found = found.width * found.width * found.thickness
        return round(vol_per_found * num_supports, 2)

    def calc_excavation(self):
        found = self.project.foundation
        geom = self.project.geometry
        
        num_supports = geom.number_of_spans + 1
        # Foundation width + 1m working space
        pit_w = found.width + 2.0
        vol_per_pit = pit_w * pit_w * found.depth_below_nsl
        return round(vol_per_pit * num_supports, 2)
