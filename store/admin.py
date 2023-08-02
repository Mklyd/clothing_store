from django.contrib import admin


from .models import Product, ProductImage, Menu, Category, Collection, ImageCollection, Size, ProductColor, Color


admin.site.register(ProductImage)
admin.site.register(ProductColor)
admin.site.register(Category)
admin.site.register(Collection)
admin.site.register(ImageCollection)
admin.site.register(Menu)
admin.site.register(Color)


class ProductColorInline(admin.TabularInline):
    model = ProductColor
    extra = 1
    filter_horizontal = ('size', )

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['collection','product_name', 'quantity', 'price']
    list_filter = ['category', 'collection']
    search_fields = ('product_name__startswith', )
    exclude = ['views']
    filter_vertical = ('colors', 'category')
    inlines = [ProductColorInline]


admin.site.site_header = 'Администрирование сайта'


