#!/usr/bin/env python3
"""
Conversor Markdown a PDF usando fpdf2 - Versión robusta
Formato APA: Arial 11, interlineado 1.5, márgenes normales (2.54cm)
"""

import re
from fpdf import FPDF

class PDFAPA(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25.4)
        font_dir = r'C:\Windows\Fonts'
        # Usar DejaVu Sans si está disponible, sino Arial
        try:
            self.add_font('DejaVu', '', f'{font_dir}\\DejaVuSans.ttf')
            self.add_font('DejaVu', 'B', f'{font_dir}\\DejaVuSans-Bold.ttf')
            self.add_font('DejaVu', 'I', f'{font_dir}\\DejaVuSans-Oblique.ttf')
            self.add_font('DejaVu', 'BI', f'{font_dir}\\DejaVuSans-BoldOblique.ttf')
            self.add_font('DejaVuMono', '', f'{font_dir}\\DejaVuSansMono.ttf')
            self.main_font = 'DejaVu'
            self.mono_font = 'DejaVuMono'
        except:
            self.add_font('Arial', '', f'{font_dir}\\arial.ttf')
            self.add_font('Arial', 'B', f'{font_dir}\\arialbd.ttf')
            self.add_font('Arial', 'I', f'{font_dir}\\ariali.ttf')
            self.add_font('Arial', 'BI', f'{font_dir}\\arialbi.ttf')
            self.add_font('Courier', '', f'{font_dir}\\cour.ttf')
            self.main_font = 'Arial'
            self.mono_font = 'Courier'
        
        self.set_font(self.main_font, '', 11)
    
    def write_text(self, text, style='', size=11, align='J'):
        self.set_font(self.main_font, style, size)
        line_h = size * 0.5 * 1.5
        self.multi_cell(0, line_h, text, 0, align)
        self.ln(2)

    def write_heading(self, text, level=1):
        sizes = {1: 16, 2: 14, 3: 12}
        self.set_font(self.main_font, 'B', sizes.get(level, 11))
        line_h = sizes.get(level, 11) * 0.5 * 1.5
        self.multi_cell(0, line_h, text, 0, 'L')
        self.ln(4 if level == 1 else 2)

    def write_code(self, lines):
        self.set_font(self.mono_font, '', 8)
        self.set_fill_color(245, 245, 245)
        for cl in lines:
            self.cell(0, 4, cl, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(3)
        self.set_font(self.main_font, '', 11)

    def write_hr(self):
        self.ln(3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def write_table(self, rows):
        if not rows:
            return
        n_cols = max(len(r) for r in rows)
        col_width = 180 / n_cols
        self.set_font(self.main_font, '', 8)
        
        for row_idx, row in enumerate(rows):
            while len(row) < n_cols:
                row.append('')
            
            row_height = 6
            
            if self.get_y() + row_height > 270:
                self.add_page()
            
            if row_idx == 0:
                self.set_font(self.main_font, 'B', 8)
                self.set_fill_color(242, 242, 242)
                fill = True
            else:
                self.set_font(self.main_font, '', 8)
                fill = False
            
            x_start = self.get_x()
            y_start = self.get_y()
            
            for col_idx, cell in enumerate(row):
                x = x_start + col_idx * col_width
                self.set_xy(x, y_start)
                cell_text = str(cell)[:50]
                self.cell(col_width, row_height, cell_text, border=1, new_x="RIGHT", new_y="TOP", fill=fill)
            
            self.set_xy(x_start, y_start + row_height)
        
        self.ln(5)


def clean_text(text):
    """Limpia markdown inline y caracteres no ASCII."""
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'`(.+?)`', r'\1', text)
    # Reemplazar caracteres especiales
    replacements = {
        '–': '-', '—': '-', ''': "'", ''': "'",
        '"': '"', '"': '"', '•': '-', '→': '->',
        '≤': '<=', '≥': '>=', '∑': 'Sum', '∞': 'inf',
        '│': '|', '┌': '+', '┐': '+', '└': '+', '┘': '+',
        '├': '+', '┤': '+', '┬': '+', '┴': '+', '┼': '+',
        '▪': '-', '●': '*', '▲': '^', '▼': 'v',
        '✓': 'OK', '✗': 'NO', '✅': 'OK',
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Eliminar cualquier char no latin-1 restante
    return ''.join(c if ord(c) < 256 else '?' for c in text)


def parse_markdown_to_pdf(md_path, pdf_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pdf = PDFAPA()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    lines = content.split('\n')
    in_code_block = False
    code_lines = []
    in_table = False
    table_rows = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Bloques de código
        if stripped.startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_lines = []
            else:
                in_code_block = False
                pdf.write_code([clean_text(c) for c in code_lines])
            i += 1
            continue
        
        if in_code_block:
            code_lines.append(line)
            i += 1
            continue
        
        # Tablas
        if stripped.startswith('|') and '|' in stripped:
            if not in_table:
                in_table = True
                table_rows = []
            
            cells = [c.strip() for c in stripped.split('|')[1:-1]]
            table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            if table_rows:
                # Filtrar fila de separadores (---)
                table_rows = [r for r in table_rows if not all(re.match(r'^[-:]+$', c) for c in r)]
                # Limpiar celdas
                table_rows = [[clean_text(c) for c in r] for r in table_rows]
                pdf.write_table(table_rows)
                table_rows = []
            in_table = False
            continue
        
        # Encabezados
        if stripped.startswith('# '):
            pdf.write_heading(clean_text(stripped[2:]), 1)
        elif stripped.startswith('## '):
            pdf.write_heading(clean_text(stripped[3:]), 2)
        elif stripped.startswith('### '):
            pdf.write_heading(clean_text(stripped[4:]), 3)
        # Línea horizontal
        elif stripped in ('---', '___', '***'):
            pdf.write_hr()
        # Texto normal
        elif stripped:
            pdf.write_text(clean_text(stripped))
        else:
            pdf.ln(3)
        
        i += 1
    
    # Tabla final
    if table_rows:
        table_rows = [r for r in table_rows if not all(re.match(r'^[-:]+$', c) for c in r)]
        table_rows = [[clean_text(c) for c in r] for r in table_rows]
        pdf.write_table(table_rows)
    
    pdf.output(pdf_path)
    print(f'PDF generado exitosamente: {pdf_path}')


if __name__ == '__main__':
    parse_markdown_to_pdf(
        r'C:\Users\Jeison Montoya\Downloads\Actividad2\campusguard_search\docs\documento_tecnico.md',
        r'C:\Users\Jeison Montoya\Downloads\Actividad2\campusguard_search\docs\documento_tecnico.pdf'
    )