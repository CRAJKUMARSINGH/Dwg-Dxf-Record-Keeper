"""
Preview Widget
==============
Integrated Matplotlib canvas for real-time 2D bridge geometry previews.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class PreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        
        self.figure = Figure(figsize=(8, 4), facecolor='#0d1117')
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#0d1117')
        self._setup_axes()

    def _setup_axes(self):
        self.ax.clear()
        self.ax.set_facecolor('#0d1117')
        self.ax.tick_params(colors='#8b949e', labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_color('#30363d')
        self.ax.grid(True, color='#30363d', linestyle='--', alpha=0.5)

    def update_preview(self, project):
        """Redraws the bridge based on current project parameters."""
        try:
            self._setup_axes()
            
            geom = project.geometry
            levels = project.levels
            
            # 1. Draw Road Top (RTL)
            total_len = sum(geom.span_lengths)
            self.ax.plot([0, total_len], [levels.road_level, levels.road_level], 
                         color='#00d4ff', linewidth=2, label="RTL")
            
            # 2. Draw Deck Bottom
            deck_bot = levels.road_level - geom.slab_thickness
            self.ax.plot([0, total_len], [deck_bot, deck_bot], 
                         color='#8b949e', linewidth=1)
            
            # 3. Draw NSL Terrain
            x_nsl = [0, total_len / 2, total_len]
            y_nsl = [levels.nsl_left, levels.nsl_pier, levels.nsl_right]
            self.ax.plot(x_nsl, y_nsl, color='#39ff14', linestyle='--', label="NSL")
            
            # 4. Draw Piers & Abutments
            from ..models.bridge_schema import PierType
            
            # Abutments
            self.ax.fill_between([-1, 0], [deck_bot, deck_bot], [levels.nsl_left - 2, levels.nsl_left - 2], 
                                 color='#30363d', alpha=0.5)
            self.ax.fill_between([total_len, total_len + 1], [deck_bot, deck_bot], [levels.nsl_right - 2, levels.nsl_right - 2], 
                                 color='#30363d', alpha=0.5)
            
            # Piers
            sub = project.substructure
            current_x = 0
            for i in range(len(geom.span_lengths) - 1):
                current_x += geom.span_lengths[i]
                nsl_at_x = np.interp(current_x, [0, total_len / 2, total_len], [levels.nsl_left, levels.nsl_pier, levels.nsl_right])
                
                # Dynamic Pier Visualization
                pw = sub.pier_width
                ph = sub.pier_height
                
                if sub.pier_type == PierType.HAMMERHEAD:
                    cw = sub.cap_beam_width
                    cd = sub.cap_beam_depth
                    # Draw Cap
                    self.ax.fill_between([current_x - cw/2, current_x + cw/2], 
                                         [deck_bot - 0.1, deck_bot - 0.1], 
                                         [deck_bot - 0.1 - cd, deck_bot - 0.1 - cd], color='#00d4ff', alpha=0.8)
                    # Draw Shaft
                    self.ax.fill_between([current_x - pw/2, current_x + pw/2], 
                                         [deck_bot - cd, deck_bot - cd], 
                                         [nsl_at_x - 3, nsl_at_x - 3], color='#8b949e', alpha=0.7)
                else:
                    # Default Wall/Column type
                    self.ax.fill_between([current_x - pw/2, current_x + pw/2], 
                                         [deck_bot - 0.1, deck_bot - 0.1], 
                                         [nsl_at_x - 3, nsl_at_x - 3], color='#8b949e', alpha=0.7)

            self.ax.set_title(f"BRIDGE PREVIEW: {project.metadata.project_name}", color='white', pad=10)

            self.ax.set_aspect('equal', adjustable='datalim')
            self.canvas.draw()
        except Exception as e:
            self.ax.clear()
            self.ax.text(0.5, 0.5, f"Preview Error:\n{str(e)}\n\nCheck DLLs or Matplotlib installation.", 
                         color='#ff9900', ha='center', va='center', transform=self.ax.transAxes)
            self.canvas.draw()

