"""
DWG Converter
==============
Wraps ODA File Converter for DWG→DXF conversion.
Falls back to ezdxf.addons.odafc if ODA path is not available.
"""

import os
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DWGConverter:
    """Wraps ODA File Converter for converting DWG to DXF."""

    def __init__(self, oda_path: str = ""):
        self.oda_path = Path(oda_path) if oda_path else Path("")
        self._has_oda = self.oda_path.exists() if oda_path else False
        self._has_odafc = False

        if not self._has_oda:
            try:
                from ezdxf.addons import odafc
                self._has_odafc = True
                logger.info("Using ezdxf.addons.odafc for DWG conversion.")
            except ImportError:
                logger.warning(
                    "ODA File Converter not found at '%s' and ezdxf.addons.odafc "
                    "not available. DWG files will be skipped.", oda_path
                )

    @property
    def available(self) -> bool:
        return self._has_oda or self._has_odafc

    def convert_file(self, input_file: Path, output_dir: Path,
                     output_version: str = "ACAD2018") -> Path | None:
        """Convert a single DWG file to DXF. Returns output path or None."""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / (input_file.stem + ".dxf")

        if self._has_odafc:
            try:
                from ezdxf.addons import odafc
                odafc.convert(str(input_file), str(output_file))
                logger.info("Converted (odafc): %s", input_file.name)
                return output_file
            except Exception as e:
                logger.warning("odafc conversion failed for %s: %s", input_file.name, e)

        if self._has_oda:
            try:
                cmd = [
                    str(self.oda_path),
                    str(input_file.parent),
                    str(output_dir),
                    output_version,
                    "DXF", "0", "1",
                ]
                subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=120)
                if output_file.exists():
                    logger.info("Converted (ODA): %s", input_file.name)
                    return output_file
            except Exception as e:
                logger.warning("ODA conversion failed for %s: %s", input_file.name, e)

        return None

    def convert_directory(self, input_dir: Path, output_dir: Path,
                          output_version: str = "ACAD2018") -> int:
        """Batch convert all DWG files. Returns count of successful conversions."""
        dwg_files = sorted(input_dir.rglob("*.dwg"))
        if not dwg_files:
            logger.info("No .dwg files found in %s", input_dir)
            return 0

        logger.info("Converting %d DWG files from %s ...", len(dwg_files), input_dir)
        success = 0
        for i, dwg in enumerate(dwg_files, 1):
            logger.info("[%d/%d] Converting %s", i, len(dwg_files), dwg.name)
            result = self.convert_file(dwg, output_dir, output_version)
            if result:
                success += 1

        logger.info("DWG conversion: %d/%d successful", success, len(dwg_files))
        return success
