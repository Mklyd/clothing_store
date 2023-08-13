from django.urls import path
from .views import ProfileView, FavoriteProductsView, CardProductsBulkView, CardProductsView

urlpatterns = [
    path('', ProfileView.as_view(), name='profile'),
    path('favorite-products/', FavoriteProductsView.as_view(), name='favorite-products'),
    path('card-products/', CardProductsView.as_view(), name='card-products'),
    path('add-card-products/', CardProductsBulkView.as_view(), name='add-card-products'),
]