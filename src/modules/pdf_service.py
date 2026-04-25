"""
PDF Service
===========
Generates professional engineering design reports and BOQ in PDF format.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime
from pathlib import Path

class PDFService:
    @staticmethod
    def generate_design_report(project_data: dict, quantities: dict, warnings: list, output_path: str):
        """Generates a professional PDF design report."""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Custom Styles
        title_style = ParagraphStyle(
            'TitleStyle', parent=styles['Heading1'],
            fontSize=18, textColor=colors.HexColor("#1F4E78"),
            spaceAfter=20, alignment=1
        )
        
        # Title
        elements.append(Paragraph("BRIDGE ENGINEERING DESIGN REPORT", title_style))
        elements.append(Spacer(1, 12))

        # Project Metadata
        meta = project_data.get('metadata', {})
        meta_data = [
            ["Project Name:", meta.get('project_name', 'N/A')],
            ["Location:", meta.get('location', 'N/A')],
            ["Client:", meta.get('client', 'N/A')],
            ["Date:", datetime.now().strftime("%Y-%m-%d")],
            ["Bridge Type:", project_data.get('bridge_type', 'N/A')]
        ]
        t_meta = Table(meta_data, colWidths=[100, 300])
        t_meta.setStyle(TableStyle([
            ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(t_meta)
        elements.append(Spacer(1, 20))

        # Design Status / Warnings
        elements.append(Paragraph("Design Audit Status", styles['Heading2']))
        if not warnings:
            elements.append(Paragraph("✅ All IRC compliance checks passed.", styles['Normal']))
        else:
            for w in warnings:
                elements.append(Paragraph(f"• {w}", styles['Normal']))
        elements.append(Spacer(1, 20))

        # BOQ Table
        elements.append(Paragraph("Bill of Quantities (BOQ) Summary", styles['Heading2']))
        boq_data = [["Item Description", "Unit", "Quantity"]]
        for k, v in quantities.items():
            boq_data.append([k.replace("_", " "), "m3" if "m3" in k else "MT", str(v)])
            
        t_boq = Table(boq_data, colWidths=[250, 80, 80])
        t_boq.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#D7E4BC")),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(t_boq)

        # Footer
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("--- End of Report ---", styles['Italic']))

        try:
            doc.build(elements)
            return True
        except Exception as e:
            print(f"PDF Generation Error: {e}")
            return False
