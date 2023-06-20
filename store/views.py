from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter, ModelMultipleChoiceFilter
from rest_framework.response import Response

from django import forms

from .models import Product, Collection, Menu, ImageProduct, Size, Category
from .serializers import ProductSerializer, CollectionSerializer, MenuSerializer, CategorySerializer, HomePageSerializer


class ColorViewSet(viewsets.ViewSet):
    def list(self, request):
        colors = ImageProduct.objects.values_list('name', flat=True).distinct()
        return Response(list(colors))


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer


class ProductFilter(FilterSet):
    color = CharFilter(field_name='images__name', lookup_expr='iexact', label='Цвет')
    size = ModelMultipleChoiceFilter(
        field_name='size',
        queryset=Size.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Product
        fields = ['category', 'collection', 'color', 'size']


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().select_related('collection').prefetch_related( 'category','images')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class =  ProductFilter

    search_fields = ['product_name']
    ordering_fields = ['price', 'date']

    def get_queryset(self):
        queryset = super().get_queryset()

        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price and max_price:
            queryset = queryset.filter(price__range=(min_price, max_price)).order_by('price')
        elif max_price and min_price:
            queryset = queryset.filter(price__range=(max_price, min_price)).order_by('-price')

        return queryset
    

class HomePageViewSet(viewsets.ModelViewSet):
    serializer_class = HomePageSerializer
    def list(self, request):
        # Получение 5 последних элементов коллекций
        collections = Collection.objects.order_by('-id')[:5]
        collection_serializer = CollectionSerializer(collections, many=True)
        
        # Получение 8 категорий с 4 последними продуктами для каждой категории
        categories = Category.objects.all()[:8]
        categories_data = []
        for category in categories:
            products = category.product_set.order_by('-id')[:4]
            product_serializer = ProductSerializer(products, many=True)
            category_data = {
                'category': CategorySerializer(category).data,
                'products': product_serializer.data
            }
            categories_data.append(category_data)
        
        # Получение 4 коллекций с 2 последними продуктами
        collections = Collection.objects.order_by('-id')[:4]
        collections_data = []
        for collection in collections:
            products = collection.product_set.order_by('-id')[:2]
            product_serializer = ProductSerializer(products, many=True)
            collection_data = {
                'collection': CollectionSerializer(collection).data,
                'products': product_serializer.data
            }
            collections_data.append(collection_data)
        
        # Составление и возврат данных в формате JSON
        data = {
            'collections': collection_serializer.data,
            'categories': categories_data,
            'collections_with_products': collections_data
        }
        return Response(data)
