from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db.models import F

from authapp.models import ShopUser
from mainapp.models import Product, ProductCategory
from authapp.forms import ShopUserRegisterForm
from adminapp.forms import AdminShopUserUpdateForm, ProductEditForm, \
    ProductCategoryEditForm, AdminOrdersEditForm
from ordersapp.models import Order
from mixins.mixins import SuperUserOnlyMixin, PageTitleMixin, GetSuccessUrlMixin


class AdminUserListView(SuperUserOnlyMixin, PageTitleMixin, ListView):
    model = ShopUser
    page_title = 'админка/пользователи'


class AdminUserCreateView(SuperUserOnlyMixin, PageTitleMixin, CreateView):
    model = ShopUser
    form_class = ShopUserRegisterForm
    success_url = reverse_lazy('admin:users')
    page_title = 'админка/пользователи/создание'


class AdminUserUpdateView(SuperUserOnlyMixin, PageTitleMixin, UpdateView):
    model = ShopUser
    form_class = AdminShopUserUpdateForm
    success_url = reverse_lazy('admin:users')
    page_title = 'админка/пользователи/редактирование'


class AdminUserDeleteView(SuperUserOnlyMixin, PageTitleMixin, DeleteView):
    model = ShopUser
    success_url = reverse_lazy('admin:users')
    page_title = 'админка/пользователи/удаление'


class CategoryCreateView(SuperUserOnlyMixin, PageTitleMixin, CreateView):
    model = ProductCategory
    form_class = ProductCategoryEditForm
    success_url = reverse_lazy('admin:categories')
    page_title = 'админка/категории/создание'


class CategoryUpdateView(SuperUserOnlyMixin, PageTitleMixin, UpdateView):
    model = ProductCategory
    form_class = ProductCategoryEditForm
    success_url = reverse_lazy('admin:categories')
    page_title = 'админка/категории/редактирование'

    def form_valid(self, form):
        if 'discount' in form.cleaned_data:
            discount = form.cleaned_data['discount']
            if discount:
                self.object.category.update(
                    price=F('price') * (1 - discount / 100)
                )
        return super().form_valid(form)


class CategoryView(SuperUserOnlyMixin, PageTitleMixin, ListView):
    model = ProductCategory
    page_title = 'админка/категории'


class CategoryDeleteView(SuperUserOnlyMixin, PageTitleMixin, DeleteView):
    model = ProductCategory
    success_url = reverse_lazy('admin:categories')
    page_title = 'админка/категории/удаление'


class ProductCreateView(SuperUserOnlyMixin, PageTitleMixin, GetSuccessUrlMixin,
                        CreateView):
    model = Product
    form_class = ProductEditForm
    page_title = 'админка/продукты/создание'

    def get_initial(self):
        return {'category': get_object_or_404(ProductCategory,
                                              pk=self.kwargs['pk'])}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_id'] = self.kwargs['pk']
        return context


class ProductsCategoryView(SuperUserOnlyMixin, PageTitleMixin, ListView):
    model = Product
    page_title = 'админка/продукты категории'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(ProductCategory,
                                                pk=self.kwargs['pk'])
        return context

    def get_queryset(self):
        return Product.objects.filter(category__pk=self.kwargs['pk']).order_by(
            'name')


class ProductDetailView(SuperUserOnlyMixin, PageTitleMixin, DetailView):
    model = Product
    page_title = 'админка/продукт'


class ProductUpdateView(SuperUserOnlyMixin, PageTitleMixin, GetSuccessUrlMixin,
                        UpdateView):
    model = Product
    form_class = ProductEditForm
    page_title = 'админка/продукты/редактирование'


class ProductDeleteView(SuperUserOnlyMixin, PageTitleMixin, GetSuccessUrlMixin,
                        DeleteView):
    model = Product
    page_title = 'админка/продукты/удаление'


class AdminOrderList(PageTitleMixin, ListView):
    model = Order
    page_title = 'админка/заказы'
    template_name = 'ordersapp/orders_list.html'


class AdminOrderUpdate(UpdateView):
    model = Order
    form_class = AdminOrdersEditForm
    success_url = reverse_lazy('admin:orders')
    template_name = 'ordersapp/orders_form.html'
    page_title = 'админка/заказы/редактирование'


class AdminOrderDelete(PageTitleMixin, DeleteView):
    model = Order
    success_url = reverse_lazy('admin:orders')
    template_name = 'ordersapp/orders_confirm_delete.html'
    page_title = 'админка/заказы/удаление'

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(self.success_url)


class AdminOrderRead(DetailView):
    model = Order
    template_name = 'ordersapp/orders_detail.html'
    page_title = 'админка/заказы/просмотр'


@receiver(pre_save, sender=ProductCategory)
def product_is_active_update_productcategory_save(sender, instance, **kwargs):
    if instance.pk:
        if instance.is_active:
            instance.category.update(is_active=True)
        else:
            instance.category.update(is_active=False)
