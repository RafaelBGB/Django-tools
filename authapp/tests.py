from django.test import TestCase
from django.test.client import Client
from django.core.management import call_command
from django.conf import settings

from authapp.models import ShopUser


class TestUserManagement(TestCase):
    def setUp(self):

        self.client = Client()
        self.superuser = ShopUser.objects.create_superuser(
            'django2',
            'django2@geekshop.local',
            'geekbrains'
        )
        self.user = ShopUser.objects.create_user(
            'test_user_1',
            'test_user_1@geekshop.local',
            'geekbrains'
        )
        self.user_with__first_name = ShopUser.objects.create_user(
            'test_user_2',
            'test_user_2@geekshop.local',
            'geekbrains',
            first_name='Ivan')

    def test_user_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_anonymous)
        self.assertEqual(response.context['page_title'], 'главная')
        self.assertNotIn('Пользователь', response.content.decode())

        self.client.login(username='test_user_1', password='geekbrains')

        response = self.client.get('/auth/login/')
        self.assertFalse(response.context['user'].is_anonymous)
        self.assertEqual(response.context['user'], self.user)

        response = self.client.get('/')
        self.assertContains(response, 'Пользователь', status_code=200)
        self.assertEqual(response.context['user'], self.user)
        self.assertIn('Пользователь', response.content.decode())

    def test_basket_login_redirect(self):
        response = self.client.get('/basket/')
        self.assertEqual(response.url, '/auth/login/?next=/basket/')
        self.assertEqual(response.status_code, 302)

        self.client.login(username='test_user_1', password='geekbrains')

        response = self.client.get('/basket/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['basket']), [])
        self.assertEqual(response.request['PATH_INFO'], '/basket/')
        self.assertIn('Пользователь', response.content.decode())

    def test_user_logout(self):
        self.client.login(username='test_user_1', password='geekbrains')

        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_anonymous)

        response = self.client.get('/auth/logout/')
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_anonymous)

    def test_user_register(self):
        response = self.client.get('/auth/user/register/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page_title'], 'регистрация')
        self.assertTrue(response.context['user'].is_anonymous)

        new_user_data = {
            'username': 'samuel',
            'first_name': 'Сэмюэл',
            'last_name': 'Джексон',
            'password1': 'geekbrains',
            'password2': 'geekbrains',
            'email': 'sumuel@geekshop.local',
            'age': '21'}

        response = self.client.post('/auth/user/register/', data=new_user_data)
        self.assertEqual(response.status_code, 200)

        new_user = ShopUser.objects.get(username=new_user_data['username'])

        activation_url = f"{settings.DOMAIN_NAME}/auth/user/verify/" \
                         f"{new_user_data['email']}/{new_user.activation_key}/"

        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, 200)

        self.client.login(username=new_user_data['username'],
                          password=new_user_data['password1'])

        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_anonymous)

        response = self.client.get('/')
        self.assertContains(response, text=new_user_data['first_name'],
                            status_code=200)

    def tearDown(self):
        call_command('sqlsequencereset', 'mainapp', 'authapp', 'ordersapp',
                     'basketapp')
