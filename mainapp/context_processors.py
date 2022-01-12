from basketapp.models import Basket


def get_basket(request):
    basket = []
    if request.user.is_authenticated:
        basket = Basket.objects.filter(user=request.user)

    return {'basket': basket,}
