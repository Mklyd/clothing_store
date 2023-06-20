from django.db import models
from django.utils.safestring import mark_safe


from colorfield.fields import ColorField


class Menu(models.Model):
    CHOICES = CHOICES = (
        ('women', 'Женщинам'),
        ('men', 'Мужчинам'),
        ('hajj', 'Для Хаджа и Умры'),
        ('buyers', 'Покупателям'),
    )
    name = models.CharField( max_length=255, choices=CHOICES, unique=True, verbose_name='Имя пункта меню')
    show_menu = models.BooleanField(default=True, verbose_name='Включить в меню')

    class Meta:
        verbose_name_plural = 'Меню'
        verbose_name = 'Меню'

    def __str__(self):
        return self.get_name_display()


class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя категории')
    menu_item = models.ManyToManyField('Menu', verbose_name='Название элемента меню', related_name='menu_item')


    class Meta:
        verbose_name_plural = 'Категории'
        verbose_name = 'Категория'

    def __str__(self) -> str:
        return self.name


class ImageCollection(models.Model):
    image = models.ImageField(upload_to='products', blank=True, verbose_name='Изображение коллекции')

    class Meta:
        verbose_name_plural = 'Изображение коллекции'
        verbose_name = 'Изображение коллекции'

    def __str__(self):
        return self.image.url


class Collection(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название коллекции')
    description = models.TextField(blank=True,verbose_name='Описание коллекции')
    images = models.ManyToManyField('ImageCollection', verbose_name='Изображание коллекции')
    video_url = models.URLField()


    class Meta:
        verbose_name_plural = 'Коллекции'
        verbose_name = 'Коллекция'

    def __str__(self) -> str:
        return self.name



class ImageProduct(models.Model):
    name = models.CharField(max_length=255, verbose_name='Цвет', null=True)
    color = ColorField(format="hexa")
    image = models.ImageField(upload_to='products', blank=False, verbose_name='Изображение товара')

    class Meta:
        verbose_name_plural = 'Изображение товаров'
        verbose_name = 'Изображение товара'

    def __str__(self):
        return self.image.url

    def image_tag(self):
        if self.image:
            return mark_safe('<img src="%s" style="width: 105px; height:105px;" />' % self.image.url)
        else:
            return 'No Image Found'

    image_tag.short_description = 'Image'


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

    name = models.CharField( max_length=255, choices=CHOICES, unique=True, verbose_name='Размер')


    class Meta:
        verbose_name_plural = 'Размеры одежды'
        verbose_name = 'Размер одежды'


    def __str__(self):
        return self.name


class Product(models.Model):
    collection = models.ForeignKey('Collection', verbose_name='Название коллекции', blank=False, on_delete=models.CASCADE, null=True )
    product_name = models.CharField(max_length=255, blank=False, verbose_name='Название товара')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', blank=False)
    size = models.ManyToManyField('Size', verbose_name='Размер одежды')
    delivery_info = models.TextField(verbose_name='Информация о доставке')
    sku = models.CharField(max_length=50, verbose_name='Артикул', blank=False)
    model_parameters = models.CharField(max_length=255, verbose_name='Параметры модели')
    size_on_the_model = models.CharField(max_length=10, verbose_name='размер на модели')
    description = models.TextField(verbose_name='Описание', blank=False)
    images = models.ManyToManyField('ImageProduct', verbose_name='Изображание товара')
    details = models.TextField(verbose_name='Состав ткани', null=True)
    care = models.TextField(verbose_name='Уход', null=True)
    category = models.ManyToManyField('Category', null=True, verbose_name='Категория')
    quantity = models.PositiveIntegerField(null=True, verbose_name='Количество товара')
    date = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True, null=True)


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