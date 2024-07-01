from django.contrib import admin
from .models import Product, Category, Order, OrderItem

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'discounted_price', 'product_image')
    search_fields = ('title', 'category__name')
    list_filter = ('category',)

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('user__username',)

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__title')

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
