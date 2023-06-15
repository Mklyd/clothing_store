from django.contrib import admin
from django.db import models
from django import forms


from .models import Product, ImageProduct, Menu, Category, Collection, ImageCollection, Size


admin.site.register(ImageProduct)
admin.site.register(Category)
admin.site.register(Collection)
admin.site.register(ImageCollection)
admin.site.register(Menu)
admin.site.register(Size)

admin.site.register(Product)

admin.site.site_header = 'Администрирование моего сайта'


