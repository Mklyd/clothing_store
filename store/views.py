from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter, Filter
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from django import forms
from rest_framework.decorators import action
from django.db.models import Count

from .models import Product, Collection, Menu, ProductColor, Size, Category, ProductView, Color
from .serializers import ProductSerializer, CollectionSerializer, MenuSerializer, CategorySerializer, HomePageSerializer, RelatedProductSerializer, CollectionNameSerializer, ProductNameSerializer, ProductColorSerializer
class MyCustomPagination(PageNumberPagination):
    page_size = 9  # Количество элементов на одной странице
    page_size_query_param = 'page_size'  # Параметр запроса для указания количества элементов на странице

class ColorAndSizesViewSet(viewsets.ViewSet):
    def list(self, request):
        colors = Color.objects.values('id', 'color_hex', 'color_name').distinct()
        size = Size.objects.values('id', 'name').distinct()
        data = {
            'colors': list(colors),
            'sizes': list(size)
        }
        return Response(data)

class ProductColorViewSet(viewsets.ModelViewSet):
    serializer_class = ProductColorSerializer
    queryset = ProductColor.objects.all()

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all().prefetch_related('images')
    serializer_class = CollectionSerializer
    
from urllib.parse import unquote

class SizeFilter(Filter):
    def filter(self, qs, value):
        if value:
            sizes = unquote(value).split(';')
            return qs.filter(**{f"{self.field_name}__in": sizes})
        return qs

class ColorFilter(Filter):
    def filter(self, qs, value):
        if value:
            colors = unquote(value).split(';')
            return qs.filter(**{f"{self.field_name}__in": colors})
        return qs

class ProductFilter(FilterSet):
    color = ColorFilter(field_name='colors__color_hex', lookup_expr='iexact', label='Цвет')
    size = SizeFilter(field_name='colors__size__name', lookup_expr='in')
    menu = CharFilter(method='filter_by_menu')
    product_name = CharFilter(field_name='product_name', lookup_expr='icontains', label='Имя продукта')

    class Meta:
        model = Product
        fields = ['category', 'collection', 'color', 'size', 'menu', 'product_name']

    def filter_by_menu(self, queryset, name, value):
        return queryset.filter(category__menu_item__menu_name=value).order_by('category__menu_item')

    def filter_by_name(self, queryset, name, value):
        return queryset.filter(product_name__icontains=value)


        
class ProductViewSet(viewsets.ModelViewSet):
    pagination_class = MyCustomPagination
    queryset = Product.objects.all().select_related('collection').prefetch_related('category', 'colors')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    ordering_fields = ['price', 'date', 'views']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())  # Фильтрация данных

        product_name = self.request.query_params.get('product_name')
        if product_name:
            queryset = queryset.filter(product_name__icontains=product_name)

        all_product = Product.objects.all().prefetch_related('colors')
        all_product_serializer = ProductNameSerializer(all_product, many=True, context={'request': request})
        
        return Response(all_product_serializer.data)

    def get_queryset(self):
        queryset = super().get_queryset()

        menu_name = self.request.query_params.get('menu_name')

        if menu_name:
            # Фильтрация продуктов по принадлежности категорий к указанному элементу меню
            queryset = queryset.filter(category__menu_item__name=menu_name)

        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price and max_price:
            queryset = queryset.filter(price__range=(min_price, max_price)).order_by('price')
        elif max_price and min_price:
            queryset = queryset.filter(price__range=(max_price, min_price)).order_by('-price')

        ordering = self.request.query_params.get('ordering')
        if ordering == 'views_count':
            queryset = queryset.annotate(views_count=Count('views__ip')).order_by('-views_count')

        return queryset
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        recommendations = Product.objects.filter(
            category__in=instance.category.all(),
            price__gte=instance.price
        ).exclude(id=instance.id)
    
        recommendations_serializer = RelatedProductSerializer(recommendations, many=True, context={'request': request})
        instance_serializer = ProductSerializer(instance, context={'request': request})

        instance_data = instance_serializer.data
        instance_data['recommendations'] =  recommendations_serializer.data

        return Response(instance_data)
        """ # Получение IP-адреса пользователя
        ip_address = self.request.META.get('HTTP_X_FORWARDED_FOR') or self.request.META.get('REMOTE_ADDR')
        # Проверка, просмотрел ли пользователь товар ранее
        product_view = ProductView.objects.filter(product=instance, ip=ip_address).first()
        if not product_view:
            # Создание объекта ProductView при первом просмотре товара пользователем с данным IP-адресом
            product_view = ProductView.objects.create(product=instance, ip=ip_address)
        
        # Увеличение счетчика просмотров товара
        instance.views.add(product_view)
        serializer = self.get_serializer(instance)

        return Response(serializer.data) """
    

class HomePageViewSet(viewsets.ModelViewSet):
    serializer_class = HomePageSerializer
    def list(self, request):
        all_collections = Collection.objects.all().prefetch_related('images')
        all_collection_serializer = CollectionNameSerializer(all_collections, many=True, context={'request': request})

        # Получение 5 последних элементов коллекций
        collections = Collection.objects.order_by('-id')[:5]
        collection_serializer = CollectionNameSerializer(collections, many=True, context={'request': request})
        
        # Получение 8 категорий с 4 последними продуктами для каждой категории
        categories = Category.objects.all()[:8]
        categories_data = []
        for category in categories:
            products = category.product_set.order_by('-id')[:4]
            product_serializer = ProductNameSerializer(products, many=True, context={'request': request})
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
            product_serializer = ProductNameSerializer(products, many=True, context={'request': request})
            collection_data = {
                'collection': CollectionNameSerializer(collection, context={'request': request}).data,
                'products': product_serializer.data
            }
            collections_data.append(collection_data)
        
        # Составление и возврат данных в формате JSON
        data = {
            'all_collections': all_collection_serializer.data,
            'collections': collection_serializer.data,
            'categories': categories_data,
            'collections_with_products': collections_data
        }
        return Response(data)


