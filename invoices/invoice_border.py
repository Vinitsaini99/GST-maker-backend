"""Modern GST invoice frame — blue/gray accents, corner brackets, section borders."""

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import TableStyle

BLUE = colors.HexColor('#1A5FB4')
BLUE_LIGHT = colors.HexColor('#E8F1FA')
GRAY_DARK = colors.HexColor('#2D3748')
GRAY_LINE = colors.HexColor('#C5CED8')
GRAY_MUTED = colors.HexColor('#64748B')

CORNER_LEN = 11 * mm
OUTER_LINE = 0.75
ACCENT_LINE = 1.25
SECTION_LINE = 0.5

_BASE = [
    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('TEXTCOLOR', (0, 0), (-1, -1), GRAY_DARK),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]


def _style(*rules, extra=None):
    styles = list(_BASE)
    for rule in rules:
        styles.extend(rule)
    if extra:
        styles.extend(extra)
    return TableStyle(styles)


def draw_invoice_frame(canvas, doc):
    x = doc.leftMargin
    y = doc.bottomMargin
    w = doc.width
    h = doc.height
    cs = CORNER_LEN

    canvas.saveState()

    canvas.setStrokeColor(GRAY_DARK)
    canvas.setLineWidth(OUTER_LINE)
    canvas.rect(x, y, w, h)

    canvas.setFillColor(BLUE)
    canvas.rect(x + 0.5, y + h - 2.2 * mm, w - 1, 0.9 * mm, fill=1, stroke=0)

    canvas.setStrokeColor(BLUE)
    canvas.setLineWidth(ACCENT_LINE)

    canvas.line(x, y + h - cs, x, y + h)
    canvas.line(x, y + h, x + cs, y + h)
    canvas.line(x + w - cs, y + h, x + w, y + h)
    canvas.line(x + w, y + h - cs, x + w, y + h)
    canvas.line(x, y, x + cs, y)
    canvas.line(x, y, x, y + cs)
    canvas.line(x + w - cs, y, x + w, y)
    canvas.line(x + w, y, x + w, y + cs)

    canvas.restoreState()


def header_section_style(extra=None):
    return _style([
        ('BOX', (0, 0), (-1, -1), SECTION_LINE, GRAY_LINE),
        ('LINEBELOW', (0, -1), (-1, -1), ACCENT_LINE, BLUE),
        ('BACKGROUND', (0, 0), (-1, 0), BLUE_LIGHT),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, 0), BLUE),
        ('FONTSIZE', (0, 0), (0, 0), 8),
        ('TEXTCOLOR', (2, 0), (2, 0), GRAY_MUTED),
        ('FONTNAME', (2, 0), (2, 0), 'Helvetica'),
    ], extra=extra)


def party_section_style(extra=None):
    return _style([
        ('BOX', (0, 0), (-1, -1), SECTION_LINE, BLUE),
        ('LINEBELOW', (0, 0), (-1, 0), SECTION_LINE, GRAY_LINE),
        ('LINEAFTER', (0, 1), (0, -1), ACCENT_LINE, BLUE),
    ], extra=extra)


def items_table_style(extra=None):
    vertical_lines = [
        ('LINEAFTER', (col, 0), (col, -1), 0.25, GRAY_LINE)
        for col in range(10)
    ]
    return _style([
        ('BOX', (0, 0), (-1, -1), SECTION_LINE, GRAY_DARK),
        *vertical_lines,
        ('LINEBELOW', (0, 0), (-1, 0), 0.5, GRAY_LINE),
        ('BACKGROUND', (0, 0), (-1, 0), BLUE_LIGHT),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (-1, 0), GRAY_DARK),
    ], extra=extra)


def summary_section_style(extra=None):
    return _style([
        ('BOX', (0, 0), (-1, -1), SECTION_LINE, GRAY_LINE),
        ('LINEBELOW', (0, 0), (-1, 0), SECTION_LINE, GRAY_LINE),
    ], extra=extra)


def footer_section_style(extra=None):
    return _style([
        ('BOX', (0, 0), (-1, -1), SECTION_LINE, GRAY_DARK),
        ('LINEABOVE', (0, 0), (-1, 0), ACCENT_LINE, BLUE),
        ('LINEAFTER', (0, 0), (0, 0), SECTION_LINE, GRAY_LINE),
        ('LINEAFTER', (1, 0), (1, 0), SECTION_LINE, GRAY_LINE),
    ], extra=extra)
