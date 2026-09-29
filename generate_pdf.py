#!/usr/bin/env python3
"""
Generate a professional PDF from the Looker Dashboard Design markdown.
Uses reportlab for PDF generation with styled paragraphs.
"""

import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, Preformatted, KeepTogether
)
from reportlab.lib import colors


# ── Color Palette ──
DARK_BG = HexColor("#0F1724")
CARD_BG = HexColor("#1A2535")
ACCENT_BLUE = HexColor("#4285F4")
SUCCESS_GREEN = HexColor("#34A853")
ERROR_RED = HexColor("#EA4335")
WARNING_AMBER = HexColor("#FBBC04")
TEXT_PRIMARY = HexColor("#1a1a2e")
TEXT_SECONDARY = HexColor("#444466")
HEADER_BG = HexColor("#EEF1F8")
TABLE_HEADER_BG = HexColor("#2C3E6B")
TABLE_ALT_ROW = HexColor("#F4F6FB")
BORDER_COLOR = HexColor("#D0D5E0")
CODE_BG = HexColor("#F0F2F5")


def build_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        'DocTitle', parent=styles['Title'],
        fontSize=22, leading=28, textColor=HexColor("#1a1a2e"),
        spaceAfter=4, fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontSize=10, leading=14, textColor=TEXT_SECONDARY,
        spaceAfter=16, fontName='Helvetica',
    ))
    styles.add(ParagraphStyle(
        'H1', parent=styles['Heading1'],
        fontSize=18, leading=24, textColor=ACCENT_BLUE,
        spaceBefore=20, spaceAfter=10, fontName='Helvetica-Bold',
        borderWidth=0, borderPadding=0,
    ))
    styles.add(ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontSize=14, leading=18, textColor=HexColor("#2C3E6B"),
        spaceBefore=14, spaceAfter=6, fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        'H3', parent=styles['Heading3'],
        fontSize=12, leading=16, textColor=HexColor("#3D4F7C"),
        spaceBefore=10, spaceAfter=4, fontName='Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        'BodyText2', parent=styles['Normal'],
        fontSize=9.5, leading=14, textColor=TEXT_PRIMARY,
        spaceAfter=6, fontName='Helvetica',
    ))
    styles.add(ParagraphStyle(
        'BulletItem', parent=styles['Normal'],
        fontSize=9.5, leading=14, textColor=TEXT_PRIMARY,
        spaceAfter=3, fontName='Helvetica',
        leftIndent=16, bulletIndent=6,
    ))
    styles.add(ParagraphStyle(
        'CodeBlock', parent=styles['Normal'],
        fontSize=8, leading=11, textColor=HexColor("#333355"),
        fontName='Courier', backColor=CODE_BG,
        leftIndent=8, rightIndent=8, spaceBefore=4, spaceAfter=6,
        borderWidth=0.5, borderColor=BORDER_COLOR, borderPadding=6,
    ))
    styles.add(ParagraphStyle(
        'ChecklistItem', parent=styles['Normal'],
        fontSize=9.5, leading=14, textColor=TEXT_PRIMARY,
        spaceAfter=2, fontName='Helvetica',
        leftIndent=16, bulletIndent=6,
    ))
    return styles


def parse_markdown_to_flowables(md_text, styles):
    flowables = []
    lines = md_text.split('\n')
    i = 0
    in_code_block = False
    code_lines = []
    in_table = False
    table_rows = []

    def flush_table():
        nonlocal table_rows, in_table
        if not table_rows:
            in_table = False
            return
        # Filter out separator rows (e.g., |---|---|)
        data_rows = []
        for row in table_rows:
            cells = [c.strip() for c in row.strip('|').split('|')]
            if all(re.match(r'^[-:]+$', c) for c in cells):
                continue
            data_rows.append(cells)

        if not data_rows:
            in_table = False
            table_rows = []
            return

        # Normalize column count
        max_cols = max(len(r) for r in data_rows)
        for r in data_rows:
            while len(r) < max_cols:
                r.append('')

        # Convert to Paragraphs
        para_data = []
        for ri, row in enumerate(data_rows):
            para_row = []
            for cell in row:
                cell_clean = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', cell)
                cell_clean = re.sub(r'`(.+?)`', r'<font face="Courier" size="8" color="#2C3E6B">\1</font>', cell_clean)
                if ri == 0:
                    para_row.append(Paragraph(
                        f'<font color="white" size="8"><b>{cell_clean}</b></font>',
                        styles['BodyText2']))
                else:
                    para_row.append(Paragraph(
                        f'<font size="8">{cell_clean}</font>',
                        styles['BodyText2']))
            para_data.append(para_row)

        col_widths = [None] * max_cols
        available = 170 * mm
        for ci in range(max_cols):
            col_widths[ci] = available / max_cols

        t = Table(para_data, colWidths=col_widths, repeatRows=1)

        style_cmds = [
            ('BACKGROUND', (0, 0), (-1, 0), TABLE_HEADER_BG),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, BORDER_COLOR),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, TABLE_ALT_ROW]),
        ]
        t.setStyle(TableStyle(style_cmds))
        flowables.append(Spacer(1, 4 * mm))
        flowables.append(t)
        flowables.append(Spacer(1, 4 * mm))

        table_rows = []
        in_table = False

    while i < len(lines):
        line = lines[i]

        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                code_text = '\n'.join(code_lines)
                # Use Preformatted for code to preserve spacing
                flowables.append(Spacer(1, 2 * mm))
                for cl in code_lines:
                    cl_escaped = cl.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                    flowables.append(Paragraph(cl_escaped, styles['CodeBlock']))
                flowables.append(Spacer(1, 2 * mm))
                code_lines = []
                in_code_block = False
            else:
                if in_table:
                    flush_table()
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Table rows
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
            table_rows.append(line)
            i += 1
            continue
        else:
            if in_table:
                flush_table()

        stripped = line.strip()

        # Empty line
        if not stripped:
            i += 1
            continue

        # Horizontal rule
        if stripped in ['---', '***', '___']:
            flowables.append(Spacer(1, 3 * mm))
            flowables.append(HRFlowable(
                width="100%", thickness=1, color=BORDER_COLOR,
                spaceAfter=3 * mm, spaceBefore=1 * mm))
            i += 1
            continue

        # Headers
        if stripped.startswith('# ') and not stripped.startswith('## '):
            text = stripped[2:].strip()
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
            flowables.append(Paragraph(text, styles['DocTitle']))
            i += 1
            continue

        if stripped.startswith('## '):
            text = stripped[3:].strip()
            # Clean markdown formatting
            text = re.sub(r'\[.*?\]\(.*?\)', lambda m: re.search(r'\[(.*?)\]', m.group()).group(1), text)
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
            flowables.append(Paragraph(text, styles['H1']))
            i += 1
            continue

        if stripped.startswith('### '):
            text = stripped[4:].strip()
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
            flowables.append(Paragraph(text, styles['H2']))
            i += 1
            continue

        if stripped.startswith('#### '):
            text = stripped[5:].strip()
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
            flowables.append(Paragraph(text, styles['H3']))
            i += 1
            continue

        # Checklist items
        if stripped.startswith('- [ ]') or stripped.startswith('- [x]') or stripped.startswith('- [/]'):
            marker = '☐' if '[ ]' in stripped[:6] else ('☑' if '[x]' in stripped[:6] else '◐')
            text = stripped[5:].strip()
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'`(.+?)`', r'<font face="Courier" size="8" color="#2C3E6B">\1</font>', text)
            flowables.append(Paragraph(f'{marker}  {text}', styles['ChecklistItem']))
            i += 1
            continue

        # Bullet items
        if stripped.startswith('- ') or stripped.startswith('* '):
            text = stripped[2:].strip()
            text = format_inline(text)
            flowables.append(Paragraph(f'•  {text}', styles['BulletItem']))
            i += 1
            continue

        # Numbered list
        num_match = re.match(r'^(\d+)\.\s+(.+)', stripped)
        if num_match:
            num = num_match.group(1)
            text = format_inline(num_match.group(2))
            flowables.append(Paragraph(f'{num}.  {text}', styles['BulletItem']))
            i += 1
            continue

        # Block quote / tip
        if stripped.startswith('> '):
            text = stripped[2:].strip()
            if text.startswith('**'):
                text = format_inline(text)
            else:
                text = format_inline(text)
            flowables.append(Paragraph(
                f'<font color="#2C3E6B">▎ </font>{text}',
                styles['BulletItem']))
            i += 1
            continue

        # Regular paragraph
        text = format_inline(stripped)
        if text:
            flowables.append(Paragraph(text, styles['BodyText2']))
        i += 1

    if in_table:
        flush_table()

    return flowables


def format_inline(text):
    """Convert markdown inline formatting to reportlab XML tags."""
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    # Inline code
    text = re.sub(r'`(.+?)`', r'<font face="Courier" size="8" color="#2C3E6B">\1</font>', text)
    # Links — just show text
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'<u>\1</u>', text)
    return text


def add_page_number(canvas, doc):
    canvas.saveState()
    # Footer
    canvas.setFillColor(HexColor("#888888"))
    canvas.setFont('Helvetica', 8)
    canvas.drawString(20 * mm, 10 * mm, "SYNTRIX — CloudMart Looker Studio Dashboard Design Guide")
    canvas.drawRightString(A4[0] - 20 * mm, 10 * mm, f"Page {doc.page}")
    # Header line
    canvas.setStrokeColor(BORDER_COLOR)
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, A4[1] - 18 * mm, A4[0] - 20 * mm, A4[1] - 18 * mm)
    # Footer line
    canvas.line(20 * mm, 15 * mm, A4[0] - 20 * mm, 15 * mm)
    canvas.restoreState()


def main():
    input_file = "Looker_Dashboard_Design.md"
    output_file = "Looker_Dashboard_Design.pdf"

    with open(input_file, 'r') as f:
        md_text = f.read()

    styles = build_styles()

    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=25 * mm,
        bottomMargin=22 * mm,
        title="SYNTRIX — Looker Studio Dashboard Design & Implementation Guide",
        author="SYNTRIX Analytics Team",
    )

    flowables = []

    # Cover page info
    flowables.append(Spacer(1, 30 * mm))
    flowables.append(Paragraph(
        "SYNTRIX", ParagraphStyle(
            'CoverLogo', parent=styles['DocTitle'],
            fontSize=42, textColor=ACCENT_BLUE, alignment=TA_CENTER,
            fontName='Helvetica-Bold',
        )))
    flowables.append(Spacer(1, 6 * mm))
    flowables.append(Paragraph(
        "Looker Studio Dashboard Design<br/>&amp; Implementation Guide",
        ParagraphStyle(
            'CoverTitle', parent=styles['DocTitle'],
            fontSize=22, textColor=TEXT_PRIMARY, alignment=TA_CENTER,
            leading=28,
        )))
    flowables.append(Spacer(1, 10 * mm))
    flowables.append(HRFlowable(width="60%", thickness=2, color=ACCENT_BLUE, spaceAfter=6 * mm))
    flowables.append(Paragraph(
        "CloudMart Enterprise Log Monitoring &amp; Visualization Platform",
        ParagraphStyle('CoverSub', parent=styles['DocSubtitle'],
                       fontSize=12, alignment=TA_CENTER, textColor=TEXT_SECONDARY)))
    flowables.append(Spacer(1, 20 * mm))

    cover_info = [
        ["Project", "CloudMart Enterprise Observability"],
        ["Version", "1.0"],
        ["Prepared By", "SYNTRIX Analytics Team"],
        ["Date", "August 2026"],
        ["Platform", "Google Cloud Platform — Looker Studio"],
    ]
    cover_table = Table(cover_info, colWidths=[50 * mm, 100 * mm])
    cover_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), ACCENT_BLUE),
        ('TEXTCOLOR', (1, 0), (1, -1), TEXT_PRIMARY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -2), 0.5, BORDER_COLOR),
    ]))
    flowables.append(cover_table)
    flowables.append(PageBreak())

    # Parse and add the rest of the markdown
    body = parse_markdown_to_flowables(md_text, styles)
    flowables.extend(body)

    doc.build(flowables, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"✅ PDF generated: {output_file}")


if __name__ == '__main__':
    main()
