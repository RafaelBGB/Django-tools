from social_core.exceptions import AuthForbidden
import requests

from authapp.models import ShopUser, ShopUserProfile
from geekshop.settings import MEDIA_ROOT


def save_user_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'vk-oauth2':
        if 'email' in response.keys():
            if response['email'].split('.')[-1] != 'ru':
                user.delete()
                raise AuthForbidden(backend)
            user.email = response['email']

        if 'about' in response.keys():
            user.shopuserprofile.about_me = response['about']

        if 'sex' in response.keys():
            if response['sex'] == 1:
                user.shopuserprofile.gender = ShopUserProfile.FEMALE
            elif response['sex'] == 2:
                user.shopuserprofile.gender = ShopUserProfile.MALE

        if 'photo' in response.keys():
            with open(f'{MEDIA_ROOT}/user_avatars/{response["first_name"]}_{response["last_name"]}.jpg', 'wb') as f:
                f.write(requests.get(response['photo']).content)

            user.avatar = f'{MEDIA_ROOT}/user_avatars/{response["first_name"]}_{response["last_name"]}.jpg'
    user.save()
