from django.contrib import admin

from django import forms
from django.forms.widgets import CheckboxSelectMultiple

from .models import Product, ProductImage, Menu, Category, Collection, ImageCollection, Size, ProductColor, Color


admin.site.register(ProductImage)
admin.site.register(ProductColor)
admin.site.register(Category)
admin.site.register(Collection)
admin.site.register(ImageCollection)
admin.site.register(Menu)
admin.site.register(Color)

class ProductColorAdminForm(forms.ModelForm):
    size = forms.ModelMultipleChoiceField(queryset=Size.objects.all(), widget=CheckboxSelectMultiple, required=False)
    
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
    list_display = ['collection','product_name', 'quantity', 'price']
    list_filter = ['category', 'collection']
    search_fields = ('product_name__startswith', )
    exclude = ['views', 'related_products']
    filter_vertical = ('colors', 'category')
    inlines = [ProductColorInline]
    form = ProductAdminForm
    


admin.site.site_header = 'Администрирование сайта'


