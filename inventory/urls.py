from django.urls import path
from . import views


urlpatterns = [

    path(
        '',
        views.home,
        name='home'
    ),

    path(
        'dashboard/',
        views.dashboard,
        name='dashboard'
    ),

    path(
        'products/',
        views.products,
        name='products'
    ),

    path(
        'products/add/',
        views.add_product,
        name='add_product'
    ),

    path(
        'product-search/',
        views.product_search,
        name='product_search'
    ),

    path(
        'inventory/',
        views.inventory,
        name='inventory'
    ),

    path(
        'inventory/update/<int:product_id>/',
        views.update_stock,
        name='update_stock'
    ),

    path(
        'stock-in/',
        views.stock_in,
        name='stock_in'
    ),

    path(
        'stock-out/',
        views.stock_out,
        name='stock_out'
    ),

    path(
        'orders/',
        views.orders,
        name='orders'
    ),

    path(
        'orders/add/',
        views.add_order,
        name='add_order'
    ),

    path(
        'orders/complete/<int:order_id>/',
        views.complete_order,
        name='complete_order'
    ),

    path(
        'orders/process-next/',
        views.process_next_order,
        name='process_next_order'
    ),

    path(
        'inventory-history/',
        views.inventory_history,
        name='inventory_history'
    ),

    path(
        'alerts/',
        views.alerts,
        name='alerts'
    ),

    path(
        'alerts/read/<int:alert_id>/',
        views.mark_alert_read,
        name='mark_alert_read'
    ),

    path(
        'alerts/resolve/<int:alert_id>/',
        views.resolve_alert,
        name='resolve_alert'
    ),

    path(
        'reports/',
        views.reports,
        name='reports'
    ),

    path(
        'analytics/',
        views.analytics,
        name='analytics'
    ),

]