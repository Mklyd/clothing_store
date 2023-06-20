from rest_framework import serializers

from .models import Product, ImageProduct, ImageCollection, Collection, Menu, Size, Category


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
    menu_item = serializers.StringRelatedField(many=True)
    
    class Meta:
        model = Category
        fields = '__all__'

class MenuSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    categories = serializers.StringRelatedField(many=True, source='menu_item')
    
    class Meta:
        model = Menu
        fields = ['name', 'categories']
        

    def get_name(self, obj):
        return dict(Menu.CHOICES).get(obj.name)


class SizeChoiceField(serializers.MultipleChoiceField):
    def to_representation(self, value):
        return [size.get_name_display() for size in value.all()]


class ProductSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    collection = CollectionSerializer()
    category = CategorySerializer(many=True)
    instructions = serializers.SerializerMethodField()
    size = SizeChoiceField(choices=Size.CHOICES, allow_blank=True, allow_null=True)
    
    class Meta:
        model = Product
        fields = ['id', 'collection', 'product_name','price', 'size', 'delivery_info', 'sku', 'model_parameters' , 'size_on_the_model', 'description', 'images' , 'instructions', 'category', 'quantity', 'date'] 
    
    def get_instructions(self, obj):
        instructions = {
            'details': obj.details,
            'care': obj.care
        }
        return instructions

class HomePageSerializer(serializers.Serializer):
    latest_collections = CollectionSerializer(many=True)  # Сериализатор для последних коллекций
    categories = CategorySerializer(many=True)  # Сериализатор для категорий с продуктами

    class Meta:
        fields = ['latest_collections', 'categories']