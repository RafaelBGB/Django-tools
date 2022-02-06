from django.contrib.auth import get_user_model
from django import forms

from authapp.forms import ShopUserEditForm, HiddenInput
from mainapp.models import ProductCategory, Product
from ordersapp.models import Order


class AdminShopUserUpdateForm(ShopUserEditForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'password',
                  'email', 'age', 'avatar',
                  'is_staff', 'is_superuser', 'is_active')


class ProductCategoryEditForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductEditForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class AdminOrdersEditForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('user',)
