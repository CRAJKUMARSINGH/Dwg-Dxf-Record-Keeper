import ezdxf
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class DXFParser:
    """Robust parser for DXF files using ezdxf."""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.doc = None
        self.msp = None
        
    def load(self) -> bool:
        try:
            self.doc = ezdxf.readfile(str(self.file_path))
            self.msp = self.doc.modelspace()
            return True
        except IOError:
            logger.error(f"Not a DXF file or a generic I/O error: {self.file_path}")
            return False
        except ezdxf.DXFStructureError as e:
            logger.error(f"Invalid or corrupted DXF file {self.file_path}: {e}")
            return False
            
    def get_layers(self) -> List[str]:
        if not self.doc: return []
        return [layer.dxf.name for layer in self.doc.layers]
        
    def get_blocks(self) -> List[str]:
        if not self.doc: return []
        return [block.name for block in self.doc.blocks if not block.name.startswith('*')]
        
    def get_text_content(self) -> List[str]:
        if not self.msp: return []
        texts = []
        for text in self.msp.query('TEXT MTEXT'):
            if text.dxftype() == 'TEXT':
                texts.append(text.dxf.text)
            elif text.dxftype() == 'MTEXT':
                texts.append(text.text)
        return texts
        
    def get_entity_counts(self) -> Dict[str, int]:
        if not self.msp: return {}
        counts = {}
        for entity in self.msp:
            dxftype = entity.dxftype()
            counts[dxftype] = counts.get(dxftype, 0) + 1
        return counts
        
    def analyze(self) -> Dict[str, Any]:
        if not self.load():
            return {"error": "Failed to load"}
            
        return {
            "filename": self.file_path.name,
            "layers": self.get_layers(),
            "blocks": self.get_blocks(),
            "texts": self.get_text_content(),
            "entity_counts": self.get_entity_counts()
        }
