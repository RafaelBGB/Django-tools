from django.urls import path
import mainapp.views as mainapp

app_name = 'mainapp'

urlpatterns = [
    path('', mainapp.main, name="index"),
    path('contact/', mainapp.contact, name="contact"),
    path('products/', mainapp.products, name='products'),
    path('category/<int:pk>/', mainapp.products, name='category'),
    path('category/<int:pk>/page/<int:page>/', mainapp.products, name='page'),
    path('products/<int:pk>/', mainapp.product_page, name='product_page'),
]
