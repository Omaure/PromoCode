from __future__ import unicode_literals
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

PROMO_TYPES = (
    ('percent', 'percent'),
    ('value', 'value'),
)

TRANSACTION_TYPES = (
    ('cash', 'cash'),
    ('visa', 'visa'),
    ('ewallet', 'ewallet'),
)

COMPANIES = (
    ('SWVL', 'SWVL'),
    ('UBER', 'UBER'),
    ('AUC', 'AUC')
)

try:
    # In case they specified something else in their settings file, which is quite common.
    user = settings.AUTH_USER_MODEL
except AttributeError:
    # get_user_model isn't working at this point in loading.
    from django.contrib.auth.models import User as user


class PromoCode(models.Model):
    """
     - Promo Codes can be a value, or a percentage.
     - They can be bound to a specific user in the system.
     - They can be single-use per user, or single-use globally.
     - They can be used a specific number of times per user, or globally.
     - They can be infinite per a specific user, or infinite globally.
     """

    created = models.DateTimeField(auto_now_add=True, help_text=_("Creation Time"), verbose_name=_("Creation Time"))

    updated = models.DateTimeField(auto_now=True, help_text=_("Update Time"), verbose_name=_("Update Time"))

    code = models.CharField(max_length=64, help_text=_("The unique promo code"), verbose_name=_("Promo Code"))

    code_l = models.CharField(max_length=64, blank=True, unique=True,
                              help_text=_("Lower Case Promo Code to have unique codes"),
                              verbose_name=_("Lower Case Promo Code"))

    type = models.CharField(max_length=16, choices=PROMO_TYPES,
                            help_text=_("Percentage or a value."), verbose_name=_("Type"))

    expires = models.DateTimeField(blank=True, null=True,
                                   help_text=_("When it expires (if it expires)"), verbose_name=_("Expire Time"))

    value = models.DecimalField(default=0.0, max_digits=10, decimal_places=2,
                                help_text=_("If percentage based make sure it's no greater than 1.0"),
                                verbose_name=_("Promo Code Value"))

    bound = models.BooleanField(default=False,
                                help_text=_("Is this Promo Code bound to a specific user?"),
                                verbose_name=_("Bound to user"))

    user = models.ForeignKey(user, blank=True, null=True, on_delete=models.CASCADE,
                             help_text=_("Which User is it bounded to?"),
                             verbose_name=_("User"))

    # To determine if you can redeem it, it'll check this value against the number of corresponding ClaimedPromoCodes.
    repeat = models.IntegerField(default=0,
                                 help_text=_(
                                     "How many times this Promo Code can be used, 0 == infinitely, otherwise it's a number, such as 1 or many."),
                                 verbose_name=_("Repeat"))

    # single-use per user
    # repeat = 1, bound = True, binding = user_id
    # single-use globally
    # repeat = 1, bound = False

    # infinite-use per user
    # repeat = 0, bound = True, binding = user_id
    # infinite globally
    # repeat = 0, bound = False

    # specific number of times per user
    # repeat => X, bound = True, binding = user_id
    # specific number of times globally
    # repeat => X, bound = False

    def __str__(self):
        return "Promo Code: " + self.code


class ClaimedPromoCode(models.Model):
    """
    These are the instances of claimed codes, each is an individual usage of a Promo Code by someone in the system.
    """

    redeemed = models.DateTimeField(auto_now_add=True,
                                    help_text=_("Redeem Time"),
                                    verbose_name=_("Redeem"))

    typeOfPayment = models.CharField(default="Cash", max_length=16, choices=TRANSACTION_TYPES,
                                     help_text=_("Cash or Visa"), verbose_name=_("Type of payment"))

    company = models.CharField(default="", max_length=64, blank=False,
                               help_text=_("Name of the business Company"),
                               verbose_name=_("Company"))

    item = models.CharField(default="", max_length=64, blank=False,
                            help_text=_("What type of item"),
                            verbose_name=_("Item"))

    service = models.CharField(default="", max_length=64, blank=False,
                               help_text=_("Name of the service"),
                               verbose_name=_("Service"))

    total_price = models.DecimalField(default=0.0, max_digits=10, decimal_places=2,
                                      help_text=_("How much did the user pay"),
                                      verbose_name=_("Total Price"))

    promoCode = models.ForeignKey('PromoCode', on_delete=models.CASCADE)
    user = models.ForeignKey(user, on_delete=models.CASCADE)

    def __str__(self):
        return "Promo Code Redeem Number: " + str(self.id)
