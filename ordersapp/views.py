from django.urls import reverse_lazy
from django.forms import inlineformset_factory
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, DetailView
from django.db import transaction
from django.shortcuts import get_object_or_404, reverse
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from ordersapp.models import Order, OrderItem
from ordersapp.forms import OrderForm, OrderItemForm
from mainapp.models import Product
from mixins.mixins import PageTitleMixin, UserOnlyMixin


class OrderList(UserOnlyMixin, ListView, PageTitleMixin):
    model = Order
    page_title = 'заказы'

    def get_queryset(self):
        return self.request.user.users_order.all()


class OrderCreate(UserOnlyMixin, CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('orders:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'заказы/создание'
        OrderFromSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=3)

        if self.request.POST:
            formset = OrderFromSet(self.request.POST, self.request.FILES)
        else:
            context['form'].initial['user'] = self.request.user
            basket_item = self.request.user.basket.all()
            if basket_item and basket_item.count():
                OrderFromSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm,
                                                     extra=basket_item.count() + 1)

                formset = OrderFromSet()
                for form, item in zip(formset.forms, basket_item):
                    form.initial['product'] = item.product
                    form.initial['quantity'] = item.quantity
                    form.initial['price'] = item.product.price
            else:
                formset = OrderFromSet()

        context['orderitems'] = formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            order = super().form_valid(form)
            if orderitems.is_valid():
                orderitems.instance = self.object
                orderitems.save()
                self.request.user.basket.all().delete()

        if self.object.total_quantity == 0:
            self.object.delete()

        return order


class OrderUpdate(UserOnlyMixin, UpdateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('orders:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'зазазы/редактирование'
        OrderFromSet = inlineformset_factory(Order, OrderItem, form=OrderItemForm, extra=1)

        if self.request.POST:
            formset = OrderFromSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            queryset = self.object.order.select_related('product')
            formset = OrderFromSet(instance=self.object, queryset=queryset)
            for form in formset.forms:
                instance = form.instance
                if instance.pk:
                    form.initial['price'] = instance.product.price
                    form.initial['total_price'] = instance.product.price * instance.quantity
                    form.initial['total_quantity'] = instance.product.quantity
        context['orderitems'] = formset
        return context

    @transaction.atomic()
    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        if orderitems.is_valid():
            orderitems.save()
        if self.object.get_summary['total_cost'] == 0:
            self.object.delete()

        return super().form_valid(form)


class OrderDelete(UserOnlyMixin, DeleteView, PageTitleMixin):
    model = Order
    success_url = reverse_lazy('orders:index')
    page_title = 'заказы/удаление'


class OrderRead(UserOnlyMixin, DetailView, PageTitleMixin):
    model = Order
    page_title = 'заказы/просмотр'


def forming_complete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = Order.SENT_TO_PROCEED
    order.save()
    return HttpResponseRedirect(reverse('orders:index'))


def ajax_update(request, pk=None):
    if request.is_ajax:
        product = Product.objects.get(pk=int(pk))
        return JsonResponse({'price': product and product.price or 0,
                             'quantity': product and product.quantity or 0})
