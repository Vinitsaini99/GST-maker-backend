from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max

from .tax_utils import compute_line_tax


class Invoice(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_CONFIRMED, 'Confirmed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invoices')
    customer = models.ForeignKey(
        'customers.Customer', on_delete=models.PROTECT, related_name='invoices'
    )
    invoice_number = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    pdf_url = models.FileField(upload_to='invoices/pdf/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.invoice_number

    @classmethod
    def generate_invoice_number(cls, user):
        prefix = 'INV-'
        last = cls.objects.filter(invoice_number__startswith=prefix).aggregate(
            max_num=Max('invoice_number')
        )['max_num']
        if last:
            try:
                num = int(last.split('-')[1]) + 1
            except (IndexError, ValueError):
                num = cls.objects.count() + 1001
        else:
            num = 1001
        candidate = f'{prefix}{num}'
        while cls.objects.filter(invoice_number=candidate).exists():
            num += 1
            candidate = f'{prefix}{num}'
        return candidate

    def recalculate_totals(self):
        items = self.items.all()
        subtotal = Decimal('0')
        cgst_total = Decimal('0')
        sgst_total = Decimal('0')
        grand = Decimal('0')
        for item in items:
            subtotal += item.taxable_amount
            cgst_total += item.cgst_amount
            sgst_total += item.sgst_amount
            grand += item.total
        tax = cgst_total + sgst_total
        total = grand - Decimal(str(self.discount or 0))
        if total < 0:
            total = Decimal('0')
        self.subtotal = subtotal
        self.tax = tax
        self.total = total
        self.save(update_fields=['subtotal', 'tax', 'total', 'updated_at'])


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=255)
    hsn_code = models.CharField(max_length=20, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    unit = models.CharField(max_length=20, default='Pcs.')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=18)
    taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=9)
    cgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sgst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=9)
    sgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        calc = compute_line_tax(self.quantity, self.price, self.gst_rate)
        self.taxable_amount = calc['taxable']
        self.cgst_rate = calc['cgst_rate']
        self.cgst_amount = calc['cgst_amount']
        self.sgst_rate = calc['sgst_rate']
        self.sgst_amount = calc['sgst_amount']
        self.total = calc['total']
        super().save(*args, **kwargs)

    def __str__(self):
        return self.item_name
