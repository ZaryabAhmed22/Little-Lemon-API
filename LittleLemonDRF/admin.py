from django.contrib import admin
from .models import Rating, MenuItem, Category, Order, OrderItem, Cart
# Register your models here.
admin.site.register(Rating)
admin.site.register(MenuItem)
admin.site.register(Cart)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
