import os
import subprocess
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DWGConverter:
    """Wraps ODA File Converter for converting DWG to DXF."""
    
    def __init__(self, oda_path: str):
        self.oda_path = Path(oda_path)
        if not self.oda_path.exists():
            logger.warning(f"ODA File Converter not found at {oda_path}. DWG conversion may fail unless ezdxf.addons.odafc is configured globally.")
            
    def convert_directory(self, input_dir: Path, output_dir: Path, output_version="ACAD2018", output_format="DXF") -> bool:
        if not self.oda_path.exists():
            logger.error("Cannot run ODA Converter; executable not found.")
            return False
            
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            str(self.oda_path),
            str(input_dir),
            str(output_dir),
            output_version,
            output_format,
            "1", # Recurse
            "1"  # Audit
        ]
        
        try:
            logger.info(f"Running ODA Converter on {input_dir}...")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info("Conversion complete.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"ODA Converter failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Error executing ODA Converter: {e}")
            return False
