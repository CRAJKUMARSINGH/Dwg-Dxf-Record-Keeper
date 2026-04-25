"""
Project Manager
===============
Handles serialization/deserialization of BridgeProject models to .brg files.
"""

import json
from pathlib import Path
from models.bridge_schema import BridgeProject
import logging

logger = logging.getLogger(__name__)

class ProjectManager:
    def __init__(self, last_project_path: str = None):
        self.current_project = BridgeProject()
        self.current_path: Path = Path(last_project_path) if last_project_path else None

    def new_project(self):
        """Reset current project to defaults."""
        self.current_project = BridgeProject()
        self.current_path = None
        logger.info("New project created.")

    def load_project(self, file_path: str) -> bool:
        """Load project from .brg (JSON) file."""
        path = Path(file_path)
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            self.current_project = BridgeProject.from_dict(data)
            self.current_path = path
            logger.info(f"Project loaded: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load project: {e}")
            return False

    def save_project(self, file_path: str = None) -> bool:
        """Save project to .brg file."""
        path = Path(file_path) if file_path else self.current_path
        if not path:
            logger.error("No path provided for saving.")
            return False
        
        # Ensure .brg extension
        if path.suffix != ".brg":
            path = path.with_suffix(".brg")
        
        try:
            with open(path, 'w') as f:
                json.dump(self.current_project.to_dict(), f, indent=4)
            self.current_path = path
            logger.info(f"Project saved: {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save project: {e}")
            return False

    def get_project_summary(self) -> str:
        """Returns a string summary for display in the UI status bar."""
        p = self.current_project
        return f"{p.metadata.project_name} | {p.bridge_type.value} | {p.geometry.number_of_spans} Spans"
