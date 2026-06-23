from django.db.models import Q
from rest_framework import viewsets

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs = Product.objects.filter(user=self.request.user)
        active = self.request.query_params.get('active')
        search = self.request.query_params.get('search', '').strip()
        shortcut = self.request.query_params.get('shortcut', '').strip()
        if active == 'true':
            qs = qs.filter(is_active=True)
        if shortcut:
            qs = qs.filter(shortcut__iexact=shortcut)
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(sku__icontains=search)
                | Q(shortcut__icontains=search)
            )
        return qs.distinct()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
