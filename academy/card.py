from django.conf import settings

from .models import Course


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(settings.CART_SESSION_ID, {})

    def add(self, product_id):
        product_id = str(product_id)
        if product_id not in self.cart:
            self.cart[product_id] = product_id
            self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def get_courses(self):
        return Course.objects.filter(id__in = self.cart.values())

    def clean(self):
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def __iter__(self):
        for product in Course.objects.filter(id__in = self.cart.values()):
            yield product
