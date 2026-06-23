from django.contrib.auth.models import User
from django.db import models


class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
    shortcut = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Shortcut',
        help_text='Short code for quick invoice entry (e.g. WD for wireless mouse, HOST for hosting).',
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Name',
        help_text='Display name shown on tax invoice line items.',
    )
    sku = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='SKU',
        help_text=(
            'SKU = Stock Keeping Unit — your unique internal product/inventory code '
            '(e.g. MOU-DEL-001, LAP-HP-15S). Optional; different from HSN or shortcut.'
        ),
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description',
        help_text='Optional notes about the product (not printed on invoice by default).',
    )
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Price',
        help_text='Unit price excluding GST (₹). Stock Keeping Unit (SKU) is separate from this amount.',
    )
    hsn_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='HSN/SAC',
        help_text=(
            'HSN = Harmonized System of Nomenclature (goods). '
            'SAC = Service Accounting Code (services). '
            'GST code, usually 4–8 digits only (e.g. 847160). Do not type "HSN" in this field.'
        ),
    )
    gst_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=18,
        verbose_name='GST %',
        help_text='Total GST percentage on this product (typically 5, 12, 18, or 28).',
    )
    unit = models.CharField(
        max_length=20,
        default='pcs',
        verbose_name='Unit',
        help_text='How quantity is counted on invoice (e.g. pcs, kg, box, hr).',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Active',
        help_text='Inactive products are hidden from new invoice item selection.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['shortcut', 'name']
        verbose_name = 'Product'
        verbose_name_plural = 'Product master'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'shortcut'],
                condition=models.Q(shortcut__gt=''),
                name='unique_product_shortcut_per_user',
            ),
        ]

    def __str__(self):
        if self.shortcut:
            return f'{self.shortcut} — {self.name}'
        return self.name
