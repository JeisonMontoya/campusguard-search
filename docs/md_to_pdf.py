#!/usr/bin/env python3
"""
Conversor y generador de Documento Técnico en PDF bajo norma APA 7.ª edición.
Garantiza: Arial 11 pt, interlineado 1.5, márgenes normales (2.54 cm), exactamente 5 páginas.
"""

import os
from generate_pdf_apa import build_pdf

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_pdf = os.path.join(base_dir, 'documento_tecnico.pdf')
    build_pdf(output_pdf)
