# -*- coding: utf-8 -*-

from django.apps import apps
from django.utils.timezone import now
from rest_framework import serializers

from promo_codes.models import PromoCode, ClaimedPromoCode


class PromoCodeSerializer(serializers.ModelSerializer):
    def validate(self, data):
        """
        Verify the input used to create or update the PromoCode is valid.  Because we don't support PATCH for the binding
        field, we don't need to check self.instance for this.
        """

        # Verify if the expiration date
        if 'expires' in data:
            if data['expires'] < now():
                raise serializers.ValidationError("Expiration date set incorrect")

        # Verify if type is 'percentage' that it is a percentage value which is only 1.0 or less than it
        if data['type'] == 'percent':
            if 'value' in data and data['value'] > 1.0:
                raise serializers.ValidationError("Percentage discount specified greater than 100%.")

        # Verify if it's bound, that the user exists.
        if 'bound' in data and data['bound']:
            if 'user' not in data:
                raise serializers.ValidationError("Bound to user, but user field not specified.")

        # Verify the lowercase code is unique.
        # IntegrityError: UNIQUE constraint failed: coupons_coupon.code_l and not returning 400.
        qs = PromoCode.objects.filter(code_l=data['code'].lower())
        if qs.count() > 0:
            # there was a matching one, is it this one?
            if self.instance:
                if data['code'].lower() != self.instance.code_l:
                    raise serializers.ValidationError("Promo Code code being updated to a code that already exists.")
            else:
                raise serializers.ValidationError("Creating Promo Code with code that violates uniqueness constraint.")

        data['code_l'] = data['code'].lower()

        return data

    def validate_repeat(self, value):
        """
        Validate that if it's specified it can be -1, 1, or more than that, but not zero.
        """

        if value < 0:
            raise serializers.ValidationError("Repeat field can be 0 for infinite, otherwise must be greater than 0.")

        return value

    def create(self, validated_data):
        return PromoCode.objects.create(**validated_data)

    class Meta:
        model = apps.get_model('promo_codes.PromoCode')
        fields = ('created', 'updated', 'code',
                  'code_l', 'type', 'expires',
                  'bound', 'user', 'repeat',
                  'value', 'id')


class ClaimedPromoCodeSerializer(serializers.ModelSerializer):
    """
    RW ClaimedCoupon serializer.
    """

    def validate(self, data):
        """
        Verify the Promo Code can be redeemed.
        """

        promoCode = data['promoCode']
        user = data['user']

        # Is the Promo Code expired?
        if promoCode.expires and promoCode.expires < now():
            raise serializers.ValidationError("Promo Code has expired.")

        # Is the Promo Code bound to someone else?
        if promoCode.bound and promoCode.user.id != user.id:
            raise serializers.ValidationError("Promo Code bound to another user.")

        # Is the Promo Code redeemed already beyond what's allowed?
        redeemed = ClaimedPromoCode.objects.filter(promoCode=promoCode.id, user=user.id).count()
        if promoCode.repeat > 0:
            if redeemed >= promoCode.repeat:
                # Already too many times (note: we don't update the claimed coupons, so this is a fine test).
                # Also, yes, > should never happen because the equals check will be hit first, but just in case
                # you somehow get beyond that... ;)
                raise serializers.ValidationError("Promo Code has been used to its limit.")

        return data

    class Meta:
        model = apps.get_model('promo_codes.ClaimedPromoCode')
        fields = ('redeemed', 'promoCode', 'user', 'id', 'company', 'typeOfPayment',
                  'total_price', 'item', 'service')
