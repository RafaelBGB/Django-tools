from random import sample
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache

from geekshop.settings import LOW_CACHE
from mainapp.models import ProductCategory, Product


def get_links_menu():
    if LOW_CACHE:
        key = 'links_menu'
        links_menu = cache.get(key)
        if links_menu is None:
            links_menu = ProductCategory.objects.filter(is_active=True)
            cache.set(key, links_menu)
        return links_menu
    return ProductCategory.objects.filter(is_active=True)


def get_category(pk):
    if LOW_CACHE:
        key = f'category_{pk}'
        category = cache.get(key)
        if category is None:
            category = get_object_or_404(ProductCategory, pk=pk)
            cache.set(key, category)
        return category
    return get_object_or_404(ProductCategory, pk=pk)


def get_products():
    if LOW_CACHE:
        key = 'products'
        product = cache.get(key)
        if product is None:
            product = Product.objects.filter(is_active=True, category__is_active=True).select_related('category')
            cache.set(key, product)
        return product
    return Product.objects.filter(is_active=True, category__is_active=True).select_related('category')


def get_hot_product():
    product = get_products()
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
    if pk is not None:
        if pk == 0:
            category = {
                'pk': 0,
                'name': 'все',
            }
            products_list = get_products()
        else:
            category = get_category(pk)
            products_list = Product.objects.filter(category__pk=pk, is_active=True, category__is_active=True).\
                order_by('price')

        paginator = Paginator(products_list, 2)
        try:
            product_paginator = paginator.page(page)
        except PageNotAnInteger:
            product_paginator = paginator.page(1)
        except EmptyPage:
            product_paginator = paginator.page(paginator.num_pages)

        context = {
                'page_title': 'товары категории',
                'links_menu': get_links_menu(),
                'category': category,
                'products_list': product_paginator,
            }
        return render(request, "mainapp/category_products.html", context)

    hot_product = get_hot_product()
    context = {
        'page_title': 'продукты',
        'links_menu': get_links_menu(),
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
        'product': product,
        # 'categories': get_category(product.category.pk),
    }
    return render(request, 'mainapp/product_page.html', context)
