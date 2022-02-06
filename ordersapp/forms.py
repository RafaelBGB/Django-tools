from django import forms
from django.forms import HiddenInput

from ordersapp.models import Order, OrderItem
from mainapp.models import Product


class BaseOrderForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'user':
                field.widget = HiddenInput()

            # if field_name == 'quantity' and self.instance.pk:
            #     field.widget.attrs['max'] = self.instance.product.quantity

            field.widget.attrs['class'] = 'form-control'


class OrderForm(BaseOrderForm):
    class Meta:
        model = Order
        fields = ('user',)


class OrderItemForm(BaseOrderForm):
    total_quantity = forms.IntegerField(required=False, label='количество на складе')
    price = forms.FloatField(required=False, label='цена за единицу')
    total_price = forms.FloatField(required=False, label='цена')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.get_items()

    def clean(self):
        cleaned_data = super().clean()
        quantity = self.cleaned_data.get('quantity')
        product = self.cleaned_data.get('product')
        if quantity > product.quantity:
            msg = 'что-то пошло не так...'
            self.add_error('quantity', msg)
        return cleaned_data

    class Meta:
        model = OrderItem
        fields = '__all__'
