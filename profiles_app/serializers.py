from rest_framework import serializers
from .models import Profile, FavoriteProducts, CardProducts
from store.models import Product
from store.serializers import ProductNameSerializer

class FavoriteProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteProducts
        fields = ['product'] 
    product = ProductNameSerializer( read_only=True)    

class FavoritesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'


class CardProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardProducts
        fields = '__all__'