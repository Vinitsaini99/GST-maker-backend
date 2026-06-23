from decimal import Decimal

from django.db.models import Count, Sum

from customers.models import Customer
from invoices.models import Invoice, InvoiceItem
from products.models import Product


def _inr(value):
    if value is None:
        return '₹0.00'
    if isinstance(value, Decimal):
        value = float(value)
    return f'₹{value:,.2f}'


def dashboard_callback(request, context):
    invoices = Invoice.objects.all()
    confirmed = invoices.filter(status=Invoice.STATUS_CONFIRMED)
    drafts = invoices.filter(status=Invoice.STATUS_DRAFT)

    revenue = confirmed.aggregate(total=Sum('total'))['total'] or 0
    products_sold = InvoiceItem.objects.aggregate(total_qty=Sum('quantity'))

    customer_sales = (
        invoices.values('customer__name')
        .annotate(invoice_count=Count('id'), total_sales=Sum('total'))
        .order_by('-total_sales')[:5]
    )

    top_products = (
        InvoiceItem.objects.values('item_name')
        .annotate(qty_sold=Sum('quantity'), revenue=Sum('total'))
        .order_by('-qty_sold')[:5]
    )

    recent = invoices.select_related('customer').order_by('-created_at')[:6]

    context.update({
        'stats': {
            'total_invoices': invoices.count(),
            'confirmed_count': confirmed.count(),
            'draft_count': drafts.count(),
            'total_revenue': _inr(revenue),
            'total_customers': Customer.objects.count(),
            'total_products': Product.objects.count(),
            'active_products': Product.objects.filter(is_active=True).count(),
            'total_products_sold': int(products_sold['total_qty'] or 0),
        },
        'customer_sales': [
            {
                'name': row['customer__name'],
                'invoices': row['invoice_count'],
                'sales': _inr(row['total_sales']),
            }
            for row in customer_sales
        ],
        'top_products': [
            {
                'name': row['item_name'],
                'qty': int(row['qty_sold'] or 0),
                'revenue': _inr(row['revenue']),
            }
            for row in top_products
        ],
        'recent_invoices': [
            {
                'number': inv.invoice_number,
                'customer': inv.customer.name,
                'total': _inr(inv.total),
                'status': inv.get_status_display(),
                'status_key': inv.status,
                'url': f'/admin/invoices/invoice/{inv.pk}/change/',
                'date': inv.date.strftime('%d %b %Y'),
            }
            for inv in recent
        ],
    })
    return context
