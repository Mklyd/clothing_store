from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter, ModelMultipleChoiceFilter, MultipleChoiceFilter
from rest_framework.response import Response

from django import forms

from .models import Product, Collection, Menu, ImageProduct, Size
from .serializers import ProductSerializer, CollectionSerializer, MenuSerializers


class ColorViewSet(viewsets.ViewSet):
    def list(self, request):
        colors = ImageProduct.objects.values_list('name', flat=True).distinct()
        return Response(list(colors))


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all().prefetch_related()
    serializer_class = MenuSerializers


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer


class ProductFilter(FilterSet):
    color = CharFilter(field_name='images__name', lookup_expr='icontains', label='Цвет')
    size = ModelMultipleChoiceFilter(
        field_name='size',
        queryset=Size.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Product
        fields = ['category', 'collection', 'color', 'size']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('collection', 'category').prefetch_related( 'images')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class =  ProductFilter

    search_fields = ['product_name']
    ordering_fields = ['price']

    def get_queryset(self):
        queryset = super().get_queryset()

        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price and max_price:
            queryset = queryset.filter(price__range=(min_price, max_price)).order_by('price')
        elif max_price and min_price:
            queryset = queryset.filter(price__range=(max_price, min_price)).order_by('-price')

        return queryset