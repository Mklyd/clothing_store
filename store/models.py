from django.db import models
from django.utils.safestring import mark_safe


class Menu(models.Model):
    CHOICES = (
        ('women', 'Женщинам'),
        ('men', 'Мужчинам'),
        ('hajj', 'Для Хаджа и Умры'),
        ('buyers', 'Покупателям'),
    )
    menu_name = models.CharField( max_length=255, choices=CHOICES, unique=True, verbose_name='Имя пункта меню')
    show_menu = models.BooleanField(default=True, verbose_name='Включить в меню')
 

    class Meta:
        verbose_name_plural = 'Меню'
        verbose_name = 'Меню'

    def __str__(self):
        return self.get_menu_name_display()


class Category(models.Model):
    category_name = models.CharField(max_length=255, verbose_name='Имя категории')
    menu_item = models.ManyToManyField('Menu', verbose_name='Название элемента меню', related_name='menu_item')

    class Meta:
        verbose_name_plural = 'Категории'
        verbose_name = 'Категория'

    def __str__(self) -> str:
        return self.category_name


class ImageCollection(models.Model):
    image_url = models.ImageField(upload_to='products', blank=True, verbose_name='Изображение коллекции')

    class Meta:
        verbose_name_plural = 'Изображение коллекции'
        verbose_name = 'Изображение коллекции'

    def __str__(self):
        return self.image_url.url


class Collection(models.Model):
    collection_name = models.CharField(max_length=255, verbose_name='Название коллекции')
    description = models.TextField(blank=True,verbose_name='Описание коллекции')
    images = models.ManyToManyField('ImageCollection', verbose_name='Изображание коллекции')
    video_url = models.URLField()


    class Meta:
        verbose_name_plural = 'Коллекции'
        verbose_name = 'Коллекция'

    def __str__(self) -> str:
        return self.collection_name


class ProductImage(models.Model):
    image_url = models.ImageField(upload_to='products', blank=False, verbose_name='Изображение товара')
    class Meta:
        verbose_name_plural = 'Изображение товаров'
        verbose_name = 'Изображение товара'

    def __str__(self):
        return self.image_url.url

    def image_tag(self):
        if self.image_url:
            return mark_safe('<img src="%s" style="width: 105px; height:105px;" />' % self.image_url.url)
        else:
            return 'No Image Found'

    image_tag.short_description = 'Image'


class Color(models.Model):
    COLOR_CHOICES = [
        ('#000000', 'Чёрный'),
        ('#FFFFFF', 'Белый'),
        ('#FF0000', 'Красный'),
        ('#00FF00', 'Зелёный'),
        ('#0000FF', 'Синий'),
        ('#FFFF00', 'Жёлтый'),
        ('#F5F5DC', 'Бежевый'),
        ('#00FFFF', 'Голубой'),
        ('#FFA500', 'Оранжевый'),
        ('#D2691E', 'Кофейный'),
        ('#FFC0CB', 'Розовый'),
        ('#808080', 'Серый'),
        ('#FFD700', 'Сиреневый'),
        ('#F3F3FA', 'Молочный'),
        ('#008080', 'Бирюзовый'),
        ('#808000', 'Оливковый'),
        ('#A52A2A', 'Коричневый'),
        ('#800080', 'Фиолетовый'),
        ('#D3D3D3', 'Металлик'),
    ]

    color_name = models.CharField(max_length=255, verbose_name='Название цвета', null=True)
    color_hex = models.CharField(choices=COLOR_CHOICES, verbose_name='Цвет', max_length=255)

    def __str__(self):
        return self.color_name


class Size(models.Model):
    CHOICES = (
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL'),
        ('3XL', '3XL'),
        ('4XL', '4XL')
    )

    name = models.CharField(max_length=255, choices=CHOICES,  verbose_name='Размер')

    class Meta:
        verbose_name_plural = 'Размеры одежды'
        verbose_name = 'Размер одежды'
 
    def __str__(self):
        return self.name

class ProductView(models.Model):
    ip = models.GenericIPAddressField()


class Product(models.Model):
    collection = models.ForeignKey('Collection', verbose_name='Коллекция', blank=False, on_delete=models.CASCADE, null=True )
    product_name = models.CharField(max_length=255, blank=False, verbose_name='Название товара')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', blank=False)
    delivery_info = models.TextField(verbose_name='Информация о доставке')
    sku = models.CharField(max_length=50, verbose_name='Артикул', blank=False)
    model_parameters = models.CharField(max_length=255, verbose_name='Параметры модели')
    size_on_the_model = models.CharField(max_length=10, verbose_name='Размер на модели', blank=True)
    description = models.TextField(verbose_name='Описание', blank=False)
    colors = models.ManyToManyField(Color, through='ProductColor', related_name='products')
    details = models.TextField(verbose_name='Состав ткани', null=True)
    care = models.TextField(verbose_name='Уход', null=True)
    category = models.ManyToManyField('Category', null=True, verbose_name='Категория')
    quantity = models.PositiveIntegerField(null=True, verbose_name='Количество товара')
    date = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True, null=True)
    related_products = models.ManyToManyField('self', verbose_name='Связанные товары', blank=True)
    views = models.ManyToManyField('ProductView', verbose_name='Просмотры продукта')


    class Meta:
        verbose_name_plural = 'Товары'
        verbose_name = 'Товар'

    def __str__(self) -> str:
        return self.product_name

    def delete(self, *args, **kwargs):
            # Delete associated images from the filesystem
            for image in self.images.all():
                image.image.delete()

            # Call the superclass delete() method to complete the deletion process
            super().delete(*args, **kwargs)


class ProductColor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='productcolors')
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    images = models.ManyToManyField('ProductImage', verbose_name='Изображения товара')
    size = models.ForeignKey(Size, on_delete=models.PROTECT, null=True)
    quantity = models.PositiveIntegerField(null=True, verbose_name='Количество товара')

    class Meta:
        verbose_name_plural = 'Изображение и цвет товаров'
        verbose_name = 'Изображение и цвет товара'


    def __str__(self):
        return self.color.color_name
    
    def image_tag(self):
        if self.image:
            return mark_safe('<img src="%s" style="width: 105px; height:105px;" />' % self.image.url)
        else:
            return 'No Image Found'

    image_tag.short_description = 'Image'

from profiles_app.models import Profile

class Order(models.Model):
    CHOICES_ORDER = (
        ('Paid', 'Оплачено'),
        ('Being assembled by the seller', 'В сборке у продавца'),
        ('Shipped', 'Передано в доставку'),
        ('Handed over to the courier', 'Передано курьеру '),
        ('Awaiting pickup', 'Ожидает в пункте выдачи'),
        ('Received', 'Получено'),
    )

    order_number = models.CharField(max_length=10 ,unique=True, editable=False, null=True)
    payment_record = models.OneToOneField('PaymentRecord', on_delete=models.CASCADE, related_name='order_record_order', null=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    products = models.ManyToManyField(Product, through='OrderItem')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, choices=CHOICES_ORDER, default='created')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Данные клиента
    first_name = models.CharField(max_length=255, verbose_name='Имя', null=True)
    last_name = models.CharField(max_length=255, verbose_name='Фамилия', null=True)
    email = models.EmailField(verbose_name='Email', null=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон', null=True, blank=True)
    city = models.CharField(max_length=255, verbose_name='Населённый пункт', null=True)
    delivery_method = models.CharField(max_length=255, verbose_name='Способ доставки', null=True)
    street = models.CharField(max_length=255, verbose_name='Улица', null=True)
    house = models.CharField(max_length=10, verbose_name='Дом', null=True)
    apartment_office = models.CharField(max_length=10, verbose_name='Квартира/офис', null=True)
    postal_code = models.CharField(max_length=10, verbose_name='Индекс', null=True)
    courier_comment = models.TextField(verbose_name='Комментарий для курьера', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Заказы'
        verbose_name = 'Заказ'


    def __str__(self):
        return f"{self.order_number} - {self.user}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    colors = models.ManyToManyField(Color, verbose_name='Цвета', blank=True)
    sizes = models.ManyToManyField(Size, verbose_name='Размеры', blank=True)


    def subtotal(self):
        return self.product.price * self.quantity

class PaymentRecord(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='payment_record_order')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')])
    payment_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Платежи'
        verbose_name = 'Платеж'

    def __str__(self) -> str:
        return str(self.order)