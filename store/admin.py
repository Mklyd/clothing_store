from django.contrib import admin
from django.db import models


from .models import Product, ImageProduct, Instruction, Size, Menu, Category, Collection, ImageCollection


admin.site.register(Product)
admin.site.register(ImageProduct)
admin.site.register(Category)
admin.site.register(Collection)
admin.site.register(ImageCollection)
admin.site.register(Menu)

admin.site.site_header = 'Администрирование моего сайта'
admin.site.register(Instruction)
admin.site.register(Size)


