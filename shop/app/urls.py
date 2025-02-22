from django.urls import path
from .views import (
    signup_view, login_view, owner_dashboard, customer_dashboard, purchase_product, admin_dashboard,product_detail,product_list,add_product
)

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('owner_dashboard/', owner_dashboard, name='owner_dashboard'),
    path('customer_dashboard/', customer_dashboard, name='customer_dashboard'),
    path('purchase/<int:product_id>/', purchase_product, name='purchase_product'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),  # Admin Panel
    path('products/', product_list, name='product_list'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
     path('add_product/', add_product, name='add_product'),
]
