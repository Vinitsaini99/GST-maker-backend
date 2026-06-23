import re

from rest_framework import serializers

from .models import Product

PRODUCT_FIELD_HELP = {
    'shortcut': 'Short code for quick invoice entry (e.g. WD, HOST).',
    'name': 'Product name printed on the tax invoice.',
    'sku': (
        'SKU — Stock Keeping Unit: unique internal product/inventory code '
        '(e.g. MOU-DEL-001). Optional.'
    ),
    'description': 'Optional product notes.',
    'price': 'Unit price excluding GST (₹).',
    'hsn_code': (
        'HSN (Harmonized System of Nomenclature) for goods, or '
        'SAC (Service Accounting Code) for services — 4–8 digit GST code.'
    ),
    'gst_rate': 'Total GST percentage (e.g. 18 for 18% GST).',
    'unit': 'Unit of measure on invoice (pcs, kg, box, hr, etc.).',
    'is_active': 'If false, product is hidden from new invoice selection.',
}


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id', 'shortcut', 'name', 'sku', 'description', 'price', 'hsn_code',
            'gst_rate', 'unit', 'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'shortcut': {
                'label': 'Shortcut code',
                'help_text': PRODUCT_FIELD_HELP['shortcut'],
            },
            'name': {
                'label': 'Product name',
                'help_text': PRODUCT_FIELD_HELP['name'],
            },
            'sku': {
                'label': 'SKU (Stock Keeping Unit)',
                'help_text': PRODUCT_FIELD_HELP['sku'],
            },
            'description': {
                'help_text': PRODUCT_FIELD_HELP['description'],
            },
            'price': {
                'label': 'Unit price (excl. GST)',
                'help_text': PRODUCT_FIELD_HELP['price'],
            },
            'hsn_code': {
                'label': 'HSN / SAC code',
                'help_text': PRODUCT_FIELD_HELP['hsn_code'],
            },
            'gst_rate': {
                'label': 'GST rate (%)',
                'help_text': PRODUCT_FIELD_HELP['gst_rate'],
            },
            'unit': {
                'label': 'Unit of measure',
                'help_text': PRODUCT_FIELD_HELP['unit'],
            },
            'is_active': {
                'help_text': PRODUCT_FIELD_HELP['is_active'],
            },
        }

    def validate_name(self, value):
        name = (value or '').strip()
        if len(name) < 2:
            raise serializers.ValidationError('Product name must be at least 2 characters.')
        return name

    def validate_price(self, value):
        if value is None or value < 0:
            raise serializers.ValidationError('Price cannot be negative.')
        return value

    def validate_gst_rate(self, value):
        if value is None or value < 0 or value > 100:
            raise serializers.ValidationError('GST rate must be between 0 and 100.')
        return value

    def validate_hsn_code(self, value):
        if not value or not str(value).strip():
            return ''
        code = re.sub(r'\D', '', str(value).strip())
        if not code or len(code) < 4 or len(code) > 8:
            raise serializers.ValidationError(
                'HSN/SAC should be 4–8 digits only (e.g. 847160). Do not include the word "HSN".'
            )
        return code

    def validate_shortcut(self, value):
        value = (value or '').strip().upper()
        if not value:
            return value
        user = self.context['request'].user
        qs = Product.objects.filter(user=user, shortcut__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Shortcut already exists for this account.')
        return value

    def validate_sku(self, value):
        if not value:
            return value
        user = self.context['request'].user
        qs = Product.objects.filter(user=user, sku=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('SKU (Stock Keeping Unit) already exists for this account.')
        return value
