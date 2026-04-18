"""
DXF Drawing Pattern Analyzer
Analyzes DXF files from the Filtered_Drawings collection to identify common drawing forms
and derive reusable code templates for bridge engineering drawings.

Author: AI Assistant for Rajkumar Singh Chauhan
Date: 2026-04-18
"""

import os
import re
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set
import json


class DXFPatternAnalyzer:
    """Analyzes DXF files to identify common patterns and drawing forms."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.dxf_files = []
        self.patterns = {
            'layers': Counter(),
            'entities': Counter(),
            'text_patterns': [],
            'dimension_patterns': [],
            'common_blocks': [],
            'drawing_types': defaultdict(list)
        }
        
    def find_dxf_files(self) -> List[Path]:
        """Find all DXF files in the directory tree."""
        print(f"Scanning for DXF files in: {self.base_path}")
        self.dxf_files = list(self.base_path.rglob('*.dxf'))
        print(f"Found {len(self.dxf_files)} DXF files")
        return self.dxf_files
    
    def analyze_dxf_file(self, file_path: Path) -> Dict:
        """Analyze a single DXF file for patterns."""
        analysis = {
            'file': str(file_path),
            'layers': set(),
            'entity_types': Counter(),
            'text_content': [],
            'dimensions': [],
            'estimated_type': 'unknown'
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # Parse layers
            for i, line in enumerate(lines):
                if line.strip() == '8' and i + 1 < len(lines):
                    layer_name = lines[i + 1].strip()
                    if layer_name and not layer_name.isdigit():
                        analysis['layers'].add(layer_name)
                
                # Count entity types
                if line.strip() == '0' and i + 1 < len(lines):
                    entity_type = lines[i + 1].strip()
                    if entity_type in ['LINE', 'CIRCLE', 'ARC', 'TEXT', 'LWPOLYLINE', 
                                     'POLYLINE', 'DIMENSION', 'INSERT', 'POINT', 'SOLID',
                                     'HATCH', 'SPLINE', 'ELLIPSE', '3DFACE', 'MTEXT']:
                        analysis['entity_types'][entity_type] += 1
                
                # Extract text content
                if line.strip() == '1' and i + 1 < len(lines):
                    text_content = lines[i + 1].strip()
                    if text_content and len(text_content) > 2:
                        analysis['text_content'].append(text_content)
                
                # Look for dimension-related patterns
                if 'DIM' in line.upper():
                    analysis['dimensions'].append(line.strip())
            
            # Estimate drawing type based on content
            analysis['estimated_type'] = self.classify_drawing_type(analysis)
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
        return analysis
    
    def classify_drawing_type(self, analysis: Dict) -> str:
        """Classify the drawing type based on its content."""
        text_lower = ' '.join(analysis['text_content']).lower()
        layers_lower = ' '.join(analysis['layers']).lower()
        combined = text_lower + ' ' + layers_lower
        
        # Classification rules
        if any(kw in combined for kw in ['general arrangement', 'gad', 'elevation']):
            return 'GAD'
        elif any(kw in combined for kw in ['pier', 'column', 'shaft']):
            return 'PIER'
        elif any(kw in combined for kw in ['abutment', 'end support']):
            return 'ABUTMENT'
        elif any(kw in combined for kw in ['reinforcement', 'rebar', 'bar bending']):
            return 'REINFORCEMENT'
        elif any(kw in combined for kw in ['cross section', 'x-section', 'section']):
            return 'CROSS_SECTION'
        elif any(kw in combined for kw in ['plan', 'footing', 'foundation']):
            return 'PLAN'
        elif any(kw in combined for kw in ['longitudinal', 'profile']):
            return 'LONGITUDINAL'
        elif any(kw in combined for kw in ['deck slab', 'slab reinforcement']):
            return 'DECK_SLAB'
        elif any(kw in combined for kw in ['wing wall', 'return wall']):
            return 'WING_WALL'
        elif any(kw in combined for kw in ['bearing', 'elastomeric']):
            return 'BEARING'
        elif any(kw in combined for kw in ['expansion joint', 'joint']):
            return 'EXPANSION_JOINT'
        else:
            return 'OTHER'
    
    def analyze_all_files(self) -> Dict:
        """Analyze all DXF files and aggregate patterns."""
        print("\nAnalyzing DXF files...")
        all_analyses = []
        type_counts = Counter()
        
        for i, dxf_file in enumerate(self.dxf_files[:50]):  # Limit to first 50 for performance
            if i % 10 == 0:
                print(f"Processing {i+1}/{min(50, len(self.dxf_files))} files...")
            
            analysis = self.analyze_dxf_file(dxf_file)
            all_analyses.append(analysis)
            
            # Aggregate patterns
            self.patterns['layers'].update(analysis['layers'])
            self.patterns['entities'].update(analysis['entity_types'])
            self.patterns['text_patterns'].extend(analysis['text_content'][:10])
            
            # Track drawing types
            drawing_type = analysis['estimated_type']
            type_counts[drawing_type] += 1
            self.patterns['drawing_types'][drawing_type].append(dxf_file)
        
        print(f"\nDrawing Type Distribution:")
        for dtype, count in type_counts.most_common():
            print(f"  {dtype}: {count} files")
        
        return {
            'analyses': all_analyses,
            'type_counts': type_counts,
            'patterns': self.patterns
        }
    
    def generate_common_forms_code(self) -> str:
        """Generate Python code templates for common drawing forms."""
        code = '''"""
Common Drawing Forms Generator
Auto-generated from analysis of DXF drawing collection.
Contains templates for standard bridge engineering drawings.

Author: Auto-generated by DXF Pattern Analyzer
Date: 2026-04-18
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class DrawingParameters:
    """Standard parameters for bridge drawings."""
    # Bridge geometry
    span_length: float
    number_of_spans: int
    carriage_width: float
    footpath_width: float
    
    # Levels
    rtl: float  # Road Top Level
    hfl: float  # High Flood Level
    bed_level: float
    foundation_level: float
    agl: float  # Average Ground Level
    
    # Pier parameters
    pier_width: float
    pier_depth: float
    pier_cap_height: float
    pier_cap_width: float
    
    # Abutment parameters
    abutment_width: float
    abutment_base_width: float
    abutment_height: float
    
    # Slab parameters
    slab_thickness: float
    wearing_coat_thickness: float
    
    # Materials
    concrete_grade: str = "M35"
    steel_grade: str = "Fe500"
    
    # Project info
    project_name: str = ""
    drawing_no: str = ""


class CommonDrawingForms:
    """Templates for common bridge drawing forms."""
    
    @staticmethod
    def create_gad_elevation(params: DrawingParameters) -> Dict:
        """
        Generate General Arrangement Drawing - Elevation View.
        Common elements: spans, piers, abutments, water level, dimensions.
        """
        entities = []
        
        # Deck slab
        deck_start = 0
        deck_end = params.span_length * params.number_of_spans
        
        # Abutments
        abutment_left = {
            'type': 'RECTANGLE',
            'x': -params.abutment_width,
            'y': params.foundation_level,
            'width': params.abutment_width,
            'height': params.abutment_height,
            'layer': 'ABUTMENTS'
        }
        entities.append(abutment_left)
        
        # Spans
        for i in range(params.number_of_spans):
            span = {
                'type': 'LINE',
                'x1': i * params.span_length,
                'y1': params.rtl,
                'x2': (i + 1) * params.span_length,
                'y2': params.rtl,
                'layer': 'DECK'
            }
            entities.append(span)
        
        # Piers
        for i in range(1, params.number_of_spans):
            pier = {
                'type': 'RECTANGLE',
                'x': i * params.span_length - params.pier_width/2,
                'y': params.foundation_level,
                'width': params.pier_width,
                'height': params.pier_depth,
                'layer': 'PIERS'
            }
            entities.append(pier)
        
        # Abutment right
        abutment_right = {
            'type': 'RECTANGLE',
            'x': deck_end,
            'y': params.foundation_level,
            'width': params.abutment_width,
            'height': params.abutment_height,
            'layer': 'ABUTMENTS'
        }
        entities.append(abutment_right)
        
        # Water level (HFL)
        hfl_line = {
            'type': 'DASHED_LINE',
            'x1': -params.abutment_width - 2,
            'y1': params.hfl,
            'x2': deck_end + params.abutment_width + 2,
            'y2': params.hfl,
            'layer': 'WATER_LEVEL',
            'label': f'HFL {params.hfl:.2f}m'
        }
        entities.append(hfl_line)
        
        # Bed level
        bed_line = {
            'type': 'LINE',
            'x1': -params.abutment_width - 2,
            'y1': params.bed_level,
            'x2': deck_end + params.abutment_width + 2,
            'y2': params.bed_level,
            'layer': 'GROUND',
            'label': f'BED {params.bed_level:.2f}m'
        }
        entities.append(bed_line)
        
        return {
            'title': 'GENERAL ARRANGEMENT DRAWING - ELEVATION',
            'entities': entities,
            'layers': ['ABUTMENTS', 'PIERS', 'DECK', 'WATER_LEVEL', 'GROUND', 'DIMENSIONS'],
            'scale': '1:100'
        }
    
    @staticmethod
    def create_pier_details(params: DrawingParameters) -> Dict:
        """
        Generate Pier Details Drawing.
        Common elements: elevation, cross-section, reinforcement, dimensions.
        """
        entities = []
        
        # Pier elevation
        pier_elevation = {
            'type': 'RECTANGLE',
            'x': -params.pier_width/2,
            'y': params.foundation_level,
            'width': params.pier_width,
            'height': params.pier_depth,
            'layer': 'PIERS'
        }
        entities.append(pier_elevation)
        
        # Pier cap
        pier_cap = {
            'type': 'RECTANGLE',
            'x': -params.pier_cap_width/2,
            'y': params.rtl - params.pier_cap_height,
            'width': params.pier_cap_width,
            'height': params.pier_cap_height,
            'layer': 'PIERS'
        }
        entities.append(pier_cap)
        
        # Cross-section A-A
        cross_section = {
            'type': 'RECTANGLE',
            'x': params.pier_width + 2,
            'y': params.foundation_level,
            'width': params.pier_width,
            'height': params.pier_depth,
            'layer': 'PIERS',
            'section_label': 'A-A'
        }
        entities.append(cross_section)
        
        # Main reinforcement bars
        num_bars = 8
        for i in range(num_bars):
            angle = (i / num_bars) * 360
            bar = {
                'type': 'CIRCLE',
                'center_x': params.pier_width + 2,
                'center_y': params.foundation_level + params.pier_depth/2,
                'radius': 0.016,  # 16mm bar
                'layer': 'REBAR',
                'label': f'{num_bars}-T16'
            }
            entities.append(bar)
        
        return {
            'title': 'PIER DETAILS - ELEVATION & CROSS-SECTION',
            'entities': entities,
            'layers': ['PIERS', 'REBAR', 'DIMENSIONS', 'ANNOTATIONS'],
            'scale': '1:50'
        }
    
    @staticmethod
    def create_abutment_details(params: DrawingParameters) -> Dict:
        """
        Generate Abutment Details Drawing.
        Common elements: elevation, plan, wing walls, reinforcement.
        """
        entities = []
        
        # Abutment stem
        stem = {
            'type': 'RECTANGLE',
            'x': 0,
            'y': params.foundation_level,
            'width': params.abutment_width,
            'height': params.abutment_height,
            'layer': 'ABUTMENTS'
        }
        entities.append(stem)
        
        # Base slab
        base = {
            'type': 'RECTANGLE',
            'x': -0.5,
            'y': params.foundation_level - 0.3,
            'width': params.abutment_base_width + 0.5,
            'height': 0.3,
            'layer': 'ABUTMENTS'
        }
        entities.append(base)
        
        # Wing walls
        wing_wall_left = {
            'type': 'POLYLINE',
            'points': [
                (0, params.foundation_level),
                (-2, params.foundation_level - 1),
                (-2, params.foundation_level - 2),
                (0, params.foundation_level - 1.5)
            ],
            'layer': 'ABUTMENTS',
            'label': 'WING WALL'
        }
        entities.append(wing_wall_left)
        
        # Dirt wall
        dirt_wall = {
            'type': 'RECTANGLE',
            'x': params.abutment_width,
            'y': params.rtl - 0.5,
            'width': 0.3,
            'height': 0.5,
            'layer': 'ABUTMENTS'
        }
        entities.append(dirt_wall)
        
        return {
            'title': 'ABUTMENT DETAILS - ELEVATION & PLAN',
            'entities': entities,
            'layers': ['ABUTMENTS', 'REBAR', 'DIMENSIONS', 'ANNOTATIONS'],
            'scale': '1:50'
        }
    
    @staticmethod
    def create_deck_slab_reinforcement(params: DrawingParameters) -> Dict:
        """
        Generate Deck Slab Reinforcement Drawing.
        Common elements: top/bottom mesh, extra bars, dimensions.
        """
        entities = []
        
        # Slab outline
        slab = {
            'type': 'RECTANGLE',
            'x': 0,
            'y': 0,
            'width': params.carriage_width,
            'height': params.span_length,
            'layer': 'DECK'
        }
        entities.append(slab)
        
        # Top reinforcement (transverse)
        for i in range(int(params.span_length / 0.15)):
            bar = {
                'type': 'LINE',
                'x1': 0.05,
                'y1': i * 0.15,
                'x2': params.carriage_width - 0.05,
                'y2': i * 0.15,
                'layer': 'REBAR_TOP',
                'label': 'T12 @ 150mm c/c'
            }
            entities.append(bar)
        
        # Bottom reinforcement (longitudinal)
        for i in range(int(params.carriage_width / 0.15)):
            bar = {
                'type': 'LINE',
                'x1': i * 0.15,
                'y1': 0.05,
                'x2': i * 0.15,
                'y2': params.span_length - 0.05,
                'layer': 'REBAR_BOTTOM',
                'label': 'T12 @ 150mm c/c'
            }
            entities.append(bar)
        
        return {
            'title': 'DECK SLAB REINFORCEMENT DETAILS',
            'entities': entities,
            'layers': ['DECK', 'REBAR_TOP', 'REBAR_BOTTOM', 'DIMENSIONS'],
            'scale': '1:20'
        }
    
    @staticmethod
    def create_cross_section(params: DrawingParameters) -> Dict:
        """
        Generate Typical Cross Section Drawing.
        Common elements: carriageway, footpath, kerb, slab, girders.
        """
        entities = []
        
        total_width = params.carriage_width + 2 * params.footpath_width
        
        # Deck slab
        deck = {
            'type': 'RECTANGLE',
            'x': -total_width/2,
            'y': params.rtl - params.slab_thickness,
            'width': total_width,
            'height': params.slab_thickness,
            'layer': 'DECK'
        }
        entities.append(deck)
        
        # Wearing coat
        wearing = {
            'type': 'RECTANGLE',
            'x': -total_width/2,
            'y': params.rtl,
            'width': total_width,
            'height': params.wearing_coat_thickness,
            'layer': 'WEARING_COAT'
        }
        entities.append(wearing)
        
        # Kerbs
        for side in [-1, 1]:
            kerb = {
                'type': 'RECTANGLE',
                'x': side * (params.carriage_width/2),
                'y': params.rtl - params.slab_thickness - 0.3,
                'width': 0.3,
                'height': 0.3,
                'layer': 'KERB'
            }
            entities.append(kerb)
        
        # Footpaths
        for side in [-1, 1]:
            footpath = {
                'type': 'RECTANGLE',
                'x': side * (params.carriage_width/2 + params.footpath_width/2 + 0.15),
                'y': params.rtl - params.slab_thickness,
                'width': params.footpath_width,
                'height': params.slab_thickness,
                'layer': 'FOOTPATH'
            }
            entities.append(footpath)
        
        return {
            'title': 'TYPICAL CROSS SECTION',
            'entities': entities,
            'layers': ['DECK', 'WEARING_COAT', 'KERB', 'FOOTPATH', 'DIMENSIONS'],
            'scale': '1:20'
        }


# Example usage
if __name__ == "__main__":
    # Create standard parameters
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
        project_name="Sample Bridge Project",
        drawing_no="GAD-001"
    )
    
    # Generate drawings
    forms = CommonDrawingForms()
    
    gad = forms.create_gad_elevation(params)
    print(f"Generated: {gad['title']}")
    print(f"  Entities: {len(gad['entities'])}")
    print(f"  Layers: {', '.join(gad['layers'])}")
    print(f"  Scale: {gad['scale']}\\n")
    
    pier = forms.create_pier_details(params)
    print(f"Generated: {pier['title']}")
    print(f"  Entities: {len(pier['entities'])}")
    print(f"  Layers: {', '.join(pier['layers'])}")
    print(f"  Scale: {pier['scale']}\\n")
    
    abutment = forms.create_abutment_details(params)
    print(f"Generated: {abutment['title']}")
    print(f"  Entities: {len(abutment['entities'])}")
    print(f"  Layers: {', '.join(abutment['layers'])}")
    print(f"  Scale: {abutment['scale']}\\n")
    
    print("✅ Common drawing forms generated successfully!")
'''
        return code
    
    def generate_analysis_report(self, results: Dict) -> str:
        """Generate a comprehensive analysis report."""
        report = f"""
# DXF Drawing Collection Analysis Report
Generated: 2026-04-18

## Summary
- Total DXF Files Analyzed: {len(results['analyses'])}
- Drawing Types Identified: {len(results['type_counts'])}

## Drawing Type Distribution
"""
        for dtype, count in results['type_counts'].most_common():
            report += f"- **{dtype}**: {count} files\n"
        
        report += f"""

## Common Layers Found
"""
        for layer, count in self.patterns['layers'].most_common(20):
            report += f"- {layer}: {count} occurrences\n"
        
        report += f"""

## Common Entity Types
"""
        for entity, count in self.patterns['entities'].most_common(10):
            report += f"- {entity}: {count:,} instances\n"
        
        report += f"""

## Drawing Files by Type
"""
        for dtype, files in self.patterns['drawing_types'].items():
            report += f"\n### {dtype} ({len(files)} files)\n"
            for f in files[:5]:  # Show first 5 files
                report += f"- {f.name}\n"
        
        report += f"""

## Recommendations
Based on the analysis, the following common drawing forms have been identified:

1. **General Arrangement Drawing (GAD)** - Overall bridge layout with spans, piers, abutments
2. **Pier Details** - Pier elevation, cross-section, reinforcement details
3. **Abutment Details** - Abutment elevation, plan, wing walls, reinforcement
4. **Deck Slab Reinforcement** - Top and bottom reinforcement mesh
5. **Cross Section** - Typical cross-section showing carriageway, footpath, kerb
6. **Longitudinal Section** - Profile view along bridge centerline
7. **Plan View** - Top-down view of bridge components
8. **Wing Wall Details** - Wing wall elevation and plan
9. **Bearing Details** - Bearing pad and pedestal details
10. **Expansion Joint Details** - Joint types and installation details

These forms can be parameterized and automated using the generated code templates.

## Next Steps
1. Review the generated `common_drawing_forms.py` file
2. Customize parameters for specific bridge projects
3. Integrate with DXF generation library (ezdxf or custom)
4. Add more drawing types as needed
5. Create a UI for parameter input and drawing generation
"""
        return report


def main():
    """Main execution function."""
    base_path = r"C:\Users\Rajkumar\Downloads\Dwg-Dxf-Record-Keeper\COLLECTION FROM RECORD\Filtered_Drawings"
    
    print("=" * 80)
    print("DXF Drawing Pattern Analyzer")
    print("=" * 80)
    
    # Initialize analyzer
    analyzer = DXFPatternAnalyzer(base_path)
    
    # Find DXF files
    analyzer.find_dxf_files()
    
    if not analyzer.dxf_files:
        print("No DXF files found. Exiting.")
        return
    
    # Analyze files
    results = analyzer.analyze_all_files()
    
    # Generate code
    print("\nGenerating common drawing forms code...")
    code = analyzer.generate_common_forms_code()
    
    code_output_path = Path(base_path).parent / "common_drawing_forms.py"
    with open(code_output_path, 'w') as f:
        f.write(code)
    print(f"✅ Code saved to: {code_output_path}")
    
    # Generate report
    print("\nGenerating analysis report...")
    report = analyzer.generate_analysis_report(results)
    
    report_output_path = Path(base_path).parent / "dxf_analysis_report.md"
    with open(report_output_path, 'w') as f:
        f.write(report)
    print(f"✅ Report saved to: {report_output_path}")
    
    print("\n" + "=" * 80)
    print("Analysis Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
