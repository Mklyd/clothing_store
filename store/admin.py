from django.contrib import admin

from django import forms
from django.forms.widgets import CheckboxSelectMultiple

from .models import Product, ProductImage, Menu, Category, Collection, ImageCollection, Size, ProductColor, Color, Order, OrderItem, Payment


admin.site.register(ProductImage)

admin.site.register(Payment)

admin.site.register(ProductColor)
admin.site.register(Category)
admin.site.register(Collection)
admin.site.register(ImageCollection)
admin.site.register(Menu)
admin.site.register(Color)

class ProductColorAdminForm(forms.ModelForm):
    
    class Meta:
        model = ProductColor
        fields = '__all__'

class ProductColorInline(admin.TabularInline):
    model = ProductColor
    filter_horizontal = ('images',)
    extra = 1
    form = ProductColorAdminForm



@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


class ProductAdminForm(forms.ModelForm):
    Связанные_товары = forms.ModelMultipleChoiceField(queryset=Product.objects.all(), widget=CheckboxSelectMultiple, required=False)
    
    class Meta:
        model = Product
        fields = '__all__'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, forms.ModelForm):
    list_display = ['id', 'collection','product_name', 'quantity', 'price']
    list_filter = ['category', 'collection']
    search_fields = ('product_name__startswith', )
    exclude = ['views', 'related_products']
    filter_vertical = ('colors', 'category')
    inlines = [ProductColorInline]
    form = ProductAdminForm
    

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'colors', 'sizes', 'quantity')
    can_delete =False
    
class OrderAdmin(admin.ModelAdmin):
    readonly_fields = ('order_number', 'user', 'created_at', 'amount')
    inlines = [OrderItemInline]  # Добавляем inlines

    list_display = ('order_number', 'user', 'created_at', 'status', 'amount')

admin.site.register(Order, OrderAdmin)

admin.site.site_header = 'Администрирование сайта'


