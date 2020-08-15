from django.contrib import admin

# Register your models here.
from .models import PromoCode, ClaimedPromoCode

admin.site.register(PromoCode)
admin.site.register(ClaimedPromoCode)
