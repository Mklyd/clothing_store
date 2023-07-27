from django.urls import path, include

from rest_framework import routers
from django.conf import settings
from django.conf.urls.static  import static

from .views import ProductViewSet, MenuViewSet, CollectionViewSet, ColorAndSizesViewSet, CategoryViewSet, HomePageViewSet

router = routers.DefaultRouter()
router.register(r'product', ProductViewSet)
router.register(r'menu', MenuViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'collection', CollectionViewSet)
router.register(r'colors&sizes', ColorAndSizesViewSet, basename='filter')
router.register(r'home', HomePageViewSet, basename='home')


urlpatterns = [
    path('', include(router.urls))
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
