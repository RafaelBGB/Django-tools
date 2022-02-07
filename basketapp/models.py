from django.db import models
from django.utils.functional import cached_property

from mainapp.models import Product
from django.contrib.auth import get_user_model


class Basket(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='basket')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='количество', default=0)
    add_datetime = models.DateTimeField(verbose_name='время', auto_now_add=True)

    @cached_property
    def get_basket(self):
        item = Basket.objects.select_related()
        print(item)
        result = {
            'total_quantity': sum(list(map(lambda x: x.quantity, item))),
            'total_cost': sum(list(map(lambda x: x.product_cost, item)))
        }
        return result

    @cached_property
    def product_cost(self):
        return self.product.price * self.quantity
