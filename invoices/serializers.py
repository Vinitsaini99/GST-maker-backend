import re

from rest_framework import serializers

from customers.serializers import CustomerSerializer
from .models import Invoice, InvoiceItem

HSN_PATTERN = re.compile(r'^\d{4,8}$')

class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = [
            'id', 'item_name', 'hsn_code', 'quantity', 'unit', 'price', 'gst_rate',
            'taxable_amount', 'cgst_rate', 'cgst_amount', 'sgst_rate', 'sgst_amount', 'total',
        ]
        read_only_fields = [
            'taxable_amount', 'cgst_rate', 'cgst_amount', 'sgst_rate', 'sgst_amount', 'total',
        ]

    def validate_item_name(self, value):
        name = (value or '').strip()
        if not name:
            raise serializers.ValidationError('Item name is required.')
        return name

    def validate_quantity(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError('Quantity must be greater than 0.')
        return value

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
        code = str(value).strip()
        if not HSN_PATTERN.match(code):
            raise serializers.ValidationError('HSN/SAC should be 4–8 digits.')
        return code

class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)
    customer_details = CustomerSerializer(source='customer', read_only=True)
    pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'customer', 'customer_details', 'date', 'due_date',
            'subtotal', 'tax', 'discount', 'total', 'status', 'pdf_url', 'items',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'invoice_number', 'subtotal', 'tax', 'total', 'pdf_url',
            'created_at', 'updated_at',
        ]

    def get_pdf_url(self, obj):
        if obj.pdf_url:
            return obj.pdf_url.url
        return None


class InvoiceCreateSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ['customer', 'date', 'due_date', 'discount', 'status', 'items']

    def validate_items(self, value):
        cleaned = [item for item in value if item.get('item_name', '').strip()]
        if not cleaned:
            raise serializers.ValidationError('At least one item is required.')
        return cleaned

    def validate(self, attrs):
        instance = getattr(self, 'instance', None)
        date = attrs.get('date') or (instance.date if instance else None)
        due_date = attrs.get('due_date') or (instance.due_date if instance else None)

        if date and due_date and due_date < date:
            raise serializers.ValidationError({'due_date': 'Due date cannot be before invoice date.'})

        discount = attrs.get('discount')
        if discount is None and instance:
            discount = instance.discount
        if discount is not None and discount < 0:
            raise serializers.ValidationError({'discount': 'Discount cannot be negative.'})

        items = attrs.get('items')
        if items is not None and discount is not None:
            from decimal import Decimal

            from .tax_utils import compute_line_tax

            grand = Decimal('0')
            for item in items:
                calc = compute_line_tax(item['quantity'], item['price'], item.get('gst_rate', 18))
                grand += calc['total']
            if discount > grand:
                raise serializers.ValidationError({
                    'discount': f'Discount cannot exceed invoice total ({grand}).',
                })

        return attrs
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        user = self.context['request'].user
        invoice_number = Invoice.generate_invoice_number(user)
        invoice = Invoice.objects.create(
            user=user,
            invoice_number=invoice_number,
            **validated_data,
        )
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)
        invoice.recalculate_totals()
        return invoice

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                InvoiceItem.objects.create(invoice=instance, **item_data)
        instance.recalculate_totals()
        return instance
