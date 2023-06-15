from rest_framework import serializers

from .models import Product, ImageProduct, ImageCollection, Collection, Menu, Size, Category


class MenuSerializers(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = '__all__'

    def get_name(self, obj):
        return dict(Menu.CHOICES).get(obj.name)
    
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageProduct
        fields = '__all__'

class ImageCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageCollection
        fields = ['id', 'image']

class CollectionSerializer(serializers.ModelSerializer):
    images = ImageCollectionSerializer(many=True)

    class Meta:
        model = Collection
        fields = ['id', 'name', 'description', 'images', 'video_url']


class CategorySerializer(serializers.ModelSerializer):
    menu_item = MenuSerializers()

    class Meta:
        model = Category
        fields = ['id', 'name', 'menu_item']

class SizeChoiceField(serializers.MultipleChoiceField):
    def to_representation(self, value):
        return [size.get_name_display() for size in value.all()]

class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)
    collection = CollectionSerializer()
    category = CategorySerializer()
    instructions = serializers.SerializerMethodField()
    size = SizeChoiceField(choices=Size.CHOICES, allow_blank=True, allow_null=True)
    
    class Meta:
        model = Product
        fields = ['id', 'collection', 'product_name','price', 'size', 'delivery_info', 'sku', 'model_parameters' , 'size_on_the_model', 'description', 'images' , 'instructions', 'category', 'quantity'] 
    
    def get_instructions(self, obj):
        instructions = {
            'details': obj.details,
            'care': obj.care
        }
        return instructions