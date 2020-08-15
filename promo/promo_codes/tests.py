# -*- coding: utf-8 -*-

# Create your tests here.
from django.contrib.auth import get_user_model
from rest_framework import status
from datetime import datetime, timedelta
from time import sleep
from rest_framework.test import APITestCase


class BasicTest(APITestCase):
    """
    Generic testing stuff.
    """

    PW = 'password123'

    def login(self, username):
        self.client.login(username=username, password=self.PW)

    def logout(self):
        self.client.logout()

    def verify_built(self, expected, data):
        for key in expected:
            self.assertEqual(data[key], expected[key])


class promocodeCreateTests(BasicTest):

    def setUp(self):
        u = get_user_model()
        u.objects.create_superuser('admin', 'admin@paymob.com', self.PW)
        self.user = u.objects.create_user('user', 'omar@paymob.com', self.PW)

    def test_can_create_promocode(self):
        promocode = {
            'code': 'HelloPaymob',
            'type': 'percent',
        }

        with self.settings(ROOT_URLCONF='promo_codes.urls'):
            self.login(username='admin')
            response = self.client.post('/promocode', promocode, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.logout()
            print(response.data)
            promocode['code_l'] = promocode['code'].lower()
            promocode['repeat'] = 0
            promocode['bound'] = False

            self.verify_built(promocode, response.data)

    def test_can_create_arabic_and_header(self):
        promocode = {
            'code': 'يا هلا',
            'type': 'percent',
        }

        with self.settings(ROOT_URLCONF='promo_codes.urls'):
            self.login(username='admin')
            response = self.client.post('/promocode', promocode, format='json',
                                        headers={'TestHeader': ' عمر'})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.logout()
            print(response.data)
            promocode['code_l'] = promocode['code'].lower()
            promocode['repeat'] = 0
            promocode['bound'] = False

            self.verify_built(promocode, response.data)

    def test_can_create_promocode_code_codel_mismatch(self):
        """
        Verify that even if you specify the lowercase version of the code when creating, it'll be ignored.
        """

        promocode = {
            'code': 'Pay1',
            'code_l': 'mismatch',
            'type': 'percent',
        }

        with self.settings(ROOT_URLCONF='promo_codes.urls'):
            self.login(username='admin')
            response = self.client.post('/promocode', promocode, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.logout()

            promocode['code_l'] = promocode['code'].lower()
            promocode['repeat'] = 0
            promocode['bound'] = False
            print(response.data)
            self.verify_built(promocode, response.data)

    def test_cant_create_promocode_duplicate_name(self):
        """
        Verify that we ensure uniqueness of promocode code.
        """

        # Create initial one.
        promocode = {
            'code': 'Paymob',
            'type': 'percent',
        }

        # Create duplicate.
        promocode2 = {
            'code': 'PAYMOB',
            'type': 'percent',
        }
        with self.settings(ROOT_URLCONF='promo_codes.urls'):
            self.login(username='admin')
            response = self.client.post('/promocode', promocode, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.logout()

            promocode['code_l'] = promocode['code'].lower()
            promocode['repeat'] = 0
            promocode['bound'] = False

            self.verify_built(promocode, response.data)

            self.login(username='admin')
            response = self.client.post('/promocode', promocode2, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.logout()
            print(response.data)


class promocodeRedeemTests(BasicTest):

    def setUp(self):
        u = get_user_model()
        u.objects.create_superuser('admin', 'john@snow.com', self.PW)
        self.user = u.objects.create_user('user', 'me@snow.com', self.PW)

    def test_cant_redeem_expired(self):
        """
        Verify that if a promocode is expired, it can't be redeemed.
        """

        future = datetime.utcnow() + timedelta(seconds=5)

        promocode = {
            'code': 'Wezaaaa',
            'type': 'percent',
            'expires': str(future),
        }

        with self.settings(ROOT_URLCONF='promo_codes.urls'):
            self.login(username='admin')
            response = self.client.post('/promocode', promocode, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            promocode_id = response.data['id']
            self.logout()
            print(response.data)
            # sleep until it's expired.
            sleep(5)

            self.login(username='admin')
            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            print(response.data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.logout()

    def test_cant_redeem_wrong_user(self):
        """
        Verify that you can't redeem a promocode that is bound to another user.
        """

        promocode = {
            'code': 'Omar',
            'type': 'percent',
            'bound': True,
            'user': self.user.id,
            'repeat': 1,
        }

        with self.settings(ROOT_URLCONF='promo_codes.urls'):
            self.login(username='admin')
            response = self.client.post('/promocode', promocode, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            print(response.data)
            promocode_id = response.data['id']
            self.logout()

            promocode['code_l'] = promocode['code'].lower()

            self.verify_built(promocode, response.data)

            self.login(username='admin')
            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            print(response.data)
            self.logout()

    def test_can_redeem_nonbound(self):
        """
        Verify that you can redeem a promocode that isn't bound to a specific user.
        """

        promocode = {
            'code': 'Wezaaaa',
            'type': 'percent',
        }

        with self.settings(ROOT_URLCONF='promo_codes.urls'):
            self.login(username='admin')
            response = self.client.post('/promocode', promocode, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            promocode_id = response.data['id']
            self.logout()

            self.login(username='admin')
            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.logout()

    def test_can_redeem_bound_to_you(self):
        """
        Verify that you can redeem a bound promocode if it's bound to you.
        """

        promocode = {
            'code': 'Wezaaaa',
            'type': 'percent',
            'bound': True,
            'user': self.user.id,
            'repeat': 1,
        }

        with self.settings(ROOT_URLCONF='promo_codes.urls'):
            self.login(username='admin')
            response = self.client.post('/promocode', promocode, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            promocode_id = response.data['id']
            self.logout()

            promocode['code_l'] = promocode['code'].lower()

            self.verify_built(promocode, response.data)

            self.login(username='user')
            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.logout()

    def test_cant_redeem_beyond_repeat(self):
        """
        Verify you can't redeem a promocode more than allowed.
        """

        promocode = {
            'code': 'Wezaaaa',
            'type': 'percent',
            'repeat': 2,
        }

        with self.settings(ROOT_URLCONF='promo_codes.urls'):
            self.login(username='admin')
            response = self.client.post('/promocode', promocode, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            promocode_id = response.data['id']

            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.logout()

    def test_cant_redeem_beyond_repeat_singleuse(self):
        """
        Verify you can't redeem a promocode more than allowed.  No huge difference for this, but just in case.
        """

        promocode = {
            'code': 'Wezaaaa',
            'type': 'percent',
            'repeat': 1,
        }

        with self.settings(ROOT_URLCONF='promo_codes.urls'):
            self.login(username='admin')
            response = self.client.post('/promocode', promocode, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            promocode_id = response.data['id']

            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.logout()

    def test_cant_redeem_beyond_repeat_multiple_users(self):
        """
        Verify that it only takes into account your claims and not other users.
        """

        promocode = {
            'code': 'Wezaaaa',
            'type': 'percent',
            'repeat': 1,
        }

        with self.settings(ROOT_URLCONF='promo_codes.urls'):
            self.login(username='admin')
            response = self.client.post('/promocode', promocode, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            promocode_id = response.data['id']
            self.logout()

            self.login(username='admin')
            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.logout()

            self.login(username='user')
            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.logout()

            self.login(username='user')
            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.logout()

    def test_can_redeem_repeat_infinite(self):
        """
        Verify that it does support repeat being 0.
        """

        promocode = {
            'code': 'Wezaaaa',
            'type': 'percent',
            'repeat': 0,
        }

        with self.settings(ROOT_URLCONF='promo_codes.urls'):
            self.login(username='admin')
            response = self.client.post('/promocode', promocode, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            promocode_id = response.data['id']
            self.logout()

            self.login(username='admin')
            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.logout()

            self.login(username='user')
            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.logout()

            self.login(username='user')
            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.logout()

    def test_can_redeem_beyond_repeat_singleuse_after_promocode_updated(self):
        """
        Verify if the promocode is updated, you can claim it more if they increase the count. :)
        """

        promocode = {
            'code': 'Wezaaaa',
            'type': 'percent',
            'repeat': 1,
        }

        with self.settings(ROOT_URLCONF='promo_codes.urls'):
            self.login(username='admin')
            response = self.client.post('/promocode', promocode, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            promocode_id = response.data['id']

            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            response = self.client.get('/promocode/%s' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            promocode = response.data
            promocode['repeat'] = 2
            del promocode['created']
            del promocode['updated']
            del promocode['id']
            del promocode['expires']

            response = self.client.put('/promocode/%s' % promocode_id, promocode, format='json')
            self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.logout()


class promocodeRedeemedTests(BasicTest):

    def setUp(self):
        u = get_user_model()
        u.objects.create_superuser('admin', 'john@snow.com', self.PW)
        self.user = u.objects.create_user('user', 'me@snow.com', self.PW)
        self.user2 = u.objects.create_user('user1', 'me1@snow.com', self.PW)

    def test_can_redeemed_list_all_users(self):
        """
        Verify that an admin can list all claims for a specific promocode.
        """

        with self.settings(ROOT_URLCONF='promo_codes.urls'):
            promocode = {
                'code': 'Wezaaaa',
                'type': 'percent',
            }

            self.login(username='admin')
            response = self.client.post('/promocode', promocode, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            promocode_id = response.data['id']
            self.logout()

            self.login(username='admin')
            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.logout()

            self.login(username='user1')
            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.logout()

            self.login(username='admin')
            response = self.client.get('/promocode/%s/redeemed' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(2, len(response.data))
            self.logout()

    def test_can_redeemed_list_mine(self):
        """
        Verify that a user can only see their claims for a specific promocode.
        """

        with self.settings(ROOT_URLCONF='promo_codes.urls'):
            promocode = {
                'code': 'Wezaaaa',
                'type': 'percent',
            }

            self.login(username='admin')
            response = self.client.post('/promocode', promocode, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            promocode_id = response.data['id']
            self.logout()

            self.login(username='user')
            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.logout()

            self.login(username='user1')
            response = self.client.put('/promocode/%s/redeem' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.logout()

            self.login(username='admin')
            response = self.client.get('/promocode/%s/redeemed' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(2, len(response.data))
            self.logout()

            self.login(username='user')
            response = self.client.get('/promocode/%s/redeemed' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(1, len(response.data))
            self.assertEqual(self.user.id, response.data[0]['user'])
            self.logout()

            self.login(username='user1')
            response = self.client.get('/promocode/%s/redeemed' % promocode_id, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(1, len(response.data))
            self.assertEqual(self.user2.id, response.data[0]['user'])
            self.logout()
