from django.core.mail import send_mail
from django.db.models import Count, Q, Sum
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from customers.models import Customer

from .models import Invoice, InvoiceItem
from .serializers import InvoiceCreateSerializer, InvoiceSerializer


def _generate_pdf(invoice):
    from .pdf import generate_invoice_pdf
    return generate_invoice_pdf(invoice)


class InvoiceViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        qs = Invoice.objects.filter(user=self.request.user).select_related('customer').prefetch_related('items')
        search = self.request.query_params.get('search', '').strip()
        status_filter = self.request.query_params.get('status', '').strip()
        if search:
            qs = qs.filter(
                Q(invoice_number__icontains=search)
                | Q(customer__name__icontains=search)
            )
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return InvoiceCreateSerializer
        return InvoiceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        invoice = serializer.instance
        return Response(
            InvoiceSerializer(invoice, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(InvoiceSerializer(instance, context={'request': request}).data)

    def retrieve(self, request, *args, **kwargs):
        invoice = self.get_object()
        if invoice.status == Invoice.STATUS_CONFIRMED:
            _generate_pdf(invoice)
            invoice.refresh_from_db()
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        user = request.user
        invoices = Invoice.objects.filter(user=user)
        confirmed = invoices.filter(status=Invoice.STATUS_CONFIRMED)
        drafts = invoices.filter(status=Invoice.STATUS_DRAFT)

        customer_sales = (
            invoices.values('customer_id', 'customer__name')
            .annotate(
                invoice_count=Count('id'),
                total_sales=Sum('total'),
            )
            .order_by('-total_sales')[:8]
        )

        top_products = (
            InvoiceItem.objects.filter(invoice__user=user)
            .values('item_name')
            .annotate(
                qty_sold=Sum('quantity'),
                revenue=Sum('total'),
            )
            .order_by('-qty_sold')[:8]
        )

        products_sold = InvoiceItem.objects.filter(invoice__user=user).aggregate(
            total_qty=Sum('quantity'),
            line_count=Count('id'),
        )

        return Response({
            'total_invoices': invoices.count(),
            'total_revenue': confirmed.aggregate(total=Sum('total'))['total'] or 0,
            'draft_count': drafts.count(),
            'confirmed_count': confirmed.count(),
            'draft_total': drafts.aggregate(total=Sum('total'))['total'] or 0,
            'total_customers': Customer.objects.filter(user=user).count(),
            'total_products_sold': float(products_sold['total_qty'] or 0),
            'total_line_items': products_sold['line_count'] or 0,
            'customer_sales': [
                {
                    'customer_id': row['customer_id'],
                    'name': row['customer__name'],
                    'invoice_count': row['invoice_count'],
                    'total_sales': row['total_sales'] or 0,
                }
                for row in customer_sales
            ],
            'top_products': [
                {
                    'item_name': row['item_name'],
                    'qty_sold': float(row['qty_sold'] or 0),
                    'revenue': row['revenue'] or 0,
                }
                for row in top_products
            ],
            'recent_invoices': InvoiceSerializer(
                invoices[:5], many=True, context={'request': request}
            ).data,
        })

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = Invoice.STATUS_CONFIRMED
        invoice.save(update_fields=['status', 'updated_at'])
        _generate_pdf(invoice)
        return Response(InvoiceSerializer(invoice, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        original = self.get_object()
        new_invoice = Invoice.objects.create(
            user=request.user,
            customer=original.customer,
            invoice_number=Invoice.generate_invoice_number(request.user),
            date=original.date,
            due_date=original.due_date,
            discount=original.discount,
            status=Invoice.STATUS_DRAFT,
            subtotal=original.subtotal,
            tax=original.tax,
            total=original.total,
        )
        for item in original.items.all():
            new_invoice.items.create(
                item_name=item.item_name,
                quantity=item.quantity,
                price=item.price,
            )
        new_invoice.recalculate_totals()
        return Response(
            InvoiceSerializer(new_invoice, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=['post'])
    def email(self, request, pk=None):
        invoice = self.get_object()
        if not invoice.pdf_url:
            _generate_pdf(invoice)
        customer_email = invoice.customer.email
        if not customer_email:
            return Response(
                {'detail': 'Customer has no email address.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        send_mail(
            subject=f'Invoice {invoice.invoice_number}',
            message=f'Please find attached invoice {invoice.invoice_number} for {invoice.total}.',
            from_email=None,
            recipient_list=[customer_email],
            fail_silently=False,
        )
        return Response({'detail': f'Invoice emailed to {customer_email}.'})
