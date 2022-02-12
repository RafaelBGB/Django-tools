from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse, reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator

from authapp.models import ShopUser
from mainapp.models import Product, ProductCategory
from authapp.forms import ShopUserRegisterForm
from adminapp.forms import AdminShopUserUpdateForm, ProductEditForm, \
    ProductCategoryEditForm


class SuperUserOnlyMixin:
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class PageTitleMixin:
    page_title_key = 'page_title'
    page_title = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[self.page_title_key] = self.page_title
        return context


class GetSuccessUrlMixin:
    def get_success_url(self):
        return reverse('admin:products_category',
                       args=[self.object.category_id])


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
        return Product.objects.filter(category__pk=self.kwargs['pk']).\
            order_by('name')


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





