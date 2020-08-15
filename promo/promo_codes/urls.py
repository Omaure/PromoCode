from django.conf.urls import url, include
from rest_framework import routers
from promo_codes import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'promocode', views.PromoCodeViewSet, basename='promocode')
router.register(r'redeemed', views.ClaimedPromoCodeViewSet, basename='redeemed')

urlpatterns = [
    url(r'^', include(router.urls)),
]
