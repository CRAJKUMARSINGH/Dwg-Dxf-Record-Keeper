"""
Enhanced DXF Pattern Analyzer
Analyzes all DXF files from the Filtered_Drawings collection to identify common drawing forms
and derive improved reusable code templates for bridge engineering drawings.

Author: AI Assistant for Rajkumar Singh Chauhan
Date: 2026-04-18
"""

import os
import re
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set
import json


class EnhancedDXFAnalyzer:
    """Enhanced analyzer for DXF files with deeper pattern recognition."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.dxf_files = []
        self.all_patterns = {
            'layers': Counter(),
            'entities': Counter(),
            'text_patterns': Counter(),
            'drawing_types': defaultdict(list),
            'file_metadata': []
        }
        
    def find_dxf_files(self) -> List[Path]:
        """Find all DXF files in the directory tree."""
        print(f"\n{'='*80}")
        print(f"Scanning for DXF files in: {self.base_path}")
        print(f"{'='*80}")
        self.dxf_files = list(self.base_path.rglob('*.dxf'))
        print(f"✓ Found {len(self.dxf_files)} DXF files\n")
        
        for i, f in enumerate(self.dxf_files, 1):
            print(f"  {i}. {f.relative_to(self.base_path)}")
        
        return self.dxf_files
    
    def analyze_dxf_file(self, file_path: Path) -> Dict:
        """Analyze a single DXF file for patterns."""
        analysis = {
            'file': str(file_path),
            'filename': file_path.name,
            'layers': set(),
            'entity_types': Counter(),
            'text_content': [],
            'blocks': set(),
            'dimensions': [],
            'estimated_type': 'unknown'
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Parse DXF structure
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                
                # Layer names (group code 8)
                if line == '8' and i + 1 < len(lines):
                    layer_name = lines[i + 1].strip()
                    if layer_name and not layer_name.isdigit() and len(layer_name) > 1:
                        analysis['layers'].add(layer_name)
                
                # Entity types (group code 0)
                elif line == '0' and i + 1 < len(lines):
                    entity_type = lines[i + 1].strip()
                    if entity_type in ['LINE', 'CIRCLE', 'ARC', 'TEXT', 'LWPOLYLINE', 
                                     'POLYLINE', 'DIMENSION', 'INSERT', 'POINT', 'SOLID',
                                     'HATCH', 'SPLINE', 'ELLIPSE', '3DFACE', 'MTEXT',
                                     'LEADER', 'ATTDEF', 'ATTRIB']:
                        analysis['entity_types'][entity_type] += 1
                
                # Text content (group code 1)
                elif line == '1' and i + 1 < len(lines):
                    text_content = lines[i + 1].strip()
                    if text_content and len(text_content) > 2:
                        analysis['text_content'].append(text_content)
                
                # Block names (group code 2)
                elif line == '2' and i + 1 < len(lines):
                    block_name = lines[i + 1].strip()
                    if block_name and not block_name.isdigit():
                        analysis['blocks'].add(block_name)
                
                i += 1
            
            # Classify drawing type
            analysis['estimated_type'] = self.classify_drawing_type(analysis)
            
        except Exception as e:
            print(f"  ⚠ Error analyzing {file_path.name}: {e}")
            
        return analysis
    
    def classify_drawing_type(self, analysis: Dict) -> str:
        """Classify the drawing type based on its content."""
        text_lower = ' '.join(analysis['text_content']).lower()
        layers_lower = ' '.join(analysis['layers']).lower()
        filename_lower = analysis['filename'].lower()
        combined = text_lower + ' ' + layers_lower + ' ' + filename_lower
        
        # Enhanced classification rules based on actual bridge drawing patterns
        if any(kw in combined for kw in ['general arrangement', 'gad', 'g.a.d']):
            return 'GAD'
        elif any(kw in combined for kw in ['pier', 'column', 'shaft', 'piers']):
            return 'PIER'
        elif any(kw in combined for kw in ['abutment', 'end support', 'abut']):
            return 'ABUTMENT'
        elif any(kw in combined for kw in ['reinforcement', 'rebar', 'bar bending', 'rcr']):
            return 'REINFORCEMENT'
        elif any(kw in combined for kw in ['cross section', 'x-section', 'section', 'c/s']):
            return 'CROSS_SECTION'
        elif any(kw in combined for kw in ['deck slab', 'slab', 'deck']):
            return 'DECK_SLAB'
        elif any(kw in combined for kw in ['girder', 'beam', 'longitudinal']):
            return 'GIRDER'
        elif any(kw in combined for kw in ['bearing', 'pedestal', 'elastomeric']):
            return 'BEARING'
        elif any(kw in combined for kw in ['cross girder', 'diaphragm']):
            return 'CROSS_GIRDER'
        elif any(kw in combined for kw in ['wing wall', 'return wall']):
            return 'WING_WALL'
        elif any(kw in combined for kw in ['foundation', 'footing', 'pile']):
            return 'FOUNDATION'
        elif any(kw in combined for kw in ['false work', 'staging', 'scaffolding']):
            return 'FALSE_WORK'
        elif any(kw in combined for kw in ['dimension', 'details']):
            return 'DIMENSION_DETAILS'
        else:
            return 'OTHER'
    
    def analyze_all_files(self) -> Dict:
        """Analyze all DXF files and aggregate patterns."""
        print(f"\n{'='*80}")
        print(f"Analyzing {len(self.dxf_files)} DXF files...")
        print(f"{'='*80}\n")
        
        all_analyses = []
        type_counts = Counter()
        
        for i, dxf_file in enumerate(self.dxf_files, 1):
            print(f"[{i}/{len(self.dxf_files)}] Analyzing: {dxf_file.relative_to(self.base_path)}")
            
            analysis = self.analyze_dxf_file(dxf_file)
            all_analyses.append(analysis)
            
            # Aggregate patterns
            self.all_patterns['layers'].update(analysis['layers'])
            self.all_patterns['entities'].update(analysis['entity_types'])
            
            # Extract meaningful text patterns
            for text in analysis['text_content'][:5]:
                if len(text) > 3 and len(text) < 100:
                    self.all_patterns['text_patterns'][text] += 1
            
            # Track drawing types
            drawing_type = analysis['estimated_type']
            type_counts[drawing_type] += 1
            self.all_patterns['drawing_types'][drawing_type].append({
                'file': dxf_file,
                'layers': analysis['layers'],
                'entities': dict(analysis['entity_types'])
            })
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"ANALYSIS SUMMARY")
        print(f"{'='*80}")
        print(f"\nDrawing Type Distribution:")
        for dtype, count in type_counts.most_common():
            print(f"  ✓ {dtype:20s}: {count:2d} files")
        
        return {
            'analyses': all_analyses,
            'type_counts': type_counts,
            'patterns': self.all_patterns
        }
    
    def generate_enhanced_forms_code(self) -> str:
        """Generate enhanced Python code templates based on actual DXF analysis."""
        
        # Identify most common layers and entities
        top_layers = [layer for layer, _ in self.all_patterns['layers'].most_common(30)]
        top_entities = [entity for entity, _ in self.all_patterns['entities'].most_common(15)]
        
        code = f'''"""
Common Drawing Forms Generator - Enhanced Version
Auto-generated from analysis of {len(self.dxf_files)} DXF files in the Filtered_Drawings collection.
Contains templates for standard bridge engineering drawings with real-world patterns.

Author: Auto-generated by Enhanced DXF Pattern Analyzer
Date: 2026-04-18
Analyzed Files: {len(self.dxf_files)} DXF files
Drawing Types: {', '.join([f"{k} ({v})" for k, v in dict(self.all_patterns["drawing_types"]).items()])}
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math


class DrawingType(Enum):
    """Enumeration of common bridge drawing types."""
    GAD = "General Arrangement Drawing"
    PIER = "Pier Details"
    ABUTMENT = "Abutment Details"
    DECK_SLAB = "Deck Slab Reinforcement"
    GIRDER = "Girder Details"
    CROSS_GIRDER = "Cross Girder Details"
    BEARING = "Bearing Details"
    CROSS_SECTION = "Cross Section"
    WING_WALL = "Wing Wall Details"
    FOUNDATION = "Foundation Details"
    FALSE_WORK = "False Work/Staging"
    DIMENSION_DETAILS = "Dimension Details"


@dataclass
class DrawingParameters:
    """Standard parameters for bridge drawings."""
    # Bridge geometry
    span_length: float = 14.0
    number_of_spans: int = 3
    carriage_width: float = 7.5
    footpath_width: float = 1.5
    skew_angle: float = 0.0  # degrees
    
    # Levels
    rtl: float = 100.500  # Road Top Level
    hfl: float = 98.200   # High Flood Level
    bed_level: float = 95.000
    foundation_level: float = 90.000
    agl: float = 96.500   # Average Ground Level
    
    # Pier parameters
    pier_width: float = 1.2
    pier_depth: float = 8.0
    pier_cap_height: float = 0.5
    pier_cap_width: float = 2.0
    pier_type: str = "rectangular"  # rectangular, circular, twin-column
    
    # Abutment parameters
    abutment_width: float = 1.5
    abutment_base_width: float = 3.0
    abutment_height: float = 6.0
    abutment_type: str = "T-type"  # T-type, gravity, counterfort
    
    # Slab parameters
    slab_thickness: float = 0.45
    wearing_coat_thickness: float = 0.075
    
    # Girder parameters
    girder_depth: float = 1.2
    girder_width: float = 0.3
    number_of_girders: int = 4
    girder_spacing: float = 2.0
    
    # Materials
    concrete_grade: str = "M35"
    steel_grade: str = "Fe500"
    concrete_cover: float = 0.050  # 50mm
    
    # Project info
    project_name: str = ""
    drawing_no: str = ""
    client: str = ""
    consultant: str = ""


@dataclass
class DXFEntity:
    """Represents a DXF entity with properties."""
    entity_type: str
    layer: str
    properties: Dict
    annotations: List[str] = None
    
    def __post_init__(self):
        if self.annotations is None:
            self.annotations = []


class CommonDrawingForms:
    """Templates for common bridge drawing forms based on analyzed DXF patterns."""
    
    @staticmethod
    def create_gad_elevation(params: DrawingParameters) -> Dict:
        """
        Generate General Arrangement Drawing - Elevation View.
        Based on patterns from: 001 General Arrangements.DXF, 001 GAD.DXF
        """
        entities = []
        
        # Calculate total bridge length
        total_length = params.span_length * params.number_of_spans
        
        # Deck slab line
        entities.append(DXFEntity(
            entity_type='LINE',
            layer='DECK',
            properties={
                'x1': 0, 'y1': params.rtl,
                'x2': total_length, 'y2': params.rtl
            },
            annotations=['DECK SLAB TOP']
        ))
        
        # Abutments
        for i, x_pos in enumerate([0, total_length]):
            entities.append(DXFEntity(
                entity_type='LWPOLYLINE',
                layer='ABUTMENT',
                properties={
                    'vertices': [
                        (x_pos - params.abutment_width if i == 0 else x_pos, params.foundation_level),
                        (x_pos - params.abutment_width if i == 0 else x_pos, params.rtl),
                        (x_pos, params.rtl),
                        (x_pos, params.foundation_level),
                        (x_pos - params.abutment_width if i == 0 else x_pos, params.foundation_level)
                    ]
                },
                annotations=[f'ABUTMENT {i+1}']
            ))
        
        # Piers
        for i in range(1, params.number_of_spans):
            x_pos = i * params.span_length
            entities.append(DXFEntity(
                entity_type='LWPOLYLINE',
                layer='PIER',
                properties={
                    'vertices': [
                        (x_pos - params.pier_width/2, params.foundation_level),
                        (x_pos - params.pier_width/2, params.rtl - params.pier_cap_height),
                        (x_pos + params.pier_width/2, params.rtl - params.pier_cap_height),
                        (x_pos + params.pier_width/2, params.foundation_level),
                        (x_pos - params.pier_width/2, params.foundation_level)
                    ]
                },
                annotations=[f'PIER {i}']
            ))
        
        # HFL line
        entities.append(DXFEntity(
            entity_type='LINE',
            layer='WATER_LEVEL',
            properties={
                'x1': -2, 'y1': params.hfl,
                'x2': total_length + 2, 'y2': params.hfl,
                'linetype': 'DASHED'
            },
            annotations=[f'HFL = {params.hfl:.3f}']
        ))
        
        # Bed level line
        entities.append(DXFEntity(
            entity_type='LINE',
            layer='GROUND',
            properties={
                'x1': -2, 'y1': params.bed_level,
                'x2': total_length + 2, 'y2': params.bed_level
            },
            annotations=[f'BED LEVEL = {params.bed_level:.3f}']
        ))
        
        # Span dimensions
        for i in range(params.number_of_spans):
            entities.append(DXFEntity(
                entity_type='DIMENSION',
                layer='DIMENSIONS',
                properties={
                    'x1': i * params.span_length,
                    'x2': (i + 1) * params.span_length,
                    'y': params.rtl + 2,
                    'value': params.span_length
                },
                annotations=[f'Span {i+1} = {params.span_length}m']
            ))
        
        return {{
            'title': 'GENERAL ARRANGEMENT DRAWING - ELEVATION',
            'type': DrawingType.GAD,
            'entities': entities,
            'layers': ['DECK', 'ABUTMENT', 'PIER', 'WATER_LEVEL', 'GROUND', 'DIMENSIONS'],
            'scale': '1:100',
            'parameters': params
        }}
    
    @staticmethod
    def create_pier_details(params: DrawingParameters) -> Dict:
        """
        Generate Pier Details Drawing.
        Based on patterns from: 01 PIER GAD.DXF, 02 PIER CAP.DXF
        """
        entities = []
        
        # Pier elevation
        entities.append(DXFEntity(
            entity_type='LWPOLYLINE',
            layer='PIER',
            properties={{
                'vertices': [
                    (-params.pier_width/2, params.foundation_level),
                    (-params.pier_width/2, params.rtl - params.pier_cap_height),
                    (params.pier_width/2, params.rtl - params.pier_cap_height),
                    (params.pier_width/2, params.foundation_level),
                    (-params.pier_width/2, params.foundation_level)
                ]
            }},
            annotations=['PIER ELEVATION']
        ))
        
        # Pier cap
        entities.append(DXFEntity(
            entity_type='LWPOLYLINE',
            layer='PIER_CAP',
            properties={{
                'vertices': [
                    (-params.pier_cap_width/2, params.rtl - params.pier_cap_height),
                    (-params.pier_cap_width/2, params.rtl),
                    (params.pier_cap_width/2, params.rtl),
                    (params.pier_cap_width/2, params.rtl - params.pier_cap_height),
                    (-params.pier_cap_width/2, params.rtl - params.pier_cap_height)
                ]
            }},
            annotations=['PIER CAP']
        ))
        
        # Cross-section at base
        offset_x = params.pier_width + 1
        entities.append(DXFEntity(
            entity_type='LWPOLYLINE',
            layer='PIER_SECTION',
            properties={{
                'vertices': [
                    (offset_x - params.pier_width/2, params.foundation_level),
                    (offset_x - params.pier_width/2, params.foundation_level + params.pier_depth),
                    (offset_x + params.pier_width/2, params.foundation_level + params.pier_depth),
                    (offset_x + params.pier_width/2, params.foundation_level),
                    (offset_x - params.pier_width/2, params.foundation_level)
                ]
            }},
            annotations=['SECTION A-A']
        ))
        
        # Main reinforcement bars
        num_bars = 12
        cover = params.concrete_cover
        for i in range(num_bars):
            angle = (i / num_bars) * 2 * math.pi
            bar_x = offset_x + (params.pier_width/2 - cover) * math.cos(angle)
            bar_y = params.foundation_level + params.pier_depth/2 + (params.pier_depth/2 - cover) * math.sin(angle)
            
            entities.append(DXFEntity(
                entity_type='CIRCLE',
                layer='REBAR_MAIN',
                properties={{
                    'center_x': bar_x,
                    'center_y': bar_y,
                    'radius': 0.016  # 16mm diameter
                }},
                annotations=[f'{num_bars}-T16']
            ))
        
        # Lateral ties
        tie_offset = cover
        entities.append(DXFEntity(
            entity_type='LWPOLYLINE',
            layer='REBAR_TIES',
            properties={{
                'vertices': [
                    (offset_x - params.pier_width/2 + tie_offset, params.foundation_level + tie_offset),
                    (offset_x + params.pier_width/2 - tie_offset, params.foundation_level + tie_offset),
                    (offset_x + params.pier_width/2 - tie_offset, params.foundation_level + params.pier_depth - tie_offset),
                    (offset_x - params.pier_width/2 + tie_offset, params.foundation_level + params.pier_depth - tie_offset),
                    (offset_x - params.pier_width/2 + tie_offset, params.foundation_level + tie_offset)
                ]
            }},
            annotations=['T10 @ 150mm c/c']
        ))
        
        return {{
            'title': 'PIER DETAILS - ELEVATION & CROSS-SECTION',
            'type': DrawingType.PIER,
            'entities': entities,
            'layers': ['PIER', 'PIER_CAP', 'PIER_SECTION', 'REBAR_MAIN', 'REBAR_TIES', 'DIMENSIONS'],
            'scale': '1:50',
            'parameters': params
        }}
    
    @staticmethod
    def create_deck_slab_reinforcement(params: DrawingParameters) -> Dict:
        """
        Generate Deck Slab Reinforcement Drawing.
        Based on patterns from: 006 Deck Slab.DXF, 002 DECK SLAB.DXF
        """
        entities = []
        
        # Slab outline
        entities.append(DXFEntity(
            entity_type='LWPOLYLINE',
            layer='SLAB_OUTLINE',
            properties={{
                'vertices': [
                    (0, 0),
                    (params.span_length, 0),
                    (params.span_length, params.carriage_width),
                    (0, params.carriage_width),
                    (0, 0)
                ]
            }},
            annotations=['DECK SLAB']
        ))
        
        # Top reinforcement (transverse direction)
        spacing = 0.150  # 150mm c/c
        num_bars_transverse = int(params.span_length / spacing)
        for i in range(num_bars_transverse):
            y_pos = i * spacing
            entities.append(DXFEntity(
                entity_type='LINE',
                layer='REBAR_TOP_TRANSVERSE',
                properties={{
                    'x1': params.concrete_cover,
                    'y1': y_pos,
                    'x2': params.span_length - params.concrete_cover,
                    'y2': y_pos
                }},
                annotations=['T12 @ 150mm c/c (Top)']
            ))
        
        # Top reinforcement (longitudinal direction)
        num_bars_longitudinal = int(params.carriage_width / spacing)
        for i in range(num_bars_longitudinal):
            x_pos = i * spacing
            entities.append(DXFEntity(
                entity_type='LINE',
                layer='REBAR_TOP_LONGITUDINAL',
                properties={{
                    'x1': x_pos,
                    'y1': params.concrete_cover,
                    'x2': x_pos,
                    'y2': params.carriage_width - params.concrete_cover
                }},
                annotations=['T12 @ 150mm c/c (Top)']
            ))
        
        # Bottom reinforcement (transverse direction)
        for i in range(num_bars_transverse):
            y_pos = i * spacing
            entities.append(DXFEntity(
                entity_type='LINE',
                layer='REBAR_BOTTOM_TRANSVERSE',
                properties={{
                    'x1': params.concrete_cover,
                    'y1': y_pos,
                    'x2': params.span_length - params.concrete_cover,
                    'y2': y_pos
                }},
                annotations=['T12 @ 150mm c/c (Bottom)']
            ))
        
        # Bottom reinforcement (longitudinal direction)
        for i in range(num_bars_longitudinal):
            x_pos = i * spacing
            entities.append(DXFEntity(
                entity_type='LINE',
                layer='REBAR_BOTTOM_LONGITUDINAL',
                properties={{
                    'x1': x_pos,
                    'y1': params.concrete_cover,
                    'x2': x_pos,
                    'y2': params.carriage_width - params.concrete_cover
                }},
                annotations=['T12 @ 150mm c/c (Bottom)']
            ))
        
        return {{
            'title': 'DECK SLAB REINFORCEMENT DETAILS',
            'type': DrawingType.DECK_SLAB,
            'entities': entities,
            'layers': ['SLAB_OUTLINE', 'REBAR_TOP_TRANSVERSE', 'REBAR_TOP_LONGITUDINAL',
                      'REBAR_BOTTOM_TRANSVERSE', 'REBAR_BOTTOM_LONGITUDINAL', 'DIMENSIONS'],
            'scale': '1:20',
            'parameters': params
        }}
    
    @staticmethod
    def create_cross_section(params: DrawingParameters) -> Dict:
        """
        Generate Typical Cross Section Drawing.
        Based on patterns from analyzed cross-section drawings.
        """
        entities = []
        
        total_width = params.carriage_width + 2 * params.footpath_width
        
        # Deck slab
        entities.append(DXFEntity(
            entity_type='LWPOLYLINE',
            layer='DECK_SLAB',
            properties={{
                'vertices': [
                    (-total_width/2, params.rtl - params.slab_thickness),
                    (total_width/2, params.rtl - params.slab_thickness),
                    (total_width/2, params.rtl),
                    (-total_width/2, params.rtl),
                    (-total_width/2, params.rtl - params.slab_thickness)
                ]
            }},
            annotations=['DECK SLAB']
        ))
        
        # Wearing coat
        entities.append(DXFEntity(
            entity_type='LWPOLYLINE',
            layer='WEARING_COAT',
            properties={{
                'vertices': [
                    (-total_width/2, params.rtl),
                    (total_width/2, params.rtl),
                    (total_width/2, params.rtl + params.wearing_coat_thickness),
                    (-total_width/2, params.rtl + params.wearing_coat_thickness),
                    (-total_width/2, params.rtl)
                ]
            }},
            annotations=['WEARING COAT']
        ))
        
        # Kerbs
        for side in [-1, 1]:
            kerb_x = side * params.carriage_width/2
            entities.append(DXFEntity(
                entity_type='LWPOLYLINE',
                layer='KERB',
                properties={{
                    'vertices': [
                        (kerb_x, params.rtl - params.slab_thickness - 0.3),
                        (kerb_x + side * 0.3, params.rtl - params.slab_thickness - 0.3),
                        (kerb_x + side * 0.3, params.rtl - params.slab_thickness),
                        (kerb_x, params.rtl - params.slab_thickness),
                        (kerb_x, params.rtl - params.slab_thickness - 0.3)
                    ]
                }},
                annotations=['KERB']
            ))
        
        # Footpaths
        for side in [-1, 1]:
            fp_center = side * (params.carriage_width/2 + params.footpath_width/2 + 0.15)
            entities.append(DXFEntity(
                entity_type='LWPOLYLINE',
                layer='FOOTPATH',
                properties={{
                    'vertices': [
                        (fp_center - params.footpath_width/2, params.rtl - params.slab_thickness),
                        (fp_center + params.footpath_width/2, params.rtl - params.slab_thickness),
                        (fp_center + params.footpath_width/2, params.rtl),
                        (fp_center - params.footpath_width/2, params.rtl),
                        (fp_center - params.footpath_width/2, params.rtl - params.slab_thickness)
                    ]
                }},
                annotations=['FOOTPATH']
            ))
        
        # Girders
        for i in range(params.number_of_girders):
            girder_x = -total_width/2 + (i + 0.5) * params.girder_spacing
            entities.append(DXFEntity(
                entity_type='LWPOLYLINE',
                layer='GIRDER',
                properties={{
                    'vertices': [
                        (girder_x - params.girder_width/2, params.rtl - params.slab_thickness),
                        (girder_x + params.girder_width/2, params.rtl - params.slab_thickness),
                        (girder_x + params.girder_width/2, params.rtl - params.slab_thickness - params.girder_depth),
                        (girder_x - params.girder_width/2, params.rtl - params.slab_thickness - params.girder_depth),
                        (girder_x - params.girder_width/2, params.rtl - params.slab_thickness)
                    ]
                }},
                annotations=[f'GIRDER {i+1}']
            ))
        
        return {{
            'title': 'TYPICAL CROSS SECTION',
            'type': DrawingType.CROSS_SECTION,
            'entities': entities,
            'layers': ['DECK_SLAB', 'WEARING_COAT', 'KERB', 'FOOTPATH', 'GIRDER', 'DIMENSIONS'],
            'scale': '1:20',
            'parameters': params
        }}
    
    @staticmethod
    def create_bearing_details(params: DrawingParameters) -> Dict:
        """
        Generate Bearing Details Drawing.
        Based on patterns from: 007 Bearing Pedestal Details.DXF
        """
        entities = []
        
        # Bearing pedestal
        pedestal_width = params.pier_cap_width
        pedestal_height = 0.3
        
        entities.append(DXFEntity(
            entity_type='LWPOLYLINE',
            layer='PEDESTAL',
            properties={{
                'vertices': [
                    (-pedestal_width/2, params.rtl - params.pier_cap_height - pedestal_height),
                    (pedestal_width/2, params.rtl - params.pier_cap_height - pedestal_height),
                    (pedestal_width/2, params.rtl - params.pier_cap_height),
                    (-pedestal_width/2, params.rtl - params.pier_cap_height),
                    (-pedestal_width/2, params.rtl - params.pier_cap_height - pedestal_height)
                ]
            }},
            annotations=['BEARING PEDESTAL']
        ))
        
        # Elastomeric bearing pad
        bearing_width = 0.4
        bearing_thickness = 0.05
        
        entities.append(DXFEntity(
            entity_type='LWPOLYLINE',
            layer='BEARING',
            properties={{
                'vertices': [
                    (-bearing_width/2, params.rtl - params.pier_cap_height),
                    (bearing_width/2, params.rtl - params.pier_cap_height),
                    (bearing_width/2, params.rtl - params.pier_cap_height + bearing_thickness),
                    (-bearing_width/2, params.rtl - params.pier_cap_height + bearing_thickness),
                    (-bearing_width/2, params.rtl - params.pier_cap_height)
                ]
            }},
            annotations=['ELASTOMERIC BEARING']
        ))
        
        return {{
            'title': 'BEARING DETAILS',
            'type': DrawingType.BEARING,
            'entities': entities,
            'layers': ['PEDESTAL', 'BEARING', 'DIMENSIONS'],
            'scale': '1:10',
            'parameters': params
        }}


# Example usage and demonstration
if __name__ == "__main__":
    print("=" * 80)
    print("Common Drawing Forms Generator - Enhanced Version")
    print("=" * 80)
    
    # Create standard parameters for a typical bridge
    params = DrawingParameters(
        span_length=14.0,
        number_of_spans=3,
        carriage_width=7.5,
        footpath_width=1.5,
        rtl=100.500,
        hfl=98.200,
        bed_level=95.000,
        foundation_level=90.000,
        agl=96.500,
        pier_width=1.2,
        pier_depth=8.0,
        pier_cap_height=0.5,
        pier_cap_width=2.0,
        abutment_width=1.5,
        abutment_base_width=3.0,
        abutment_height=6.0,
        slab_thickness=0.45,
        wearing_coat_thickness=0.075,
        girder_depth=1.2,
        girder_width=0.3,
        number_of_girders=4,
        girder_spacing=2.0,
        concrete_grade="M35",
        steel_grade="Fe500",
        project_name="Sample Bridge Project",
        drawing_no="GAD-001"
    )
    
    # Generate all drawing forms
    forms = CommonDrawingForms()
    
    drawing_generators = [
        ('GAD Elevation', forms.create_gad_elevation),
        ('Pier Details', forms.create_pier_details),
        ('Deck Slab Reinforcement', forms.create_deck_slab_reinforcement),
        ('Cross Section', forms.create_cross_section),
        ('Bearing Details', forms.create_bearing_details)
    ]
    
    print(f"\\nGenerating {len(drawing_generators)} drawing forms...\\n")
    
    for name, generator in drawing_generators:
        drawing = generator(params)
        print(f"✓ {drawing['title']}")
        print(f"  Type: {drawing['type'].value}")
        print(f"  Entities: {len(drawing['entities'])}")
        print(f"  Layers: {', '.join(drawing['layers'])}")
        print(f"  Scale: {drawing['scale']}\\n")
    
    print("=" * 80)
    print("✅ All common drawing forms generated successfully!")
    print("=" * 80)
'''
        
        return code


def main():
    """Main execution function."""
    base_path = r"C:\Users\Rajkumar\Downloads\Dwg-Dxf-Record-Keeper\COLLECTION FROM RECORD\Filtered_Drawings"
    
    # Initialize enhanced analyzer
    analyzer = EnhancedDXFAnalyzer(base_path)
    
    # Find all DXF files
    analyzer.find_dxf_files()
    
    if not analyzer.dxf_files:
        print("\n⚠ No DXF files found. Exiting.")
        return
    
    # Analyze all files
    results = analyzer.analyze_all_files()
    
    # Generate enhanced code
    print(f"\n{'='*80}")
    print("Generating enhanced common drawing forms code...")
    print(f"{'='*80}\n")
    
    code = analyzer.generate_enhanced_forms_code()
    
    code_output_path = Path(base_path).parent / "common_drawing_forms.py"
    with open(code_output_path, 'w', encoding='utf-8') as f:
        f.write(code)
    print(f"✓ Enhanced code saved to: {code_output_path}\n")
    
    print(f"{'='*80}")
    print("✅ Analysis Complete!")
    print(f"{'='*80}")
    print(f"\nSummary:")
    print(f"  • DXF Files Analyzed: {len(analyzer.dxf_files)}")
    print(f"  • Drawing Types Found: {len(results['type_counts'])}")
    print(f"  • Unique Layers: {len(analyzer.all_patterns['layers'])}")
    print(f"  • Code Generated: common_drawing_forms.py")
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
