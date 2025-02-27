from django.urls import path
from .views import (
    user_login, user_logout, admin_dashboard, product_list, product_create, product_update, product_delete, order_list, order_create, employee_orders, update_order_status, cancel_order, report_list, generate_sales_report, generate_low_stock_alert, custom_login_redirect
)

urlpatterns = [
    path('', custom_login_redirect, name='home'), # redirect each user into his own space if logged in, else it will redirect user to login 
    path('login/', user_login, name='login'), # Login page
    path('redirect_after_login/', custom_login_redirect, name="redirect_after_login"), # redirection for certain cases
    path('logout/', user_logout, name='logout'), # it just redirects you to login page
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'), # Admin dashboard
    path('products/', product_list, name='product_list'), # List of products
    path('products/create/', product_create, name='product_create'), # Add product's form
    path('products/<int:product_id>/edit/', product_update, name='product_update'), # Edit product
    path('products/<int:product_id>/delete/', product_delete, name='product_delete'), # Delete product
    path('orders/', order_list, name='order_list'), # List of orders
    path('orders/create/', order_create, name='order_create'), # Create order's form
    path('orders/my_orders/', employee_orders, name='employee_orders'), # Employye's order list
    path("orders/<int:order_id>/update-status/", update_order_status, name="update_order_status"), # Update order status (Only Admins)
    path("orders/<int:order_id>/cancel/", cancel_order, name="cancel_order"), # Cancel order (Only Employees)
    path('reports/', report_list, name='report_list'), # Reports list
    path('reports/generate_sales/', generate_sales_report, name='generate_sales_report'), # Generates sales reports (1 time a day)
    path('reports/generate_low_stock/', generate_low_stock_alert, name='generate_low_stock_alert'), # Generates low stock alerts
]