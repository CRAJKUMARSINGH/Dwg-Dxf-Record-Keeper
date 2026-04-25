"""
PDF Generator Module
====================
Professional PDF report generation for BridgeMaster Pro.
Generates structural dossiers, BOQ reports, and BBS tables.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import cm

class PDFGenerator:
    @staticmethod
    def generate_dossier(project_data: dict, bbs_entries, file_path: str):
        """Generates a professional Bridge Engineering Dossier."""
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # 1. Branding & Header
        title_style = ParagraphStyle(
            'TitleStyle', parent=styles['Heading1'],
            fontSize=24, textColor=colors.navy, spaceAfter=20, alignment=1
        )
        story.append(Paragraph("BridgeMaster Pro 2026", title_style))
        story.append(Paragraph("STRUCTURAL DESIGN DOSSIER", styles['Heading2']))
        story.append(Spacer(1, 1*cm))

        # 2. Project Metadata
        meta = project_data.get('metadata', {})
        story.append(Paragraph("1. PROJECT INFORMATION", styles['Heading3']))
        meta_data = [
            ["Project Name", meta.get('project_name', 'N/A')],
            ["Client", meta.get('client', 'N/A')],
            ["Location", meta.get('location', 'N/A')],
            ["Seismic Zone", meta.get('seismic_zone', 'N/A')],
            ["Date", datetime.now().strftime("%Y-%m-%d %H:%M")]
        ]
        t_meta = Table(meta_data, colWidths=[5*cm, 10*cm])
        t_meta.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_meta)
        story.append(Spacer(1, 1*cm))

        # 3. Structural Parameters
        story.append(Paragraph("2. SUBSTRUCTURE GEOMETRY", styles['Heading3']))
        sub = project_data.get('substructure', {})
        sub_data = [
            ["Pier Type", sub.get('pier_type', 'N/A')],
            ["Pier Height", f"{sub.get('pier_height', 0)} m"],
            ["Pier Width", f"{sub.get('pier_width', 0)} m"],
            ["Cap Width", f"{sub.get('cap_beam_width', 0)} m"]
        ]
        t_sub = Table(sub_data, colWidths=[5*cm, 10*cm])
        t_sub.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BACKGROUND', (0,0), (0,-1), colors.whitesmoke),
        ]))
        story.append(t_sub)
        story.append(Spacer(1, 1*cm))

        # 4. Bar Bending Schedule (BBS)
        story.append(Paragraph("3. BAR BENDING SCHEDULE (PIER)", styles['Heading3']))
        bbs_header = ["Mark", "Description", "Dia (mm)", "Length (m)", "Qty", "Weight (kg)"]
        bbs_data = [bbs_header]
        total_w = 0
        for e in bbs_entries:
            bbs_data.append([
                e.mark, e.description, str(e.diameter), 
                f"{e.length:.2f}", str(e.quantity), f"{e.total_weight:.2f}"
            ])
            total_w += e.total_weight
        
        bbs_data.append(["", "", "", "", "TOTAL STEEL", f"{total_w:.2f} kg"])
        
        t_bbs = Table(bbs_data, colWidths=[1.5*cm, 4*cm, 2*cm, 2.5*cm, 2.5*cm, 3*cm])
        t_bbs.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.navy),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (2,1), (-1,-1), 'CENTER'),
        ]))
        story.append(t_bbs)

        # Build PDF
        doc.build(story)
        return True
