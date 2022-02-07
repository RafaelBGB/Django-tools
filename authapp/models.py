import hashlib
import random
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils.timezone import now

from geekshop.settings import DOMAIN_NAME, EMAIL_HOST_USER, ACTIVATION_KEY_TTL


class ShopUser(AbstractUser):
    avatar = models.ImageField(upload_to='user_avatars', blank=True)
    age = models.PositiveIntegerField(verbose_name='возраст', default=18)
    activation_key = models.CharField(max_length=128, blank=True)
    email = models.EmailField('email address', unique=True)

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save(using=using)

    def is_activation_key_expired(self):
        return now() - self.date_joined > timedelta(hours=ACTIVATION_KEY_TTL)

    def set_activation_key(self):
        salt = hashlib.sha1(str(random.random()).encode('utf8')).hexdigest()[:6]
        self.activation_key = hashlib.sha1((self.email + salt).encode('utf8')).hexdigest()

    def send_confirm_email(self):
        verify_link = reverse('auth:verify', kwargs={'email': self.email, 'activation_key': self.activation_key})
        subject = f'Подтверждение учетоной записи {self.username}'
        massage = f'Для завершения регистрации пройдите по ссылке: \n{DOMAIN_NAME}{verify_link}'
        return send_mail(subject, massage, EMAIL_HOST_USER, [self.email])

    def basket_price(self):
        return sum(el.product_cost for el in self.basket.all())

    def basket_qty(self):
        return sum(el.quantity for el in self.basket.all())


class ShopUserProfile(models.Model):
    MALE = 'M'
    FEMALE = 'W'

    GENDER_CHOICES = (
        (MALE, 'мужской'),
        (FEMALE, 'женский'),
    )

    user = models.OneToOneField(ShopUser, primary_key=True, on_delete=models.CASCADE)
    tagline = models.CharField(verbose_name='теги', max_length=128, blank=True)
    about_me = models.TextField(verbose_name='о себе', blank=True)
    gender = models.CharField(verbose_name='пол', max_length=1, choices=GENDER_CHOICES, blank=True)
