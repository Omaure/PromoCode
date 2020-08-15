# -*- coding: utf-8 -*-

from django_filters import FilterSet, NumberFilter
from django.apps import apps


class PromoCodeFilter(FilterSet):
    """
    An initial basic filter for Coupons.  This could be handled with filter_fields = () until I add in range filtering
    on the discount value, then it is more helpful to do this.
    """

    min_value = NumberFilter(name='value', lookup_expr='gte')
    max_value = NumberFilter(name='value', lookup_expr='lte')

    class Meta:
        model = apps.get_model('promo_codes.PromoCode')
        fields = ['user', 'bound', 'type', 'min_value', 'max_value']
