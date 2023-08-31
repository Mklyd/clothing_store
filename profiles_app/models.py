from django.db import models
from django.conf import settings
from store.models import Product


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    first_name = models.CharField(max_length=255, verbose_name='Имя', blank=True, null=True)
    last_name = models.CharField(max_length=255, verbose_name='Фамилия', blank=True, null=True)
    clothing_size = models.CharField('Размер одежды', max_length=10, blank=True, null=True)
    gender = models.CharField('Пол', max_length=10, blank=True, null=True)
    birthday = models.DateField('Дата рождения', blank=True, null=True)

    city = models.CharField(max_length=255, verbose_name='Населённый пункт', blank=True, null=True)
    street = models.CharField(max_length=255, verbose_name='Улица', blank=True, null=True)
    house = models.CharField(max_length=10, verbose_name='Дом',  blank=True,null=True)
    apartment_office = models.CharField(max_length=10, verbose_name='Квартира/офис', blank=True, null=True)
    postal_code = models.CharField(max_length=10, verbose_name='Индекс', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.user.username}"

class FavoriteProducts(models.Model):
    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product.product_name} - {self.user_profile.name} {self.user_profile.surname}"

class CardProducts(models.Model):
    user_profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    current = models.PositiveIntegerField('current', blank=True, null=True)
    size = models.CharField("size", max_length=10, blank=True, null=True)
    color = models.CharField("color", max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.product.product_name} - {self.user_profile.name} {self.user_profile.surname}"
     