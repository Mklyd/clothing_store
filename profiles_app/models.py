from django.db import models
from django.conf import settings
from store.models import Product


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    name = models.CharField("name", max_length=500)
    surname = models.CharField("surname", max_length=500)
    clothing_size = models.CharField('clothing_size', max_length=10, blank=True, null=True)
    gender = models.CharField('gender', max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.name} {self.surname} {self.user.username}"

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
     