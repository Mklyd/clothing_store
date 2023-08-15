from rest_framework import serializers

from .models import Product, ProductImage, ImageCollection, Collection, Menu, Size, Category, ProductColor, Color, Order



class ImageCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageCollection
        fields = ['id', 'image_url']
    def get_image(self, obj):
        if 'request' in self.context:
            request = self.context['request']
            image_url = obj.image_url.url
            return request.build_absolute_uri(image_url)
        return None

class CollectionSerializer(serializers.ModelSerializer):
    images = ImageCollectionSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'collection_name', 'description', 'images', 'video_url']
    

class CollectionNameSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        first_image = obj.images.first()
        first_image_serializer = ImageProductSerializer(first_image, context={'request': self.context.get('request')})
        return first_image_serializer.data['image_url']
        
    class Meta:
        model = Collection
        fields = ['id', 'image', 'collection_name']
    

class CategorySerializer(serializers.ModelSerializer):   
    class Meta:
        model = Category
        fields = ['id', 'category_name']


class MenuSerializer(serializers.ModelSerializer):
    menu_name = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ['id', 'menu_name', 'categories']

    def get_menu_name(self, obj):
        return dict(Menu.CHOICES).get(obj.menu_name)

    def get_categories(self, obj):
        categories = obj.menu_item.all()
        return [{'id': category.id, 'name': category.category_name} for category in categories]


class SizeChoiceField(serializers.MultipleChoiceField):
    def to_representation(self, value):
        return [size.get_name_display() for size in value.all()]
    

class ImageProductSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = '__all__'

    def get_image_url(self, obj):
        if 'request' in self.context:
            request = self.context['request']
            image_url = obj.image_url.url
            return request.build_absolute_uri(image_url)
        return None
    

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']
        
    
class ColorSerializer(serializers.ModelSerializer):
    sizes = serializers.SerializerMethodField()

    class Meta:
        model = Color
        fields = ('id', 'color_hex', 'color_name', 'sizes')

    def get_sizes(self, color):
        product_colors = ProductColor.objects.filter(color=color)
        size_data = []

        for product_color in product_colors:
            size_data.append({
                'size': SizeSerializer(product_color.size).data,
                'quantity': product_color.quantity
            })

        return size_data
    
class ProductColorSerializer(serializers.ModelSerializer): 
    color = ColorSerializer()
    images = ImageProductSerializer( many=True) 
    class Meta:
        model = ProductColor
        fields = ['id', 'images', 'color']


class RelatedProductSerializer(serializers.ModelSerializer):
    collection_name = serializers.CharField(source='collection.collection_name', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'collection_name', 'product_name', 'price', 'image']

    def get_image(self, obj):
        first_image = obj.productcolors.first().images.first() if obj.productcolors.exists() else None
        if first_image:
            return first_image.image_url.url
        return None

class ProductNameSerializer(serializers.ModelSerializer):
    collection_name = serializers.CharField(source='collection.collection_name', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'image', 'collection_name', 'product_name', 'price', ]

    def get_image(self, obj):
        first_image = obj.productcolors.first().images.first() if obj.productcolors.exists() else None
        if first_image:
            image_url = first_image.image_url.url
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image_url)
            return image_url
        return None


class ProductSerializer(serializers.ModelSerializer):
    colors = ProductColorSerializer(source='productcolors', many=True)
    collection = CollectionSerializer()
    category = CategorySerializer(many=True)
    instructions = serializers.SerializerMethodField()

    views = serializers.SerializerMethodField()
    related_products = RelatedProductSerializer(many=True, read_only=True)


    def get_views(self, obj):
        # Получение количества просмотров с учетом уникальных IP-адресов
        return obj.views.values('ip').distinct().count() 
    

    class Meta:
        model = Product
        fields = ['id', 'collection', 'product_name','price', 'delivery_info', 'sku', 'model_parameters' , 'size_on_the_model', 'description', 'colors' , 'instructions', 'category', 'quantity','related_products', 'date', 'views'] 
    
    
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



class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'