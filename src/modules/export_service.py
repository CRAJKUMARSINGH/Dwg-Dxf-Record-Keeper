"""
Export Service
==============
Handles exporting BOQ to Excel and potentially PDF.
"""

import xlsxwriter
from pathlib import Path
from datetime import datetime

class ExportService:
    @staticmethod
    def export_boq_to_excel(project_data: dict, quantities: dict, output_path: str):
        """Generates a professional BOQ Excel sheet."""
        path = Path(output_path)
        workbook = xlsxwriter.Workbook(path)
        worksheet = workbook.add_worksheet("BOQ Summary")
        
        # Formats
        bold = workbook.add_format({'bold': True, 'bg_color': '#D7E4BC', 'border': 1})
        header = workbook.add_format({'bold': True, 'font_size': 14, 'font_color': '#1F4E78'})
        border = workbook.add_format({'border': 1})
        money = workbook.add_format({'num_format': '#,##0.00', 'border': 1})

        # Header
        worksheet.write('A1', 'BRIDGE ENGINEERING SUITE - BOQ REPORT', header)
        worksheet.write('A2', f"Project: {project_data.get('metadata', {}).get('project_name', 'Unnamed')}")
        worksheet.write('A3', f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # Table Headers
        worksheet.write('A5', 'Description', bold)
        worksheet.write('B5', 'Unit', bold)
        worksheet.write('C5', 'Quantity', bold)
        worksheet.write('D5', 'Rate (Assumed)', bold)
        worksheet.write('E5', 'Total Amount', bold)
        
        # Data
        data = [
            ('Concrete (Deck Slab)', 'm3', quantities.get('Concrete_Deck_m3', 0), 12000),
            ('Concrete (Piers)', 'm3', quantities.get('Concrete_Pier_m3', 0), 10000),
            ('Concrete (Abutments)', 'm3', quantities.get('Concrete_Abutment_m3', 0), 10000),
            ('Concrete (Foundations)', 'm3', quantities.get('Concrete_Foundations_m3', 0), 8000),
            ('Reinforcement Steel (Est.)', 'MT', quantities.get('Steel_Total_MT', 0), 75000),
            ('Earthwork Excavation', 'm3', quantities.get('Excavation_m3', 0), 400),
        ]
        
        row = 5
        total_sum = 0
        for desc, unit, qty, rate in data:
            amt = qty * rate
            total_sum += amt
            worksheet.write(row, 0, desc, border)
            worksheet.write(row, 1, unit, border)
            worksheet.write(row, 2, qty, money)
            worksheet.write(row, 3, rate, money)
            worksheet.write(row, 4, amt, money)
            row += 1
            
        # Total
        worksheet.write(row, 3, 'GRAND TOTAL', bold)
        worksheet.write(row, 4, total_sum, money)
        
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:E', 15)
        
        workbook.close()
        return True
