from user.models import User
from .models import Cart

def get_cart(user: User):
    cart, created = Cart.objects.get_or_create(user = user, status = 'created')
    cart_courses = cart.items.all()
    total_price = 0
    for course in cart_courses:
        total_price += course.price
    return cart, total_price, cart_courses