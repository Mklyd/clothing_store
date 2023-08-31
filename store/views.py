from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import FilterSet, CharFilter, Filter
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from django.db.models import Count

from .models import Product, Collection, Menu, ProductColor, Size, Category, ProductView, Color, Order
from .serializers import ProductSerializer, CollectionSerializer, MenuSerializer, CategorySerializer, HomePageSerializer, RelatedProductSerializer, CollectionNameSerializer, ProductNameSerializer, ProductColorSerializer, OrderSerializer


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
    
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

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
    category_name = CharFilter(field_name='category__category_name', lookup_expr='icontains')
    class Meta:
        model = Product
        fields = {
            'productcolors__size__name': ['exact'],  # Filtering based on size
            'productcolors__color__color_name': ['exact'],  # Filtering based on color
            'product_name': ['icontains'],  # Filtering based on product_name
            'collection__collection_name': ['icontains'],  # Filtering based on collection_name
            'category__menu_item__menu_name': ['exact']
        }
   

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductNameSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product_name', 'description', 'model_parameters', 'details', 'care']
    ordering_fields = ['price', 'date']
    filterset_class = ProductFilter
    

    def get_queryset(self):
        queryset = Product.objects.all()

        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if min_price is not None and max_price is not None:
            queryset = queryset.filter(price__range=(min_price, max_price)).order_by('price')
        elif max_price is not None:
            queryset = queryset.filter(price__lte=max_price).order_by('-price')
        elif min_price is not None:
            queryset = queryset.filter(price__gte=min_price).order_by('price')

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


# shop/views.py

import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from yookassa import Configuration, Payment
from .models import Order, OrderItem, PaymentRecord

# shop/views.py
import random
import string

def generate_order_number():
    # Генерируем случайный номер, состоящий из букв и цифр
    letters_and_digits = string.ascii_uppercase + string.digits
    order_number = ''.join(random.choice(letters_and_digits) for _ in range(10))
    return order_number

# shop/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from yookassa import Configuration, Payment
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Order, OrderItem, Product

class YookassaPaymentCreateAPIView(APIView):
    def post(self, request, format=None):
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None

        product_data_list = request.data.get("products", [])
        order_items = []
        total_amount = 0
        
       # Получение данных о клиенте
        client_data = request.data.get("client_data", {})
        first_name = client_data.get("first_name")
        last_name = client_data.get("last_name")
        email = client_data.get("email")
        phone = client_data.get("phone")
        city = client_data.get("city")
        delivery_method = client_data.get("delivery_method")
        street = client_data.get("street")
        house = client_data.get("house")
        apartment_office = client_data.get("apartment_office")
        postal_code = client_data.get("postal_code")
        courier_comment = client_data.get("courier_comment")
        
        # Создание заказа с автоматическим номером и суммой
        order_number = generate_order_number()
        if user is None:
            order = Order.objects.create(
                status='created',
                amount=total_amount,
                order_number=order_number,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                city=city,
                delivery_method=delivery_method,
                street=street,
                house=house,
                apartment_office=apartment_office,
                postal_code=postal_code,
                courier_comment=courier_comment
            )
        else:
            order = Order.objects.create(
                user=user,
                status='created',
                amount=total_amount,
                order_number=order_number,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                city=city,
                delivery_method=delivery_method,
                street=street,
                house=house,
                apartment_office=apartment_office,
                postal_code=postal_code,
                courier_comment=courier_comment
            )


       # Обработка данных о продуктах
        for product_data in product_data_list:  
            product_id = product_data.get("product_id")
            quantity = product_data.get("quantity")
            size_id = product_data.get("size_id")
            color_id = product_data.get("color_id")
            price = product_data.get("price")

            if product_id is None or quantity is None:
                return Response({"error": "Некорректные данные продукта"}, status=400)

            try:
                product = Product.objects.get(pk=product_id)
                product_amount = price * quantity
                total_amount += product_amount
                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                )

                if color_id:
                    color = Color.objects.get(pk=color_id)
                    order_item.colors.add(color)

                if size_id:
                    size = Size.objects.get(pk=size_id)
                    order_item.sizes.add(size)

                order_item.save()
                order_items.append(order_item)

            except Product.DoesNotExist:
                return Response({"error": "Продукт с ID {} не найден".format(product_id)}, status=400)

        
        order.amount = total_amount
        order.save()
        

        Configuration.account_id = settings.YOOKASSA_ACCOUNT_ID
        Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

        payment = Payment.create({
            "amount": {
                "value": str(total_amount),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://www.example.com/return_url"
            },
            "description": "Оплата заказа №" + str(order.id)
        })
        # Получение данных о платеже
        payment_status = payment.status
        payment_amount = payment.amount.value
        # Сохранение данных о платеже в модели Payment
        payment_record = PaymentRecord.objects.create(
            order=order,
            amount=payment_amount,
            status=payment_status
        )
        payment_record.save()
        # После создания заказа отправляем уведомление
        subject = 'New Order Notification'
        message = f'A new order has been placed. Order ID: {order.id}'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [admin_email for _, admin_email in settings.ADMINS]

        # Отправка письма с использованием шаблона
        email_html_message = render_to_string('email_templates/new_order_notification.html', {'order': order})
        try:
            send_mail(subject, message, from_email, recipient_list, html_message=email_html_message)
            print("Email sent successfully")
        except Exception as e:
            print("Email sending failed:")
        confirmation_url = payment.confirmation.confirmation_url

        return Response({"confirmation_url": confirmation_url})
    

""" import base64
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import PaymentRecord
from .serializers import PaymentSerializer
def confirm_payment(payment_id):
    shop_id = 'your_shop_id'
    secret_key = 'your_secret_key'
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{shop_id}:{secret_key}".encode()).decode()}'
    }
    response = requests.post(f'https://api.yookassa.ru/v3/payments/{payment_id}/capture', headers=headers)

    if response.status_code == 200:
        payment = Payment.objects.get(payment_id=payment_id)
        payment.status = 'confirmed'
        payment.save()
        return True
    else:
        return False

def cancel_payment(payment_id):
    shop_id = settings.YOOKASSA_ACCOUNT_ID
    secret_key = settings.YOOKASSA_SECRET_KEY
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{shop_id}:{secret_key}".encode()).decode()}'
    }
    response = requests.post(f'https://api.yookassa.ru/v3/payments/{payment_id}/cancel', headers=headers)

    if response.status_code == 200:
        payment = Payment.objects.get(payment_id=payment_id)
        payment.status = 'cancelled'
        payment.save()
        return True
    else:
        return False

class PaymentConfirmationView(APIView):
    def post(self, request, *args, **kwargs):
        payment_id = request.data.get('payment_id')
        
        if payment_id:
            if confirm_payment(payment_id):
                return Response({'message': 'Payment confirmed successfully.'})
            else:
                return Response({'error': 'Failed to confirm payment.'}, status=400)
        else:
            return Response({'error': 'Payment ID is required.'}, status=400)

class PaymentCancellationView(APIView):
    def post(self, request, *args, **kwargs):
        payment_id = request.data.get('payment_id')
        
        if payment_id:
            if cancel_payment(payment_id):
                return Response({'message': 'Payment cancelled successfully.'})
            else:
                return Response({'error': 'Failed to cancel payment.'}, status=400)
        else:
            return Response({'error': 'Payment ID is required.'}, status=400)
 """