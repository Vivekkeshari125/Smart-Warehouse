from django.contrib import admin
from .models import Product, Order, StockTransaction, Alert


admin.site.register(Product)

admin.site.register(Order)

admin.site.register(StockTransaction)

admin.site.register(Alert)