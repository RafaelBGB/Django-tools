from django.urls import reverse_lazy
from django.forms import inlineformset_factory
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, \
    DetailView
from django.db import transaction
from django.shortcuts import get_object_or_404, reverse
from django.http import HttpResponseRedirect

from ordersapp.models import Order, OrderItem
from ordersapp.forms import OrderForm, OrderItemForm
from mixins.mixins import PageTitleMixin


class OrderList(ListView, PageTitleMixin):
    model = Order
    page_title = 'заказы'

    def get_queryset(self):
        return self.request.user.users_order.all()


class OrderCreate(CreateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('orders:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'заказы/создание'
        OrderFromSet = inlineformset_factory(Order, OrderItem,
                                             form=OrderItemForm, extra=1)

        if self.request.POST:
            formset = OrderFromSet(self.request.POST, self.request.FILES)
        else:
            context['form'].initial['user'] = self.request.user
            basket_item = self.request.user.basket.all()
            if basket_item and basket_item.count():
                OrderFromSet = inlineformset_factory(Order, OrderItem,
                                                     form=OrderItemForm,
                                                     extra=basket_item.count())

                formset = OrderFromSet()
                for form, item in zip(formset.forms, basket_item):
                    form.initial['product'] = item.product
                    form.initial['quantity'] = item.quantity
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

        if self.object.total_cost == 0:
            self.object.delete()

        return order


class OrderUpdate(UpdateView):
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy('orders:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'зазазы/редактирование'
        OrderFromSet = inlineformset_factory(Order, OrderItem,
                                             form=OrderItemForm, extra=1)

        if self.request.POST:
            formset = OrderFromSet(self.request.POST, self.request.FILES,
                                   instance=self.object)
        else:
            formset = OrderFromSet(instance=self.object)
        context['orderitems'] = formset
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            order = super().form_valid(form)
            if orderitems.is_valid():
                orderitems.save()

            if self.object.total_cost == 0:
                self.object.delete()

            return order


class OrderDelete(DeleteView, PageTitleMixin):
    model = Order
    success_url = reverse_lazy('orders:index')
    page_title = 'заказы/удаление'


class OrderRead(DetailView, PageTitleMixin):
    model = Order
    page_title = 'заказы/просмотр'


def forming_complete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = Order.SENT_TO_PROCEED
    order.save()
    return HttpResponseRedirect(reverse('orders:index'))
