from django.conf import settings
from django.urls import reverse
from academy.models import Course
from .models import Cart, CartItem, Order
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import F, Sum
from django.db import transaction
from .utils import get_cart


class AddCourseToCartView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, content_type, course_id, *args, **kwargs):
        content_types = {
            'course': Course,
        }
        if content_type not in content_types.keys():
            raise Http404()
        
        course = get_object_or_404(content_types[content_type], id = course_id)
        cart_item = CartItem.objects.create(content_type = content_type, media_id = course_id, price = course.get_final_price())
        cart, created = Cart.objects.get_or_create(user = request.user, status = 'created')
        if cart_item not in cart.items.all():
            cart.items.add(cart_item)

        return redirect(request.GET.get('next', course.get_absolute_url()))


class RevmoveCourseFromCartView(LoginRequiredMixin, View):
    http_method_names = ['post']

    def post(self, request, content_type, course_id, *args, **kwargs):
        content_types = {
            'course': Course,
        }
        if content_type not in content_types.keys():
            raise Http404()

        cart_item = get_object_or_404(CartItem, content_type = content_type, media_id = course_id)
        cart, created = Cart.objects.get_or_create(user = request.user, status = 'created')
        if cart_item in cart.items.all():
            cart.items.remove(cart_item)
            cart_item.delete()

        return redirect(request.GET.get('next', cart_item.get_object().get_absolute_url()))


class CheckoutView(LoginRequiredMixin, View):
    template_name = 'cart/checkout.html'

    def dispatch(self, request, *args, **kwargs):
        cart, self.total_price, cart_courses = get_cart(request.user)

        self.context = {
            'cart_courses': cart_courses,
            'total_price': self.total_price,
        }
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        

        return render(request, self.template_name, self.context)


class PaymentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # order, created = Order.objects.get_or_create(user = request.user, status = 'created')
        cart, total_price, cart_courses = get_cart(request.user)

        try:
            with transaction.atomic():
                order, created = Order.objects.get_or_create(
                    user = request.user,
                    total_price = total_price,
                    status = 'pending',
                    cart = cart,
                    # payment_id = '' # payment id
                    )
                Cart.objects.filter(user = request.user, status = 'created').update(status = 'pending')
                # user.balance -= total_price
                # user.save()

                cart.status = 'pending'
                cart.save()

            user = request.user
            if settings.BYPASS_SHOPPING or user.balance >= total_price:
                with transaction.atomic():
                    order.status = 'paid'
                    order.save()

                    if not settings.BYPASS_SHOPPING:
                        user.balance -= total_price
                        user.save()
                # TODO: redirect to bought products url
                return redirect('academy:home')
            else:
                return redirect('academy:home') # redirect to paymend url
        except Exception as ex:
            print('ERROR: In Checkout view in POST method in save order.')
            print(ex)
            return redirect('academy:home') # redirect to paymend url

