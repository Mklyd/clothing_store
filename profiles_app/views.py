from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Profile, FavoriteProducts, CardProducts
from .serializers import ProfileSerializer, FavoriteProductsSerializer, CardProductsSerializer

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data)
        except Profile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FavoriteProductsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        favorite_products = FavoriteProducts.objects.filter(user_profile__user=request.user)
        serializer = FavoriteProductsSerializer(favorite_products, many=True)
        return Response(serializer.data)
    def post(self, request):
        data = request.data
        user_profile = Profile.objects.get(user=request.user)  # Получаем профиль текущего пользователя
        serializer = FavoriteProductsSerializer(data={'user_profile': user_profile.id, 'product': data['product_id']})
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request):
        data = request.data
        user_profile = Profile.objects.get(user=request.user)  # Получаем профиль текущего пользователя
        
        try:
            favorite_product = FavoriteProducts.objects.get(user_profile=user_profile, product=data['product_id'])
            favorite_product.delete()
            return Response({'message': 'Product removed from favorites'}, status=status.HTTP_204_NO_CONTENT)
        except FavoriteProducts.DoesNotExist:
            return Response({'message': 'Product not found in favorites'}, status=status.HTTP_404_NOT_FOUND)



class CardProductsBulkView(APIView):
    def post(self, request):
        data = request.data
        user_profile = Profile.objects.get(user=request.user)

        for item in data:
            product_id = item['product_id']
            size = item['size']
            color = item['color']

            try:
                card_product = CardProducts.objects.get(
                    user_profile=user_profile,
                    product_id=product_id,
                    size=size,
                    color=color
                )
                
                card_product.current += item['current']
                card_product.save()
                
            except CardProducts.DoesNotExist:
                serializer = CardProductsSerializer(data={
                    'user_profile': user_profile.id,
                    'product': product_id,
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
