from django.urls import path
import basketapp.views as basketapp


app_name = 'basketapp'

urlpatterns = [
    path('', basketapp.index, name='index'),
    path('add/<int:product_pk>', basketapp.add, name='add'),
    path('remove/<int:pk>', basketapp.remove, name='remove'),
    path('edit/<int:pk>/<int:quantity>/', basketapp.edit, name='edit'),
]
