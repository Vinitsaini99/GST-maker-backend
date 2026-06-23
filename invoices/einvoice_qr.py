import json
from io import BytesIO

import qrcode
from reportlab.platypus import Image

from .company_profile import COMPANY_PROFILE


def build_einvoice_qr_payload(invoice) -> str:
    customer = invoice.customer
    items = list(invoice.items.all())
    display_number = invoice.invoice_number.replace('INV-', '', 1) if invoice.invoice_number else ''
    main_hsn = next((i.hsn_code for i in items if i.hsn_code), '')
    doc_dt = invoice.date.strftime('%d/%m/%Y') if invoice.date else ''

    payload = {
        'SellerGstin': COMPANY_PROFILE['gstin'],
        'BuyerGstin': getattr(customer, 'gstin', '') or '',
        'DocNo': display_number,
        'DocTyp': 'INV',
        'DocDt': doc_dt,
        'TotInvVal': float(invoice.total or 0),
        'ItemCnt': len(items),
        'MainHsnCode': main_hsn,
        'Irn': getattr(invoice, 'irn', '') or '',
        'AckNo': getattr(invoice, 'ack_no', '') or '',
        'AckDt': getattr(invoice, 'ack_date', '') or '',
    }
    return json.dumps(payload, separators=(',', ':'))


def make_qr_flowable(invoice, width_mm=25):
    from reportlab.lib.units import mm

    qr = qrcode.QRCode(version=None, box_size=3, border=1)
    qr.add_data(build_einvoice_qr_payload(invoice))
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    size = width_mm * mm
    return Image(buf, width=size, height=size)
