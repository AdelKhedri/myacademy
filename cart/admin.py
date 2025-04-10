from django.contrib import admin
from .models import Cart, CartItem, Order


@admin.register(CartItem)
class CartItemRegister(admin.ModelAdmin):
    list_display = ['content_type', 'media_id', 'price']
    list_filter = ['content_type']


@admin.register(Cart)
class CartRegister(admin.ModelAdmin):
    list_display = ['id', 'status', 'user', 'get_items_count']
    list_display_links = ['id', 'status']
    list_filter = ['status']
    filter_horizontal = ['items']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related('items')

    @admin.display()
    def get_items_count(self, obj):
        return obj.items.count()


@admin.register(Order)
class OrderRegister(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'payment_id', 'created_at']
    list_display_links = ['id', 'user']
    list_filter = ['status']
    list_select_related = ['cart', 'user']