from django.templatetags.static import static


def environment_callback(request):
    return 'Development', 'info'

"STYLES": [
    lambda request: static("admin/css/invoiceflow_admin.css"),
]

UNFOLD = {
    'SITE_TITLE': 'InvoiceFlow Admin',
    'SITE_HEADER': 'InvoiceFlow',
    'SITE_SUBHEADER': 'GST Invoicing & Billing',
    'SITE_URL': 'http://localhost:5173/dashboard',
    'SITE_SYMBOL': 'receipt_long',
    'SHOW_HISTORY': True,
    'SHOW_VIEW_ON_SITE': False,
    'BORDER_RADIUS': '12px',
    'DASHBOARD_CALLBACK': 'config.dashboard.dashboard_callback',
    'ENVIRONMENT': environment_callback,
    'STYLES': [
        lambda request: static('admin/css/invoiceflow_admin.css'),
    ],
    'COLORS': {
        'base': {
            '50': 'oklch(98.5% 0.002 272)',
            '100': 'oklch(96% 0.004 272)',
            '200': 'oklch(91% 0.008 272)',
            '300': 'oklch(84% 0.012 272)',
            '400': 'oklch(70% 0.02 272)',
            '500': 'oklch(55% 0.025 272)',
            '600': 'oklch(45% 0.03 272)',
            '700': 'oklch(37% 0.03 272)',
            '800': 'oklch(28% 0.025 272)',
            '900': 'oklch(22% 0.02 272)',
            '950': 'oklch(16% 0.015 272)',
        },
        'primary': {
            '50': 'oklch(96.2% .018 272.314)',
            '100': 'oklch(93% .035 272)',
            '200': 'oklch(87% .065 272)',
            '300': 'oklch(78% .12 272)',
            '400': 'oklch(67% .19 272)',
            '500': 'oklch(58% .24 272)',
            '600': 'oklch(51% .26 272)',
            '700': 'oklch(45% .24 272)',
            '800': 'oklch(39% .2 272)',
            '900': 'oklch(33% .16 272)',
            '950': 'oklch(25% .12 272)',
        },
    },
    'LOGIN': {
        'redirect_after': lambda request: '/admin/',
    },
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': True,
        'navigation': [
            {
                'title': 'InvoiceFlow',
                'items': [
                    {
                        'title': 'Admin home',
                        'icon': 'home',
                        'link': '/admin/',
                    },
                    {
                        'title': 'Frontend dashboard',
                        'icon': 'dashboard',
                        'link': 'http://localhost:5173/dashboard',
                    },
                    {
                        'title': 'Create invoice',
                        'icon': 'add_circle',
                        'link': 'http://localhost:5173/invoices/new',
                    },
                ],
            },
            {
                'title': 'Manage',
                'separator': True,
                'collapsible': True,
                'items': [
                    {
                        'title': 'Invoices',
                        'icon': 'description',
                        'link': '/admin/invoices/invoice/',
                    },
                    {
                        'title': 'Customers',
                        'icon': 'groups',
                        'link': '/admin/customers/customer/',
                    },
                    {
                        'title': 'Products',
                        'icon': 'inventory_2',
                        'link': '/admin/products/product/',
                    },
                    {
                        'title': 'Users & auth',
                        'icon': 'manage_accounts',
                        'link': '/admin/auth/user/',
                    },
                ],
            },
        ],
    },
}
