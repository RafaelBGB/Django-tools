from django.urls import path
import adminapp.views as adminapp


app_name = 'adminapp'

urlpatterns = [
    path('users/create/', adminapp.AdminUserCreateView.as_view(),
         name='user_create'),
    path('users/read/', adminapp.AdminUserListView.as_view(),
         name='users'),
    path('users/update/<int:pk>/', adminapp.AdminUserUpdateView.as_view(),
         name='user_update'),
    path('users/delete/<int:pk>/', adminapp.AdminUserDeleteView.as_view(),
         name='user_delete'),

    path('categories/create/', adminapp.CategoryCreateView.as_view(),
         name='category_create'),
    path('categories/read/', adminapp.CategoryView.as_view(),
         name='categories'),
    path('categories/update/<int:pk>/', adminapp.CategoryUpdateView.as_view(),
         name='category_update'),
    path('categories/delete/<int:pk>/', adminapp.CategoryDeleteView.as_view(),
         name='category_delete'),

    path('products/create/category/<int:pk>/',
         adminapp.ProductCreateView.as_view(), name='product_create'),
    path('products/read/category/<int:pk>/',
         adminapp.ProductsCategoryView.as_view(), name='products_category'),
    path('products/read/<int:pk>/',
         adminapp.ProductDetailView.as_view(), name='product_read'),
    path('products/update/<int:pk>/',
         adminapp.ProductUpdateView.as_view(), name='product_update'),
    path('products/delete/<int:pk>/',
         adminapp.ProductDeleteView.as_view(), name='product_delete'),

    path('orders/', adminapp.AdminOrderList.as_view(), name='orders'),
    path('orders/update/<int:pk>/',
         adminapp.AdminOrderUpdate.as_view(), name='orders_update'),
    path('orders/delete/<int:pk>/',
         adminapp.AdminOrderDelete.as_view(), name='orders_delete'),
    path('orders/read/<int:pk>/',
         adminapp.AdminOrderRead.as_view(), name='orders_read'),
]
