"""
Parameter Panel
===============
Dynamic property grid for editing bridge parameters.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, 
    QDoubleSpinBox, QSpinBox, QComboBox, QLabel,
    QScrollArea, QGroupBox
)
from PySide6.QtCore import Signal

class ParameterPanel(QWidget):
    # Signal emitted whenever a parameter changes
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.NoFrame)
        
        self.container = QWidget()
        self.form_layout = QFormLayout(self.container)
        self.scroll.setWidget(self.container)
        
        self.layout.addWidget(self.scroll)
        self.current_project = None

    def load_section(self, section_name, project):
        """Rebuilds the form based on the selected sidebar section."""
        self.current_project = project
        self._clear_layout()
        
        if section_name == "Project Info":
            self._add_info_fields(project.metadata)
        elif section_name == "Environment & Materials":
            self._add_environment_fields(project)
        elif section_name == "Bridge Geometry":
            self._add_geometry_fields(project.geometry)
        elif section_name == "Pier Details":
            self._add_pier_fields(project.substructure)
        elif section_name == "Foundation":
            self._add_foundation_fields(project.foundation)
        elif section_name == "Levels & NSL":
            self._add_levels_fields(project.levels)

    def _add_environment_fields(self, project):
        meta = project.metadata
        mat = project.materials
        
        # Seismic Zone
        from ..models.bridge_schema import SeismicZone
        combo_seismic = QComboBox()
        combo_seismic.addItems([z.value for z in SeismicZone])
        combo_seismic.setCurrentText(meta.seismic_zone.value)
        combo_seismic.currentTextChanged.connect(lambda v: setattr(meta, "seismic_zone", v) or self.changed.emit())
        self.form_layout.addRow("Seismic Zone", combo_seismic)
        
        # Materials Group
        mat_group = QGroupBox("Material Grades")
        mat_form = QFormLayout(mat_group)
        
        from ..models.bridge_schema import ConcreteGrade, SteelGrade
        combo_m = QComboBox()
        combo_m.addItems([g.value for g in ConcreteGrade])
        combo_m.setCurrentText(mat.concrete_grade_sub.value)
        combo_m.currentTextChanged.connect(lambda v: setattr(mat, "concrete_grade_sub", v) or self.changed.emit())
        mat_form.addRow("Concrete Grade (Sub)", combo_m)
        
        self.form_layout.addRow(mat_group)

    def _add_pier_fields(self, sub):
        # Pier Type
        from ..models.bridge_schema import PierType
        combo_pier = QComboBox()
        combo_pier.addItems([p.value for p in PierType])
        combo_pier.setCurrentText(sub.pier_type.value)
        combo_pier.currentTextChanged.connect(lambda v: self._on_pier_type_changed(v, sub))
        self.form_layout.addRow("Pier Type", combo_pier)
        
        # Geometry
        spin_h = QDoubleSpinBox()
        spin_h.setRange(2.0, 50.0)
        spin_h.setValue(sub.pier_height)
        spin_h.valueChanged.connect(lambda v: setattr(sub, "pier_height", v) or self.changed.emit())
        self.form_layout.addRow("Pier Height (m)", spin_h)
        
        spin_cols = QSpinBox()
        spin_cols.setRange(1, 4)
        spin_cols.setValue(sub.number_of_columns)
        spin_cols.valueChanged.connect(lambda v: setattr(sub, "number_of_columns", v) or self.changed.emit())
        self.form_layout.addRow("Number of Columns", spin_cols)

    def _on_pier_type_changed(self, value, sub):
        sub.pier_type = value
        self.load_section("Pier Details", self.current_project)
        self.changed.emit()


    def _clear_layout(self):
        while self.form_layout.count():
            child = self.form_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _add_info_fields(self, metadata):
        # Project Name
        edit_name = QLineEdit(metadata.project_name)
        edit_name.textChanged.connect(lambda v: setattr(metadata, "project_name", v) or self.changed.emit())
        self.form_layout.addRow("Project Name", edit_name)
        
        # Client
        edit_client = QLineEdit(metadata.client)
        edit_client.textChanged.connect(lambda v: setattr(metadata, "client", v) or self.changed.emit())
        self.form_layout.addRow("Client", edit_client)

    def _add_geometry_fields(self, geometry):
        # Spans
        spin_spans = QSpinBox()
        spin_spans.setRange(1, 10) # Limit to 10 for performance
        spin_spans.setValue(geometry.number_of_spans)
        spin_spans.valueChanged.connect(self._on_spans_changed)
        self.form_layout.addRow("Number of Spans", spin_spans)
        
        # Width
        spin_width = QDoubleSpinBox()
        spin_width.setRange(3.75, 25.0) # Standard carriageway ranges
        spin_width.setSingleStep(0.5)
        spin_width.setValue(geometry.carriageway_width)
        spin_width.valueChanged.connect(lambda v: setattr(geometry, "carriageway_width", v) or self.changed.emit())
        self.form_layout.addRow("Carriageway Width (m)", spin_width)
        
        # Slab Thickness
        spin_thick = QDoubleSpinBox()
        spin_thick.setRange(0.4, 3.5) # RCC Slab/T-Beam limits
        spin_thick.setSingleStep(0.05)
        spin_thick.setValue(geometry.slab_thickness)
        spin_thick.valueChanged.connect(lambda v: setattr(geometry, "slab_thickness", v) or self.changed.emit())
        self.form_layout.addRow("Slab/Girder Depth (m)", spin_thick)

    def _add_levels_fields(self, levels):
        # Road Level
        spin_rl = QDoubleSpinBox()
        spin_rl.setRange(0, 8000) # Support high altitude
        spin_rl.setDecimals(3)
        spin_rl.setValue(levels.road_level)
        spin_rl.valueChanged.connect(lambda v: setattr(levels, "road_level", v) or self.changed.emit())
        self.form_layout.addRow("Road Top Level (RTL)", spin_rl)
        
        # HFL
        spin_hfl = QDoubleSpinBox()
        spin_hfl.setRange(0, 8000)
        spin_hfl.setDecimals(3)
        spin_hfl.setValue(levels.hfl)
        spin_hfl.valueChanged.connect(lambda v: setattr(levels, "hfl", v) or self.changed.emit())
        self.form_layout.addRow("HFL", spin_hfl)

        # NSL Left
        spin_nl = QDoubleSpinBox()
        spin_nl.setRange(0, 8000)
        spin_nl.setDecimals(3)
        spin_nl.setValue(levels.nsl_left)
        spin_nl.valueChanged.connect(lambda v: setattr(levels, "nsl_left", v) or self.changed.emit())
        self.form_layout.addRow("NSL Left", spin_nl)


    def _on_spans_changed(self, value):
        self.current_project.geometry.number_of_spans = value
        # Update span lengths list if needed
        while len(self.current_project.geometry.span_lengths) < value:
            self.current_project.geometry.span_lengths.append(14.0)
        self.changed.emit()

    # Add other field methods as needed...
    def _add_substructure_fields(self, sub):
        # 1. Pier Parameters
        pier_group = QGroupBox("Pier Details")
        pier_form = QFormLayout(pier_group)
        
        spin_pw = QDoubleSpinBox()
        spin_pw.setRange(0.5, 5.0)
        spin_pw.setValue(sub.pier_width)
        spin_pw.valueChanged.connect(lambda v: setattr(sub, "pier_width", v) or self.changed.emit())
        pier_form.addRow("Pier Width (m)", spin_pw)
        
        self.form_layout.addRow(pier_group)

        # 2. Abutment Parameters
        abut_group = QGroupBox("Abutment Details")
        abut_form = QFormLayout(abut_group)
        
        combo_type = QComboBox()
        combo_type.addItems(["Cantilever", "Gravity", "Counterfort"])
        combo_type.setCurrentText(sub.abutment_type)
        combo_type.currentTextChanged.connect(lambda v: self._on_abutment_type_changed(v, sub))
        abut_form.addRow("Abutment Type", combo_type)

        # Conditional Fields based on type
        if sub.abutment_type in ["Cantilever", "Counterfort"]:
            spin_stem = QDoubleSpinBox()
            spin_stem.setRange(0.3, 2.0)
            spin_stem.setValue(sub.abutment_stem_thickness)
            spin_stem.valueChanged.connect(lambda v: setattr(sub, "abutment_stem_thickness", v) or self.changed.emit())
            abut_form.addRow("Stem Thickness (m)", spin_stem)
            
            spin_heel = QDoubleSpinBox()
            spin_heel.setRange(0.5, 6.0)
            spin_heel.setValue(sub.abutment_heel_length)
            spin_heel.valueChanged.connect(lambda v: setattr(sub, "abutment_heel_length", v) or self.changed.emit())
            abut_form.addRow("Heel Length (m)", spin_heel)

        if sub.abutment_type == "Gravity":
            spin_top = QDoubleSpinBox()
            spin_top.setSuffix(" mm")
            spin_top.setRange(300, 3000)
            spin_top.setValue(sub.abutment_top_width * 1000)
            spin_top.valueChanged.connect(lambda v: setattr(sub, "abutment_top_width", v/1000.0) or self.changed.emit())
            abut_form.addRow("Top Width (mm)", spin_top)

            spin_hoff = QDoubleSpinBox()
            spin_hoff.setSuffix(" mm")
            spin_hoff.setRange(0, 2000)
            spin_hoff.setValue(sub.gravity_heel_offset * 1000)
            spin_hoff.valueChanged.connect(lambda v: setattr(sub, "gravity_heel_offset", v/1000.0) or self.changed.emit())
            abut_form.addRow("Heel Offset (mm)", spin_hoff)

            spin_toff = QDoubleSpinBox()
            spin_toff.setSuffix(" mm")
            spin_toff.setRange(0, 2000)
            spin_toff.setValue(sub.gravity_toe_offset * 1000)
            spin_toff.valueChanged.connect(lambda v: setattr(sub, "gravity_toe_offset", v/1000.0) or self.changed.emit())
            abut_form.addRow("Toe Offset (mm)", spin_toff)

        if sub.abutment_type == "Counterfort":
            spin_space = QDoubleSpinBox()
            spin_space.setRange(1.5, 6.0)
            spin_space.setValue(sub.counterfort_spacing)
            spin_space.valueChanged.connect(lambda v: setattr(sub, "counterfort_spacing", v) or self.changed.emit())
            abut_form.addRow("Counterfort Spacing (m)", spin_space)

        self.form_layout.addRow(abut_group)

    def _on_abutment_type_changed(self, value, sub):
        sub.abutment_type = value
        self.load_section("Substructure", self.current_project)
        self.changed.emit()


    def _add_foundation_fields(self, found):
        spin_fw = QDoubleSpinBox()
        spin_fw.setValue(found.width)
        spin_fw.valueChanged.connect(lambda v: setattr(found, "width", v) or self.changed.emit())
        self.form_layout.addRow("Foundation Width (m)", spin_fw)
