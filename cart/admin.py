from django.contrib import admin
from .models import Cart, CartItem


@admin.register(CartItem)
class CartItemRegister(admin.ModelAdmin):
    list_display = ['content_type', 'media_id', 'price']
    list_filter = ['content_type']


@admin.register(Cart)
class CartRegister(admin.ModelAdmin):
    list_display = ['status', 'user', 'get_items_count']
    list_filter = ['status']
    filter_horizontal = ['items']

    @admin.display()
    def get_items_count(self, obj):
        return obj.items.count()
