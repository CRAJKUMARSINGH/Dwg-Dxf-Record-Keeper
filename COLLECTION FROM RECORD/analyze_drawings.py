"""
Enhanced Drawing Collection Analyzer
Analyzes DWG/DXF file names and structure to identify common drawing forms
from the Filtered_Drawings collection.

Author: AI Assistant for Rajkumar Singh Chauhan
Date: 2026-04-18
"""

import os
from pathlib import Path
from collections import Counter, defaultdict
import re


class DrawingCollectionAnalyzer:
    """Analyzes drawing collection to identify common forms."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.drawings = []
        self.categories = defaultdict(list)
        
    def scan_drawings(self):
        """Scan for all DWG and DXF files."""
        print(f"Scanning: {self.base_path}")
        
        # Find all drawing files
        patterns = ['*.dwg', '*.dxf']
        for pattern in patterns:
            self.drawings.extend(list(self.base_path.rglob(pattern)))
        
        print(f"Found {len(self.drawings)} drawing files\n")
        return self.drawings
    
    def categorize_by_name(self):
        """Categorize drawings based on filename patterns."""
        print("Categorizing drawings by name patterns...\n")
        
        for drawing in self.drawings:
            name = drawing.stem.upper()
            filename = drawing.name.upper()
            
            # Categorization rules based on common bridge drawing terminology
            if any(kw in name for kw in ['GAD', 'GENERAL ARRANGEMENT', 'SUBMERSIBLE']):
                category = 'GAD_GENERAL_ARRANGEMENT'
            elif any(kw in name for kw in ['PIER', 'COLUMN', 'SHAFT']):
                if any(kw in name for kw in ['REINFORCEMENT', 'REINF', 'BAR']):
                    category = 'PIER_REINFORCEMENT'
                elif any(kw in name for kw in ['SECTION', 'GEOMETRY', 'DIMENSION']):
                    category = 'PIER_GEOMETRY'
                else:
                    category = 'PIER_GENERAL'
            elif any(kw in name for kw in ['ABUTMENT', 'END_SUPPORT']):
                if any(kw in name for kw in ['REINFORCEMENT', 'REINF', 'BAR']):
                    category = 'ABUTMENT_REINFORCEMENT'
                else:
                    category = 'ABUTMENT_GENERAL'
            elif any(kw in name for kw in ['WING WALL', 'RETURN WALL']):
                category = 'WING_WALL'
            elif any(kw in name for kw in ['BED PROTECTION', 'BED ANCHORAGE']):
                category = 'BED_PROTECTION'
            elif any(kw in name for kw in ['DECK SLAB', 'SLAB ANCHORAGE']):
                category = 'DECK_SLAB_DETAILS'
            elif any(kw in name for kw in ['GUARD STONE', 'KERB']):
                category = 'GUARD_STONE_KERB'
            elif any(kw in name for kw in ['FOOTBRIDGE', 'FOOT BRIDGE']):
                category = 'FOOTBRIDGE'
            elif any(kw in name for kw in ['FALSE WORK', 'FORMWORK']):
                category = 'FALSE_WORK'
            elif any(kw in name for kw in ['EXPANSION JOINT', 'ENDJOINT']):
                category = 'EXPANSION_JOINT'
            elif any(kw in name for kw in ['FOUNDATION', 'FOOTING', 'PILE']):
                category = 'FOUNDATION'
            elif any(kw in name for kw in ['BEARING', 'PEDESTAL']):
                category = 'BEARING_DETAILS'
            elif any(kw in name for kw in ['CROSS SECTION', 'X-SECTION']):
                category = 'CROSS_SECTION'
            elif any(kw in name for kw in ['LONGITUDINAL', 'PROFILE']):
                category = 'LONGITUDINAL_SECTION'
            elif any(kw in name for kw in ['PLAN', 'LAYOUT']):
                category = 'PLAN_LAYOUT'
            elif any(kw in name for kw in ['CULVERT']):
                category = 'CULVERT'
            elif any(kw in name for kw in ['NOTE', 'SPECIFICATION']):
                category = 'NOTES_SPECS'
            else:
                category = 'OTHER'
            
            self.categories[category].append(drawing)
        
        # Print distribution
        print("Drawing Distribution by Category:")
        print("=" * 70)
        for category in sorted(self.categories.keys()):
            count = len(self.categories[category])
            print(f"{category:40s}: {count:3d} files")
        print("=" * 70)
        print(f"{'TOTAL':40s}: {len(self.drawings):3d} files\n")
        
        return self.categories
    
    def analyze_common_patterns(self):
        """Analyze common patterns in drawing names."""
        print("Analyzing common patterns...\n")
        
        # Extract common terms
        all_names = [d.stem.upper() for d in self.drawings]
        text_content = ' '.join(all_names)
        
        # Find common bridge-related terms
        common_terms = [
            'PIER', 'ABUTMENT', 'GAD', 'REINFORCEMENT', 'SECTION',
            'BED', 'SLAB', 'WING', 'WALL', 'BRIDGE', 'DECK',
            'GUARD', 'STONE', 'FOUNDATION', 'BEARING', 'JOINT',
            'CULVERT', 'FOOTBRIDGE', 'SKEW', 'SUBMERSIBLE'
        ]
        
        term_counts = Counter()
        for term in common_terms:
            count = text_content.count(term)
            if count > 0:
                term_counts[term] = count
        
        print("Common Terms Found:")
        for term, count in term_counts.most_common():
            print(f"  {term:20s}: {count:4d} occurrences")
        print()
        
        return term_counts
    
    def show_category_examples(self, category: str, max_examples: int = 5):
        """Show example files for a category."""
        if category in self.categories:
            print(f"\n{category} Examples:")
            for drawing in self.categories[category][:max_examples]:
                rel_path = drawing.relative_to(self.base_path)
                print(f"  - {rel_path}")
    
    def generate_summary_report(self):
        """Generate a comprehensive summary report."""
        report = []
        report.append("=" * 80)
        report.append("DRAWING COLLECTION ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"\nBase Path: {self.base_path}")
        report.append(f"Total Drawings: {len(self.drawings)}")
        report.append(f"\nCategories Identified: {len(self.categories)}")
        
        report.append("\n" + "=" * 80)
        report.append("CATEGORY DISTRIBUTION")
        report.append("=" * 80)
        
        for category in sorted(self.categories.keys()):
            count = len(self.categories[category])
            report.append(f"\n{category}: {count} files")
            report.append("-" * 60)
            
            # Show first 3 examples
            for drawing in self.categories[category][:3]:
                rel_path = drawing.relative_to(self.base_path)
                report.append(f"  • {rel_path}")
            
            if count > 3:
                report.append(f"  ... and {count - 3} more files")
        
        report.append("\n" + "=" * 80)
        report.append("COMMON DRAWING FORMS IDENTIFIED")
        report.append("=" * 80)
        
        forms = [
            ("General Arrangement Drawing (GAD)", "Overall bridge layout, elevation, spans"),
            ("Pier Geometry & Dimensions", "Pier cross-sections, dimensions, geometry"),
            ("Pier Reinforcement Details", "Rebar layouts, bar bending schedules"),
            ("Abutment Details", "Abutment elevation, plan, reinforcement"),
            ("Wing Wall Details", "Wing wall elevation, plan, reinforcement"),
            ("Bed Protection & Anchorage", "Bed protection details, anchorage"),
            ("Deck Slab Details", "Slab reinforcement, anchorage details"),
            ("Guard Stone & Kerb Details", "Guard stone, kerb, railing details"),
            ("Cross Sections", "Typical cross-sections of bridge"),
            ("Expansion Joint Details", "Joint types, installation details"),
            ("Bearing Details", "Bearing pads, pedestals"),
            ("Foundation Details", "Footing, pile foundations"),
            ("False Work/Formwork", "Temporary support structures"),
            ("Notes & Specifications", "General notes, specifications"),
        ]
        
        for i, (form, description) in enumerate(forms, 1):
            report.append(f"\n{i}. {form}")
            report.append(f"   {description}")
        
        report.append("\n" + "=" * 80)
        report.append("RECOMMENDATIONS")
        report.append("=" * 80)
        report.append("""
Based on this analysis, the following common drawing forms should be coded:

1. GAD Generator - Parameterized general arrangement drawings
2. Pier Detail Generator - Geometry + Reinforcement templates
3. Abutment Detail Generator - Various abutment types
4. Wing Wall Generator - Standard wing wall configurations
5. Bed Protection Generator - Anchorage and protection details
6. Deck Slab Generator - Slab reinforcement patterns
7. Cross Section Generator - Typical bridge cross-sections
8. Expansion Joint Generator - Joint detail templates
9. Bearing Detail Generator - Bearing pad configurations
10. Foundation Generator - Footing and pile templates

Each generator should support:
- Parameter input (dimensions, levels, materials)
- Multiple view generation (elevation, plan, section)
- Layer management
- Dimension and annotation placement
- DXF export capability
""")
        
        return '\n'.join(report)


def main():
    """Main execution."""
    base_path = r"C:\Users\Rajkumar\Downloads\Dwg-Dxf-Record-Keeper\COLLECTION FROM RECORD\Filtered_Drawings"
    
    print("=" * 80)
    print("Enhanced Drawing Collection Analyzer")
    print("=" * 80 + "\n")
    
    # Initialize analyzer
    analyzer = DrawingCollectionAnalyzer(base_path)
    
    # Scan drawings
    analyzer.scan_drawings()
    
    # Categorize
    analyzer.categorize_by_name()
    
    # Analyze patterns
    analyzer.analyze_common_patterns()
    
    # Show examples for major categories
    major_categories = [
        'GAD_GENERAL_ARRANGEMENT',
        'PIER_GEOMETRY',
        'PIER_REINFORCEMENT',
        'ABUTMENT_GENERAL',
        'WING_WALL',
        'BED_PROTECTION',
        'DECK_SLAB_DETAILS'
    ]
    
    for category in major_categories:
        analyzer.show_category_examples(category, max_examples=3)
    
    # Generate report
    report = analyzer.generate_summary_report()
    
    # Save report
    report_path = Path(base_path).parent / "drawing_collection_analysis.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n{'=' * 80}")
    print(f"Report saved to: {report_path}")
    print(f"{'=' * 80}")


if __name__ == "__main__":
    main()
