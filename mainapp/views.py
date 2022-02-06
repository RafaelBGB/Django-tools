from random import sample
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import ProductCategory, Product


def get_categories():
    return ProductCategory.objects.all()


def get_hot_product():
    product = Product.objects.all()
    return sample(list(product), 1)[0]


def get_same_products(hot_product):
    same_product = Product.objects.filter(category=hot_product.category).exclude(pk=hot_product.pk)[:3]
    return same_product


def main(request):
    products_list = Product.get_items()
    context = {
        'page_title': 'главная',
        'products_list': products_list
    }
    return render(request, "mainapp/index.html", context)


def products(request, pk=None, page=1):
    link_menu = ProductCategory.objects.filter(is_active=True)

    if pk is not None:
        if pk == 0:
            category = {
                'pk': 0,
                'name': 'все',
            }
            products_list = Product.objects.filter(is_active=True, category__is_active=True).order_by('price')
        else:
            category = get_object_or_404(ProductCategory, pk=pk)
            products_list = Product.objects.filter(category__pk=pk, is_active=True, category__is_active=True).order_by('price')

        paginator = Paginator(products_list, 2)
        try:
            product_paginator = paginator.page(page)
        except PageNotAnInteger:
            product_paginator = paginator.page(1)
        except EmptyPage:
            product_paginator = paginator.page(paginator.num_pages)

        context = {
                'page_title': 'товары категории',
                'links_menu': link_menu,
                'category': category,
                'products_list': product_paginator,
            }
        return render(request, "mainapp/category_products.html", context)

    hot_product = get_hot_product()
    context = {
        'page_title': 'продукты',
        'links_menu': get_categories(),
        'hot_product': hot_product,
        'same_products': get_same_products(hot_product),
    }
    return render(request, "mainapp/products.html", context)


def contact(request):
    context = {'page_title': 'контакты'}
    return render(request, "mainapp/contact.html", context)


def product_page(request, pk):
    product = get_object_or_404(Product, pk=pk)
    context = {
        'page_title': 'старница продукта',
        'links_menu': get_categories(),
        'product': product,
        'categories': get_categories(),
    }
    return render(request, 'mainapp/product_page.html', context)
