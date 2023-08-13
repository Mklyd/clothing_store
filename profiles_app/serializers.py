from rest_framework import serializers
from .models import Profile, FavoriteProducts, CardProducts

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class FavoriteProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteProducts
        fields = '__all__'

class CardProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CardProducts
        fields = '__all__'