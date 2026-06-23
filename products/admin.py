from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import Product


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = [
        'shortcut',
        'name',
        'sku',
        'display_price',
        'hsn_code',
        'gst_rate',
        'unit',
        'display_active',
        'user',
    ]
    list_display_links = ['shortcut', 'name']
    list_filter = ['is_active', 'user', 'gst_rate']
    list_filter_submit = True
    search_fields = ['shortcut', 'name', 'sku', 'hsn_code']
    ordering = ['shortcut', 'name']
    list_per_page = 25

    fieldsets = (
        (
            'Product identity',
            {
                'fields': ('user', 'shortcut', 'name', 'sku', 'is_active'),
                'description': (
                    '<strong>Shortcut</strong> — quick code in invoices (e.g. HD). '
                    '<strong>SKU</strong> = Stock Keeping Unit — internal inventory code.'
                ),
            },
        ),
        (
            'Pricing & GST',
            {
                'fields': ('price', 'hsn_code', 'gst_rate', 'unit'),
                'description': (
                    '<strong>HSN</strong> = Harmonized System of Nomenclature. '
                    '<strong>SAC</strong> = Service Accounting Code.'
                ),
            },
        ),
        ('Details', {'fields': ('description',), 'classes': ('collapse',)}),
    )

    @display(description='Price', ordering='price')
    def display_price(self, obj):
        return f'₹ {obj.price:,.2f}'

    @display(
        description='Active',
        ordering='is_active',
        label={
            True: 'success',
            False: 'danger',
        },
    )
    def display_active(self, obj):
        return obj.is_active

    @admin.action(description='Mark selected as active')
    def mark_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Mark selected as inactive')
    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description='Duplicate selected products')
    def duplicate_products(self, request, queryset):
        for product in queryset:
            Product.objects.create(
                user=product.user,
                shortcut=f'{product.shortcut}-COPY'[:20] if product.shortcut else '',
                name=f'{product.name} (Copy)',
                sku='',
                description=product.description,
                price=product.price,
                hsn_code=product.hsn_code,
                gst_rate=product.gst_rate,
                unit=product.unit,
                is_active=product.is_active,
            )

    actions = ['mark_active', 'mark_inactive', 'duplicate_products']
