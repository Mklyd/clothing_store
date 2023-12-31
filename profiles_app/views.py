from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Profile, FavoriteProducts, CardProducts
from store.models import Product
from .serializers import ProfileSerializer, CardProductsSerializer, FavoritesSerializer, FavoriteProductsSerializer
from store.serializers import ProductNameSerializer

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    def post(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FavoriteProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorites = FavoriteProducts.objects.filter(user_profile__user=request.user)
        products = [item.product for item in favorites]
        serializer = ProductNameSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'message': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        user_profile = request.user.profile  # Получаем профиль текущего пользователя
        favorite_product = FavoriteProducts(user_profile=user_profile, product_id=product_id)

        try:
            favorite_product.save()
            return Response({'message': 'Product added to favorites'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'message': 'Error adding product to favorites'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({'message': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        user_profile = Profile.objects.get(user=request.user)  # Получаем профиль текущего пользователя
        
        try:
            favorite_product = FavoriteProducts.objects.get(user_profile=user_profile, product=product_id)
            favorite_product.delete()
            return Response({'message': 'Product removed from favorites'}, status=status.HTTP_204_NO_CONTENT)
        except FavoriteProducts.DoesNotExist:
            return Response({'message': 'Product not found in favorites'}, status=status.HTTP_404_NOT_FOUND)



class CardProductsBulkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        for item in data:
            product_id = item['product']['id']
            product = Product.objects.get(id=product_id)
            size = item['size']
            color = item['color']
            user_profile = Profile.objects.get(user=request.user)

            try:
                card_product = CardProducts.objects.get(
                    user_profile=user_profile,
                    product=product.id,
                    size=size,
                    color=color
                )
                print(card_product)
                card_product.current = item['current']
                card_product.save()
                
            except CardProducts.DoesNotExist:
                serializer = CardProductsSerializer(data={
                    'user_profile': user_profile.id,
                    'product': product.id,
                    'current': item['current'],
                    'size': size,
                    'color': color
                })

                if serializer.is_valid():
                    serializer.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Products added to cart'}, status=status.HTTP_201_CREATED)



class CardProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        card_products = CardProducts.objects.filter(user_profile__user=request.user)
        serializer = CardProductsSerializer(card_products, many=True)
        return Response(serializer.data)
    def post(self, request):
        data = request.data
        user_profile = Profile.objects.get(user=request.user) 

        product_id = data['product_id']
        size = data['size']
        color = data['color']
        try:
            card_product = CardProducts.objects.get(
                user_profile=user_profile,
                product_id=product_id,
                size=size,
                color=color
            )
            card_product.current = data['current']
            card_product.save()
                
        except CardProducts.DoesNotExist:
            serializer = CardProductsSerializer(data={
                'user_profile': user_profile.id,
                'product': product_id,
                'current': data['current'],
                'size': size,
                'color': color
            })

            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Product added to cart'}, status=status.HTTP_201_CREATED)
    def delete(self, request):
        data = request.data
        user_profile = Profile.objects.get(user=request.user)
        
        try:
            card_product = CardProducts.objects.get(user_profile=user_profile, id=data['id'])
            card_product.delete()
            return Response({'message': 'Product removed from favorites'}, status=status.HTTP_204_NO_CONTENT)
        except FavoriteProducts.DoesNotExist:
            return Response({'message': 'Product not found in favorites'}, status=status.HTTP_404_NOT_FOUND)
