from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Customer


@admin.register(Customer)
class CustomerAdmin(ModelAdmin):
    list_display = ['name', 'phone', 'email', 'gstin', 'user']
    list_display_links = ['name']
    list_filter = ['user']
    list_filter_submit = True
    search_fields = ['name', 'email', 'phone', 'gstin']
    list_per_page = 25

    fieldsets = (
        (
            'Customer details',
            {
                'fields': ('user', 'name', 'phone', 'email'),
                'description': 'Party details printed on GST tax invoice.',
            },
        ),
        (
            'GST & address',
            {
                'fields': ('gstin', 'address'),
                'description': 'GSTIN = Goods and Services Tax Identification Number (15 characters, optional for B2C).',
            },
        ),
    )
