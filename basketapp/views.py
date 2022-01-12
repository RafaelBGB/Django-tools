from django.shortcuts import HttpResponseRedirect, render, get_object_or_404
from basketapp.models import Basket
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.template.loader import render_to_string
from django.http import JsonResponse


@login_required
def index(request):
    basket_items = request.user.basket.all().order_by('product__category')
    context = {
        'page_title': 'корзина',
        'basket_items': basket_items,
    }
    return render(request, 'basketapp/index.html', context)


@login_required
def add(request, product_pk):
    if 'login' in request.META.get('HTTP_REFERER'):
        return HttpResponseRedirect(reverse('main:product_page', args=[product_pk]))
    basket, _ = Basket.objects.get_or_create(user=request.user, product_id=product_pk)
    basket.quantity += 1
    basket.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def remove(request, pk):
    basket_record = get_object_or_404(Basket, pk=pk)
    basket_record.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def edit(request, pk, quantity):
    if request.is_ajax():
        quantity = int(quantity)
        new_basket_item = Basket.objects.get(pk=int(pk))

        if quantity > 0:
            new_basket_item.quantity = quantity
            new_basket_item.save()
        else:
            new_basket_item.delete()

        basket_item = request.user.basket.all().order_by('product__category')
        context = {
            'basket_items': basket_item,
        }
        result = render_to_string('basketapp/includes/inc_basket_list.html', context)
        return JsonResponse({'result': result})
