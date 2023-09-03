from django.urls import path, include

from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static

from .views import ProductViewSet, MenuViewSet, CollectionViewSet, ColorAndSizesViewSet, CategoryViewSet, HomePageViewSet, OrderViewSet, YookassaPaymentCreateAPIView
""" , PaymentConfirmationView, PaymentCancellationView """

router = routers.DefaultRouter()
router.register(r'product', ProductViewSet)
# router.register(r'orders', OrderViewSet)
router.register(r'menu', MenuViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'collection', CollectionViewSet)
router.register(r'colors&sizes', ColorAndSizesViewSet, basename='filter')
router.register(r'home', HomePageViewSet, basename='home')


urlpatterns = [
    path('payments/yookassa/', YookassaPaymentCreateAPIView.as_view(),
         name='yookassa-payment-create'),
    # path('confirm-payment/', PaymentConfirmationView.as_view(), name='confirm-payment'),
    # path('cancel-payment/', PaymentCancellationView.as_view(), name='cancel-payment'),
    path('orders/', OrderViewSet.as_view(), name='order-list'),
    path('', include(router.urls))
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
