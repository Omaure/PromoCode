# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from promo_codes.filters import PromoCodeFilter
from promo_codes.models import PromoCode, ClaimedPromoCode
from promo_codes.serializers import PromoCodeSerializer, ClaimedPromoCodeSerializer


def group_required():
    def in_groups(u):
        if u.is_authenticated:
            if u.is_superuser:
                return True
        return False

    return user_passes_test(in_groups)


def get_redeemed_queryset(user, promoCode_id=None):
    """
    Return a consistent list of the redeemed list.
    """

    if promoCode_id is None:
        qs_all = ClaimedPromoCode.objects.all()
        qs_some = ClaimedPromoCode.objects.filter(user=user.id)
    else:
        qs_all = ClaimedPromoCode.objects.filter(promoCode_id=promoCode_id)
        qs_some = ClaimedPromoCode.objects.filter(promoCode_id=promoCode_id, user=user.id)

    if user.is_superuser:
        return qs_all

    return qs_some


class PromoCodeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that lets you create, delete, retrieve Promo Codes.
    """

    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filter_class = PromoCodeFilter
    search_fields = ('code', 'code_l')
    serializer_class = PromoCodeSerializer

    def get_queryset(self):
        """
        Return a subset of promo codes or all promo codes depending on user
        """
        qs_all = PromoCode.objects.all()
        qs_some = PromoCode.objects.filter(bound=True, user=self.request.user.id)

        if self.request.user.is_superuser:
            return qs_all

        return qs_some

    @method_decorator(group_required())
    def create(self, request, **kwargs):
        """
        Create Promo Code
        """
        serializer = PromoCodeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(group_required())
    def destroy(self, request, pk=None, **kwargs):
        """
        Delete Promocode
        """

        promocode = get_object_or_404(PromoCode.objects.all(), pk=pk)
        promocode.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk=None, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None, **kwargs):
        """
        Anybody can retrieve a promo code
        """

        value_is_int = False

        try:
            pk = int(pk)
            value_is_int = True
        except ValueError:
            pass

        if value_is_int:
            promocode = get_object_or_404(PromoCode.objects.all(), pk=pk)
        else:
            promocode = get_object_or_404(PromoCode.objects.all(), code_l=pk.lower())

        serializer = PromoCodeSerializer(promocode, context={'request': request})

        return Response(serializer.data)

    @method_decorator(group_required())
    def update(self, request, pk=None, **kwargs):
        """
        This forces it to return a 202 upon success instead of 200.
        """

        promocode = get_object_or_404(PromoCode.objects.all(), pk=pk)

        serializer = PromoCodeSerializer(promocode, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def redeemed(self, request, pk=None, **kwargs):
        """
        Endpoint for getting a list of claimed promo codes.
        """

        promoCode = get_object_or_404(PromoCode.objects.all(), pk=pk)
        qs = get_redeemed_queryset(self.request.user, promoCode.id)

        serializer = ClaimedPromoCodeSerializer(qs, many=True, context={'request': request})

        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def redeem(self, request, pk=None, **kwargs):
        """
        Endpoint for redeeming.
        """

        queryset = PromoCode.objects.all()
        promoCode = get_object_or_404(queryset, pk=pk)

        data = {
            'promoCode': pk,
            'user': self.request.user.id,
        }

        serializer = ClaimedPromoCodeSerializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClaimedPromoCodeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that lets you retrieve claimed Promo Code details.
    """

    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('user',)
    serializer_class = ClaimedPromoCodeSerializer

    def get_queryset(self):
        return get_redeemed_queryset(self.request.user)

    def create(self, request, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    @method_decorator(group_required())
    def destroy(self, request, pk=None, **kwargs):
        """
        un-redeem a Promocode.
        """

        redeemed = get_object_or_404(ClaimedPromoCode.objects.all(), pk=pk)
        redeemed.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk=None, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None, **kwargs):
        return Response(status=status.HTTP_404_NOT_FOUND)
