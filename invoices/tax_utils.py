from decimal import Decimal, ROUND_HALF_UP

ONES = [
    '', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
    'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
    'Seventeen', 'Eighteen', 'Nineteen',
]
TENS = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']


def _two_digits(num):
    if num < 20:
        return ONES[num]
    return f'{TENS[num // 10]} {ONES[num % 10]}'.strip()


def _convert_hundreds(num):
    parts = []
    if num >= 100:
        parts.append(f'{ONES[num // 100]} Hundred')
        num %= 100
    if num:
        parts.append(_two_digits(num))
    return ' '.join(parts).strip()


def amount_in_words(amount):
    value = int(Decimal(str(amount)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    if value == 0:
        return 'Rupees Zero Only'
    parts = []
    crore = value // 10000000
    value %= 10000000
    lakh = value // 100000
    value %= 100000
    thousand = value // 1000
    value %= 1000
    if crore:
        parts.append(f'{_convert_hundreds(crore)} Crore')
    if lakh:
        parts.append(f'{_convert_hundreds(lakh)} Lakh')
    if thousand:
        parts.append(f'{_convert_hundreds(thousand)} Thousand')
    if value:
        parts.append(_convert_hundreds(value))
    words = ' '.join(parts).strip()
    return f'Rupees {words} Only'


def compute_line_tax(quantity, price, gst_rate=Decimal('18')):
    qty = Decimal(str(quantity))
    unit_price = Decimal(str(price))
    gst_rate = Decimal(str(gst_rate))
    taxable = (qty * unit_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    half_rate = (gst_rate / Decimal('2')).quantize(Decimal('0.01'))
    cgst = (taxable * half_rate / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    sgst = cgst
    total = taxable + cgst + sgst
    return {
        'taxable': taxable,
        'cgst_rate': half_rate,
        'cgst_amount': cgst,
        'sgst_rate': half_rate,
        'sgst_amount': sgst,
        'total': total,
    }
