"""
Main Window - Bridge Suite
==========================
The primary desktop shell containing the Ribbon, Sidebar, and Viewport.
"""

import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QPushButton, QListWidget, QDockWidget,
    QLabel, QStatusBar, QFileDialog, QMessageBox,
    QFrame, QSplitter
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QFont

from modules.project_manager import ProjectManager

from ui.preview_widget import PreviewWidget
from ui.parameter_panel import ParameterPanel

from generators.templates import SheetTemplates
from models.bridge_schema import BridgeType, BridgeProject
from modules.boq_engine import BOQEngine
from modules.design_checks import DesignChecker
from modules.export_service import ExportService
from modules.pdf_service import PDFService

class BridgeSuiteMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BridgeMaster Pro 2026 — Professional Bridge CAD")
        self.setWindowIcon(QIcon("assets/logo.png")) # Future logo
        self.resize(1200, 850)
        
        self.project_manager = ProjectManager()
        self.last_output_dir = str(Path.home() / "Documents")
        
        self._init_ui()
        self._load_theme()
        
        # Initial trigger
        self._new_project()


    def _init_ui(self):
        # 1. Ribbon Area (Top)
        self.ribbon = QTabWidget()
        self.ribbon.setFixedHeight(120)
        self._setup_ribbon_tabs()
        
        # 2. Central Area (Splitter)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.ribbon)
        
        self.content_splitter = QSplitter(Qt.Horizontal)
        
        # 3. Sidebar (Left)
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.addItems([
            "Project Info", 
            "Environment & Materials",
            "Bridge Geometry", 
            "Pier Details", 
            "Foundation", 
            "Levels & NSL"
        ])

        self.sidebar.setCurrentRow(0)
        self.sidebar.currentRowChanged.connect(self._on_sidebar_changed)
        
        # 4. Viewport & Parameters (Right)
        self.view_container = QSplitter(Qt.Vertical)
        
        # Top half: Preview
        self.preview_area = PreviewWidget()
        
        # Bottom half: Parameters
        self.param_area = QFrame()
        self.param_area.setFrameStyle(QFrame.StyledPanel)
        self.param_layout = QVBoxLayout(self.param_area)
        
        self.param_panel = ParameterPanel()
        self.param_panel.changed.connect(self._refresh_preview)
        
        self.param_header = QLabel("Parameters")
        self.param_header.setObjectName("HeaderLabel")
        self.param_layout.addWidget(self.param_header)
        self.param_layout.addWidget(self.param_panel)
        
        self.view_container.addWidget(self.preview_area)
        self.view_container.addWidget(self.param_area)
        self.view_container.setSizes([500, 300])
        
        self.content_splitter.addWidget(self.sidebar)
        self.content_splitter.addWidget(self.view_container)
        
        self.main_layout.addWidget(self.content_splitter)
        
        # 5. Status Bar (Bottom)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def _setup_ribbon_tabs(self):
        # Home Tab
        home_tab = QWidget()
        home_layout = QHBoxLayout(home_tab)
        home_layout.setAlignment(Qt.AlignLeft)
        
        # Project Actions
        proj_group = QVBoxLayout()
        btn_new = QPushButton("New Project")
        btn_new.clicked.connect(self._new_project)
        btn_open = QPushButton("Open Project")
        btn_open.clicked.connect(self._open_project)
        btn_save = QPushButton("Save Project")
        btn_save.clicked.connect(self._save_project)
        
        btn_defaults = QPushButton("Load Engineering\nDefaults")
        btn_defaults.clicked.connect(self._load_engineering_defaults)
        btn_defaults.setObjectName("SecondaryButton") # For styling

        proj_group.addWidget(btn_new)
        proj_group.addWidget(btn_open)
        proj_group.addWidget(btn_save)
        proj_group.addWidget(btn_defaults)
        home_layout.addLayout(proj_group)


        
        # Bridge Type Selection
        type_group = QVBoxLayout()
        type_group.addWidget(QLabel("BRIDGE TYPE"))
        self.combo_type = QComboBox()
        self.combo_type.addItems([t.value for t in BridgeType])
        self.combo_type.currentTextChanged.connect(self._on_type_changed)
        type_group.addWidget(self.combo_type)
        type_group.addStretch()
        home_layout.addLayout(type_group)
        
        # Drawing Tab
        draw_tab = QWidget()
        draw_layout = QHBoxLayout(draw_tab)
        draw_layout.setAlignment(Qt.AlignLeft)
        
        btn_gen_gad = QPushButton("Generate GAD")
        btn_gen_gad.clicked.connect(lambda: self._generate_sheets(single="GAD"))
        
        btn_gen_all = QPushButton("Generate\nAll Sheets")
        btn_gen_all.setObjectName("PrimaryButton")
        btn_gen_all.clicked.connect(lambda: self._generate_sheets())
        
        btn_pdf = QPushButton("Export Structural\nDossier (PDF)")
        btn_pdf.clicked.connect(self._export_pdf)
        btn_pdf.setObjectName("SecondaryButton")
        
        draw_layout.addWidget(btn_gen_gad)
        draw_layout.addWidget(btn_gen_all)
        draw_layout.addWidget(btn_pdf)
        
        # BOQ Tab
        boq_tab = QWidget()
        boq_layout = QHBoxLayout(boq_tab)
        boq_layout.setAlignment(Qt.AlignLeft)
        
        btn_calc = QPushButton("Calculate\nQuantities")
        btn_calc.clicked.connect(self._calculate_boq)
        
        btn_exp_xl = QPushButton("Export to\nExcel")
        btn_exp_xl.clicked.connect(self._export_excel)
        
        btn_exp_pdf = QPushButton("Export to\nPDF Report")
        btn_exp_pdf.clicked.connect(self._export_pdf)
        
        boq_layout.addWidget(btn_calc)
        boq_layout.addWidget(btn_exp_xl)
        boq_layout.addWidget(btn_exp_pdf)

        # HELP / COMMERCIAL Tab
        help_tab = QWidget()
        help_layout = QHBoxLayout(help_tab)
        help_layout.setAlignment(Qt.AlignLeft)
        
        btn_about = QPushButton("About\nBridgeMaster")
        btn_about.clicked.connect(self._show_about)
        
        btn_license = QPushButton("License\nActivation")
        btn_license.setEnabled(False) # For Phase 6
        
        btn_manual = QPushButton("Open\nUser Manual")
        btn_manual.clicked.connect(self._open_manual)
        
        help_layout.addWidget(btn_about)
        help_layout.addWidget(btn_license)
        help_layout.addWidget(btn_manual)

        self.ribbon.addTab(home_tab, "HOME")
        self.ribbon.addTab(draw_tab, "DRAWING")
        self.ribbon.addTab(boq_tab, "BOQ / DESIGN")
        self.ribbon.addTab(help_tab, "HELP")


    def _on_type_changed(self, text):
        for t in BridgeType:
            if t.value == text:
                self.project_manager.current_project.bridge_type = t
                break
        self._refresh_preview()

    def _generate_sheets(self, single=None):
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.last_output_dir)
        if not output_dir:
            return
            
        self.last_output_dir = output_dir
        project = self.project_manager.current_project
        try:
            drawings = SheetTemplates.generate_from_project(project)
            
            saved_paths = []
            for name, builder in drawings.items():
                if single and single not in name: continue
                path = Path(output_dir) / f"{name}.dxf"
                builder.save(path)
                saved_paths.append(str(path))
            
            self.status_bar.showMessage(f"SUCCESS: Saved {len(saved_paths)} drawings to {output_dir}")
            QMessageBox.information(self, "Success", f"Generated {len(saved_paths)} drawings in:\n{output_dir}")
        except Exception as e:
            self.status_bar.showMessage(f"ERROR: Generation failed: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to generate drawings: {e}")


    def _load_theme(self):
        theme_path = Path(__file__).parent / "theme.qss"
        if theme_path.exists():
            with open(theme_path, "r") as f:
                self.setStyleSheet(f.read())

    def _load_engineering_defaults(self):
        """Populates the current project with professional engineering seed data."""
        project = self.project_manager.current_project
        bt = project.bridge_type
        
        if bt == BridgeType.RCC_SLAB:
            project.geometry.span_lengths = [12.0, 12.0]
            project.geometry.slab_thickness = 0.85
            project.substructure.abutment_type = "Cantilever"
            project.substructure.abutment_heel_length = 2.5
            project.substructure.abutment_toe_length = 1.0
            
        elif bt == BridgeType.T_BEAM:
            project.geometry.span_lengths = [25.0, 25.0]
            project.geometry.slab_thickness = 1.8
            project.substructure.abutment_type = "Counterfort"
            project.substructure.abutment_heel_length = 3.5
            project.substructure.counterfort_spacing = 3.0
            
        elif bt == BridgeType.BOX_CULVERT:
            project.geometry.span_lengths = [4.0, 4.0]
            project.geometry.slab_thickness = 0.45
            
        self._on_sidebar_changed(self.sidebar.currentRow())
        self._refresh_preview()
        self.status_bar.showMessage("Professional Engineering Defaults Loaded.", 3000)

    def _on_sidebar_changed(self, index):
        if not self.sidebar.currentItem():
            return
        item_text = self.sidebar.currentItem().text()
        self.param_header.setText(f"PARAMETERS: {item_text.upper()}")
        self.param_panel.load_section(item_text, self.project_manager.current_project)

    def _refresh_preview(self):
        project = self.project_manager.current_project
        self.preview_area.update_preview(project)
        
        # Run design checks
        checker = DesignChecker(project)
        warnings = checker.run_all_checks()
        if warnings:
            self.status_bar.showMessage(f"WARNING: {warnings[0]}")
            self.status_bar.setStyleSheet("color: #ff9900;")
        else:
            self.status_bar.showMessage(self.project_manager.get_project_summary())
            self.status_bar.setStyleSheet("color: #8b949e;")

    def _calculate_boq(self):
        engine = BOQEngine(self.project_manager.current_project)
        results = engine.calculate_all()
        
        summary = "\n".join([f"{k}: {v}" for k, v in results.items()])
        QMessageBox.information(self, "BOQ Calculation", f"Quantities Calculated:\n\n{summary}")

    def _export_excel(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export BOQ", "", "Excel Files (*.xlsx)")
        if file_name:
            engine = BOQEngine(self.project_manager.current_project)
            results = engine.calculate_all()
            if ExportService.export_boq_to_excel(self.project_manager.current_project.to_dict(), results, file_name):
                QMessageBox.information(self, "Success", f"BOQ exported successfully to:\n{file_name}")

    def _export_pdf(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Structural Dossier", "", "PDF Files (*.pdf)")
        if file_name:
            from ..modules.bbs_engine import BBSEngine
            from ..modules.pdf_generator import PDFGenerator
            
            project = self.project_manager.current_project
            # 1. Calculate BBS
            engine = BBSEngine(project)
            bbs_entries = engine.calculate_pier_bbs()
            
            # 2. Generate PDF
            if PDFGenerator.generate_dossier(project.to_dict(), bbs_entries, file_name):
                QMessageBox.information(self, "Success", f"Structural Dossier exported to:\n{file_name}")
                self.status_bar.showMessage("PDF Export Successful.", 5000)

    def _export_all_dxf(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export PDF Report", "", "PDF Files (*.pdf)")
        if file_name:
            project = self.project_manager.current_project
            engine = BOQEngine(project)
            results = engine.calculate_all()
            
            checker = DesignChecker(project)
            warnings = checker.run_all_checks()
            
            if PDFService.generate_design_report(project.to_dict(), results, warnings, file_name):
                self.status_bar.showMessage(f"SUCCESS: Exported PDF report to {file_name}")
                QMessageBox.information(self, "Success", f"Design report exported successfully to:\n{file_name}")
            else:
                QMessageBox.critical(self, "Error", "Failed to generate PDF report.")

    def _show_about(self):
        QMessageBox.about(self, "About BridgeMaster Pro", 
            "<h2>BridgeMaster Pro 2026</h2>"
            "<p><b>Version 1.0.0 (Release Candidate)</b></p>"
            "<p>The complete professional Bridge CAD Suite for India.</p>"
            "<hr>"
            "<p>Developed for PWD/NHAI Consultants and Engineers.</p>"
            "<p>© 2026 BridgeMaster Software. All rights reserved.</p>")

    def _open_manual(self):
        manual_path = Path("docs/USER_MANUAL_PHASE4.md").absolute()
        if manual_path.exists():
            import os
            os.startfile(str(manual_path))
        else:
            QMessageBox.warning(self, "Error", "User Manual not found.")

    def _new_project(self):
        self.project_manager.new_project()
        self._on_sidebar_changed(0)
        self._refresh_preview()

    def _open_project(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Bridge Project", "", "Bridge Files (*.brg)")
        if file_name:
            if self.project_manager.load_project(file_name):
                self._on_sidebar_changed(0)
                self._refresh_preview()
                self.setWindowTitle(f"Bridge Suite — {file_name}")

    def _save_project(self):
        if not self.project_manager.current_path:
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Bridge Project", "", "Bridge Files (*.brg)")
            if not file_name:
                return
        else:
            file_name = self.project_manager.current_path
            
        if self.project_manager.save_project(file_name):
            self.status_bar.showMessage("Project Saved Successfully")
            self.setWindowTitle(f"Bridge Suite — {file_name}")



if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = BridgeSuiteMainWindow()
    window.show()
    sys.exit(app.exec())
