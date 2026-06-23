from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import Invoice, InvoiceItem


class InvoiceItemInline(TabularInline):
    model = InvoiceItem
    extra = 0
    fields = ['item_name', 'hsn_code', 'quantity', 'unit', 'price', 'gst_rate', 'total']
    readonly_fields = ['total']


@admin.register(Invoice)
class InvoiceAdmin(ModelAdmin):
    list_display = [
        'invoice_number',
        'customer',
        'display_total',
        'display_status',
        'date',
        'user',
    ]
    list_display_links = ['invoice_number', 'customer']
    list_filter_submit = True
    list_filter = ['status', 'date', 'user']
    search_fields = ['invoice_number', 'customer__name']
    list_per_page = 25
    inlines = [InvoiceItemInline]
    readonly_fields = ['invoice_number', 'subtotal', 'tax', 'total']

    fieldsets = (
        (
            'Invoice',
            {
                'fields': (
                    'user', 'customer', 'invoice_number', 'status',
                    'date', 'due_date', 'discount',
                ),
            },
        ),
        (
            'Totals',
            {
                'fields': ('subtotal', 'tax', 'total', 'pdf_url'),
            },
        ),
    )

    @display(description='Total', ordering='total')
    def display_total(self, obj):
        return f'₹ {obj.total:,.2f}'

    @display(
        description='Status',
        ordering='status',
        label={
            'confirmed': 'success',
            'draft': 'warning',
        },
    )
    def display_status(self, obj):
        return obj.status
