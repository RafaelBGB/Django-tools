from django.db import models
from django.contrib.auth import get_user_model
from django.utils.functional import cached_property

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
    created_data = models.DateTimeField(verbose_name='время добавления', db_index=True, auto_now_add=True)
    update_data = models.DateTimeField(verbose_name='время обновления', auto_now=True)
    status = models.CharField(verbose_name='статус', max_length=3, choices=STATUS_CHOICES, default=FORMING)
    is_active = models.BooleanField(verbose_name='активен', db_index=True, default=True)

    class Meta:
        ordering = ('-created_data',)
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    @cached_property
    def is_forming(self):
        return self.status == self.FORMING

    @cached_property
    def get_summary(self):
        items = self.order.select_related()
        summary = {
            'total_quantity': sum(map(lambda x: x.quantity, items)),
            'total_cost': sum(map(lambda x: x.product_cost, items))
        }
        return summary

    def delete(self, using=None, keep_parents=False):
        self.order.delete()
        self.status = Order.CANCEL
        self.save()


class OrderItemQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        for item in self:
            item.delete()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order')
    product = models.ForeignKey(Product, verbose_name='продукт', on_delete=models.CASCADE, related_name='product')
    quantity = models.PositiveIntegerField(verbose_name='количество', default=0)

    objects = OrderItemQuerySet.as_manager()

    @cached_property
    def product_cost(self):
        return self.product.price * self.quantity

    def delete(self, using=None, keep_parents=False):
        self.product.quantity += self.quantity
        self.product.save()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.pk:
            old_value = Order.objects.get(pk=self.order.pk).order.get(pk=self.pk).quantity
            self.product.quantity += old_value - self.quantity
        else:
            self.product.quantity -= self.quantity

        self.product.save()
        super().save()
