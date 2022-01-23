from django.urls import path
import ordersapp.views as ordersapp


app_name = 'ordersapp'

urlpatterns = [
    path('', ordersapp.OrderList.as_view(), name='index'),
    path('create/', ordersapp.OrderCreate.as_view(), name='create'),
    path('update/<int:pk>/', ordersapp.OrderUpdate.as_view(), name='update'),
    path('delete/<int:pk>/', ordersapp.OrderDelete.as_view(), name='delete'),
    path('read/<int:pk>/', ordersapp.OrderRead.as_view(), name='read'),
    path('complate/<int:pk>/', ordersapp.forming_complete, name='complete'),
]
