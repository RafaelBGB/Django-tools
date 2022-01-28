from django.db import models
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import pre_save, pre_delete

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
        # for item in self.order.all():
        #     item.product.quantity += item.quantity
        #     item.product.save()

        # вызываем delete для продуктов заказа. Хотя на мой взгляд это лучше сделать циклом for,
        # прям в данном методе (закоментировано выше)
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

    items = OrderItemQuerySet.as_manager()

    @property
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


# @receiver(pre_save, sender=OrderItem)
# def product_quantity_update_save(sender, update_fields, instance, **kwargs):
#     if instance.pk:
#         old_quantity = sender.objects.get(pk=instance.pk).quantity
#         instance.product.quantity += old_quantity - instance.quantity
#     else:
#         instance.product.quantity -= instance.quantity
#
#     instance.product.save()
#
#
# @receiver(pre_delete, sender=OrderItem)
# def product_quantity_update_delete(sender, instance, **kwargs):
#     print('orderitem delete')
#     instance.product.quantity += instance.quantity
#     instance.product.save()
