from django.db import models
from django.contrib.auth import get_user_model

from mainapp.models import Product


class Order(models.Model):
    FORMING = 'FM'
    SENT_TO_PROCEED = 'STP'
    PROCEEDED = 'PRD'
    PAID = 'PD'
    READY = 'RDY'
    CANCEL = 'CNC'

    STATUS_CHOICES = (
        (FORMING, 'формируется'),
        (SENT_TO_PROCEED, 'отправлен в обработку'),
        (PAID, 'оплачен'),
        (PROCEEDED, 'обрабатывается'),
        (READY, 'готов к выдаче'),
        (CANCEL, 'отменен'),
    )

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='users_order')
    created_data = models.DateTimeField(verbose_name='время добавления', auto_now_add=True)
    update_data = models.DateTimeField(verbose_name='время обновления', auto_now=True)
    status = models.CharField(verbose_name='статус', max_length=3, choices=STATUS_CHOICES, default=FORMING)
    is_active = models.BooleanField(verbose_name='активен', default=True)

    class Meta:
        ordering = ('-created_data',)
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    @property
    def is_forming(self):
        return self.status == self.FORMING

    @property
    def total_quantity(self):
        return sum(map(lambda x: x.quantity, self.order.all()))

    @property
    def total_cost(self):
        return sum(map(lambda x: x.product_cost, self.order.all()))

    def delete(self, using=None, keep_parents=False):
        self.status = Order.CANCEL
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order')
    product = models.ForeignKey(Product, verbose_name='продукт', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='количество', default=0)

    @property
    def product_cost(self):
        return self.product.price * self.quantity
