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
    age = models.PositiveIntegerField(verbose_name='возраст')
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
