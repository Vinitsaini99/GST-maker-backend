import os
from io import BytesIO
from pathlib import Path

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .company_profile import COMPANY_PROFILE
from .einvoice_qr import make_qr_flowable
from .invoice_border import (
    BLUE,
    BLUE_LIGHT,
    GRAY_DARK,
    GRAY_MUTED,
    draw_invoice_frame,
    footer_section_style,
    header_section_style,
    items_table_style,
    party_section_style,
    summary_section_style,
)
from .tax_utils import amount_in_words

LOGO_PATH = Path(__file__).resolve().parent / 'assets' / 'logo.png'

MARGIN = 8 * mm
CONTENT_W = 210 * mm - (2 * MARGIN)
FOOTER_H = 50 * mm
FOOTER_TOP_GAP = 8 * mm
FOOTER_BOTTOM_GAP = 3 * mm
SECTION_GAP = 2 * mm
HEADER_PARTY_GAP = 4 * mm
LOGO_SIZE = 22 * mm
BLANK_ROW_H = 5 * mm

ITEM_COL_RATIOS = [8, 42, 14, 12, 10, 16, 11, 14, 11, 14, 16]
ITEM_COLS = [CONTENT_W * (r / sum(ITEM_COL_RATIOS)) for r in ITEM_COL_RATIOS]

PARTY_COLS = [CONTENT_W * 0.48, CONTENT_W * 0.18, CONTENT_W * 0.34]
FOOTER_COLS = [CONTENT_W * 0.37, CONTENT_W * 0.26, CONTENT_W * 0.37]
TAX_COLS = [CONTENT_W * 0.17, CONTENT_W * 0.22, CONTENT_W * 0.20, CONTENT_W * 0.20, CONTENT_W * 0.21]
HEADER_COLS = [LOGO_SIZE, CONTENT_W - LOGO_SIZE - (30 * mm), 30 * mm]


def fmt(amount):
    return f'{float(amount):,.2f}'


def _logo_flowable():
    if LOGO_PATH.is_file():
        return RLImage(str(LOGO_PATH), width=LOGO_SIZE, height=LOGO_SIZE, kind='proportional')
    return Spacer(LOGO_SIZE, LOGO_SIZE)


def generate_invoice_pdf(invoice):
    buffer = BytesIO()
    company = COMPANY_PROFILE
    customer = invoice.customer

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=MARGIN,
        leftMargin=MARGIN,
        topMargin=MARGIN,
        bottomMargin=MARGIN,
    )

    styles = getSampleStyleSheet()
    normal = ParagraphStyle('Normal8', parent=styles['Normal'], fontSize=8, leading=11, textColor=GRAY_DARK)
    bold = ParagraphStyle('Bold8', parent=normal, fontName='Helvetica-Bold')
    center = ParagraphStyle('Center8', parent=normal, alignment=1)
    title = ParagraphStyle('Title', parent=bold, alignment=1, fontSize=12, leading=14, textColor=BLUE)
    company_name = ParagraphStyle(
        'CompanyName',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=1,
        textColor=GRAY_DARK,
    )
    gstin_line = ParagraphStyle(
        'GstinLine', parent=normal, fontSize=8, fontName='Helvetica-Bold', textColor=BLUE, leading=10,
    )
    copy_line = ParagraphStyle(
        'CopyLine', parent=normal, fontSize=7.5, textColor=GRAY_MUTED, alignment=2, leading=10,
    )
    right = ParagraphStyle('Right8', parent=normal, alignment=2)
    right_bold = ParagraphStyle('RightBold8', parent=bold, alignment=2)

    story = []

    header = Table(
        [
            [
                Paragraph(f'GSTIN : {company["gstin"]}', gstin_line),
                '',
                Paragraph('Original Copy', copy_line),
            ],
            [_logo_flowable(), Paragraph('TAX INVOICE', title), ''],
            ['', Paragraph(company['name'], company_name), ''],
            ['', Paragraph(company['address'], center), ''],
            ['', Paragraph(
                f'Tel. : {company["phone"]}'
                f'{"&nbsp;" * 10}'
                f'email : {company["email"]}',
                center,
            ), ''],
        ],
        colWidths=HEADER_COLS,
        rowHeights=[None, None, 9 * mm, None, None],
    )
    header.setStyle(header_section_style([
        ('SPAN', (0, 0), (1, 0)),
        ('SPAN', (0, 1), (0, 4)),
        ('SPAN', (1, 1), (2, 1)),
        ('SPAN', (1, 2), (2, 2)),
        ('SPAN', (1, 3), (2, 3)),
        ('SPAN', (1, 4), (2, 4)),
        ('BACKGROUND', (0, 0), (1, 0), BLUE_LIGHT),
        ('BACKGROUND', (2, 0), (2, 0), BLUE_LIGHT),
        ('FONTNAME', (1, 2), (2, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (1, 2), (2, 2), 16),
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('VALIGN', (1, 2), (2, 2), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (1, 2), (2, 2), 5),
        ('BOTTOMPADDING', (1, 2), (2, 2), 5),
        ('ALIGN', (0, 1), (0, 4), 'CENTER'),
        ('VALIGN', (0, 1), (0, 4), 'MIDDLE'),
        ('ALIGN', (1, 1), (2, 4), 'CENTER'),
        ('BOTTOMPADDING', (1, 4), (2, 4), 10),
    ]))
    story.append(header)
    story.append(Spacer(1, HEADER_PARTY_GAP))

    display_number = invoice.invoice_number.replace('INV-', '')
    party_meta = Table(
        [
            ['Party Details :', 'Invoice No.', display_number],
            [customer.name, 'Dated', invoice.date.strftime('%d-%m-%Y')],
            [customer.address or '', 'Place of Supply', company['place_of_supply']],
            [f'Party Mobile No : {customer.phone or ""}', 'Reverse Charge', company['reverse_charge']],
            [f'GSTIN / UIN : {customer.gstin or ""}', 'Transport', company['transport']],
            ['', 'Station', company['station']],
            ['IRN :', 'Ack.No. :', 'Ack. Date :'],
        ],
        colWidths=PARTY_COLS,
    )
    party_meta.setStyle(party_section_style([
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, 5), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
    ]))
    story.append(party_meta)
    story.append(Spacer(1, SECTION_GAP))

    rows = [[
        'S.N.', 'Description of Goods', 'HSN/SAC\nCode', 'Qty.', 'Unit', 'Price',
        'CGST\nRate', 'CGST\nAmount', 'SGST\nRate', 'SGST\nAmount', 'Amount\n(Rs.)',
    ]]
    total_qty = 0
    items_grand = 0
    item_count = 0
    for idx, item in enumerate(invoice.items.all(), start=1):
        item_count += 1
        total_qty += float(item.quantity)
        items_grand += float(item.total)
        rows.append([
            str(idx),
            item.item_name,
            item.hsn_code or '',
            fmt(item.quantity),
            item.unit,
            fmt(item.price),
            f'{item.cgst_rate} %',
            fmt(item.cgst_amount),
            f'{item.sgst_rate} %',
            fmt(item.sgst_amount),
            fmt(item.total),
        ])

    blank_rows = max(0, min(5, 8 - item_count))
    blank_start = len(rows)
    for _ in range(blank_rows):
        rows.append([''] * 11)

    rows.append([
        'Grand Total', '', '', fmt(total_qty), 'Pcs.', '', '', '', '', '', fmt(items_grand),
    ])

    discount = float(invoice.discount or 0)
    if discount > 0:
        rows.append([
            'Less : Discount', '', '', '', '', '', '', '', '', '', f'- {fmt(discount)}',
        ])
        rows.append([
            'Net Payable', '', '', '', '', '', '', '', '', '', fmt(invoice.total),
        ])

    summary_start = len(rows) - (3 if discount > 0 else 1)
    bold_rows = {0} | set(range(summary_start, len(rows)))

    row_heights = [None] * len(rows)
    for row_idx in range(blank_start, blank_start + blank_rows):
        row_heights[row_idx] = BLANK_ROW_H

    items_table = Table(rows, colWidths=ITEM_COLS, rowHeights=row_heights, repeatRows=1)
    items_table.setStyle(items_table_style([
        *[
            ('FONTNAME', (0, row_idx), (-1, row_idx), 'Helvetica-Bold')
            for row_idx in bold_rows
            if row_idx > 0
        ],
        ('FONTSIZE', (0, 0), (-1, -1), 7.5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('ALIGN', (5, 1), (5, -1), 'RIGHT'),
        ('ALIGN', (10, 1), (10, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        *[
            ('SPAN', (0, row_idx), (2, row_idx))
            for row_idx in range(summary_start, len(rows))
        ],
        ('LINEABOVE', (0, summary_start), (-1, summary_start), 0.5, GRAY_DARK),
    ]))
    story.append(items_table)
    story.append(Spacer(1, SECTION_GAP))

    cgst_sum = sum(float(i.cgst_amount) for i in invoice.items.all())
    sgst_sum = sum(float(i.sgst_amount) for i in invoice.items.all())
    tax_summary = Table(
        [
            ['Tax Rate', 'Taxable Amt.', 'CGST Amt.', 'SGST Amt.', 'Total Tax'],
            ['18 %', fmt(invoice.subtotal), fmt(cgst_sum), fmt(sgst_sum), fmt(invoice.tax)],
        ],
        colWidths=TAX_COLS,
    )
    tax_summary.setStyle(summary_section_style([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 1), (-1, 1), 'LEFT'),
    ]))
    story.append(tax_summary)
    story.append(Spacer(1, SECTION_GAP))

    words_block = Table(
        [[Paragraph(
            f'<b>Amount in words :</b> {amount_in_words(invoice.total)}<br/>Party - {fmt(invoice.total)}',
            normal,
        )]],
        colWidths=[CONTENT_W],
    )
    words_block.setStyle(summary_section_style([
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(words_block)
    story.append(Spacer(1, FOOTER_TOP_GAP))

    terms = '<br/>'.join(f'{i + 1}. {t}' for i, t in enumerate(company['terms']))
    bank_cell = Paragraph(
        f'<b>Bank Details</b><br/>{company["bank_name"]}<br/>'
        f'A/C NO :- {company["bank_account"]}<br/>IFSC CODE:- {company["bank_ifsc"]}<br/><br/>'
        f'<b>Terms &amp; Conditions</b><br/>{terms}',
        normal,
    )
    qr_cell = Table(
        [
            [Paragraph('<b>E-Invoice QR Code</b>', center)],
            [make_qr_flowable(invoice, width_mm=18)],
        ],
        colWidths=[FOOTER_COLS[1] - 8],
    )
    qr_cell.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))
    sign_cell = Table(
        [
            [Paragraph("Receiver's Signature :", right)],
            [''],
            [Paragraph(f'<b>For {company["name"]}</b><br/>Authorised Signatory', right_bold)],
        ],
        colWidths=[FOOTER_COLS[2] - 8 * mm],
        rowHeights=[7 * mm, 22 * mm, 10 * mm],
    )
    sign_cell.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ('VALIGN', (0, 1), (0, 1), 'TOP'),
        ('VALIGN', (0, 2), (0, 2), 'BOTTOM'),
        ('TEXTCOLOR', (0, 0), (-1, -1), GRAY_DARK),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    footer = Table(
        [[bank_cell, qr_cell, sign_cell]],
        colWidths=FOOTER_COLS,
        rowHeights=[FOOTER_H],
    )
    footer.setStyle(footer_section_style([
        ('VALIGN', (0, 0), (0, 0), 'TOP'),
        ('VALIGN', (1, 0), (1, 0), 'MIDDLE'),
        ('VALIGN', (2, 0), (2, 0), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(footer)
    story.append(Spacer(1, FOOTER_BOTTOM_GAP))

    doc.build(story, onFirstPage=draw_invoice_frame, onLaterPages=draw_invoice_frame)
    buffer.seek(0)

    pdf_dir = settings.MEDIA_ROOT / 'invoices' / 'pdf'
    os.makedirs(pdf_dir, exist_ok=True)
    filename = f'{invoice.invoice_number}.pdf'
    filepath = pdf_dir / filename

    with open(filepath, 'wb') as f:
        f.write(buffer.getvalue())

    relative_path = f'invoices/pdf/{filename}'
    invoice.pdf_url.name = relative_path
    invoice.save(update_fields=['pdf_url', 'updated_at'])
    return invoice.pdf_url
