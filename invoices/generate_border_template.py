"""Generate 2480x3508 PNG invoice border template (A4 @ 300 DPI)."""

from pathlib import Path

from PIL import Image, ImageDraw

WIDTH = 2480
HEIGHT = 3508
MARGIN = 120
INNER_W = WIDTH - 2 * MARGIN
INNER_H = HEIGHT - 2 * MARGIN
CORNER = 200

BLUE = '#1A5FB4'
BLUE_LIGHT = '#E8F1FA'
GRAY_DARK = '#2D3748'
GRAY_LINE = '#C5CED8'
GRAY_MUTED = '#64748B'
WHITE = '#FFFFFF'

OUT = Path(__file__).resolve().parent / 'assets' / 'invoice-border-template.png'


def _corner_brackets(draw, x, y, w, h, length=CORNER, color=BLUE, width=4):
    draw.line([(x, y + length), (x, y), (x + length, y)], fill=color, width=width, joint='curve')
    draw.line([(x + w - length, y), (x + w, y), (x + w, y + length)], fill=color, width=width, joint='curve')
    draw.line([(x, y + h - length), (x, y + h), (x + length, y + h)], fill=color, width=width, joint='curve')
    draw.line([(x + w - length, y + h), (x + w, y + h), (x + w, y + h - length)], fill=color, width=width, joint='curve')


def generate():
    img = Image.new('RGB', (WIDTH, HEIGHT), WHITE)
    draw = ImageDraw.Draw(img)

    x, y = MARGIN, MARGIN
    w, h = INNER_W, INNER_H

    draw.rectangle([x, y, x + w, y + h], outline=GRAY_DARK, width=3)
    draw.rectangle([x + 1, y + 1, x + w - 1, y + 9], fill=BLUE)

    _corner_brackets(draw, x, y, w, h)

    pad = 40
    cx, cy = x + pad, y + pad
    cw, ch = w - 2 * pad, h - 2 * pad

    header_h = 280
    draw.rectangle([cx, cy, cx + cw, cy + header_h], fill=BLUE_LIGHT, outline=GRAY_LINE, width=2)
    draw.line([(cx, cy + header_h), (cx + cw, cy + header_h)], fill=BLUE, width=3)

    party_y = cy + header_h + 20
    party_h = 300
    draw.rectangle([cx, party_y, cx + cw, party_y + party_h], outline=GRAY_LINE, width=2)

    items_y = party_y + party_h + 20
    items_h = 1180
    draw.rectangle([cx, items_y, cx + cw, items_y + items_h], outline=GRAY_DARK, width=2)
    draw.rectangle([cx, items_y, cx + cw, items_y + 70], fill=BLUE_LIGHT, outline=BLUE, width=2)
    draw.line([(cx, items_y + 70), (cx + cw, items_y + 70)], fill=BLUE, width=2)

    row_h = 80
    for i in range(1, (items_h - 70) // row_h):
        ry = items_y + 70 + i * row_h
        if ry < items_y + items_h:
            draw.line([(cx, ry), (cx + cw, ry)], fill=GRAY_LINE, width=1)

    col_x = [120, 620, 820, 960, 1100, 1260, 1420, 1580, 1740, 1900, 2060]
    for gx in col_x:
        draw.line([(cx + gx, items_y), (cx + gx, items_y + items_h)], fill=GRAY_LINE, width=1)

    tax_y = items_y + items_h + 20
    draw.rectangle([cx, tax_y, cx + cw, tax_y + 120], outline=GRAY_LINE, width=2)
    words_y = tax_y + 140
    draw.rectangle([cx, words_y, cx + cw, words_y + 100], outline=GRAY_LINE, width=2)

    footer_y = words_y + 120
    footer_h = cy + ch - footer_y
    draw.rectangle([cx, footer_y, cx + cw, footer_y + footer_h], outline=GRAY_DARK, width=2)
    draw.line([(cx, footer_y + 3), (cx + cw, footer_y + 3)], fill=BLUE, width=4)
    draw.line([(cx + int(cw * 0.37), footer_y), (cx + int(cw * 0.37), footer_y + footer_h)], fill=GRAY_LINE, width=2)
    draw.line([(cx + int(cw * 0.63), footer_y), (cx + int(cw * 0.63), footer_y + footer_h)], fill=GRAY_LINE, width=2)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT, 'PNG', dpi=(300, 300))
    print(f'Wrote {OUT} ({WIDTH}x{HEIGHT})')


if __name__ == '__main__':
    generate()
