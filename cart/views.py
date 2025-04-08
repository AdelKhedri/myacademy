from django.urls import reverse
from academy.models import Course
from .models import Cart, CartItem, Order
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import F, Sum
from django.db import transaction


class AddCourseToCartView(View, LoginRequiredMixin):
    http_method_names = ['post']

    def post(self, request, content_type, course_id, *args, **kwargs):
        content_types = {
            'course': Course,
        }
        if content_type not in content_types.keys():
            raise Http404()
        
        course = get_object_or_404(content_types[content_type], id = course_id)
        cart_item = CartItem.objects.create(content_type = content_type, media_id = course_id, price = course.get_final_price())
        cart, created = Cart.objects.get_or_create(user = request.user, status = 'pending')
        if cart_item not in cart.items.all():
            cart.items.add(cart_item)

        return redirect(request.GET.get('next', course.get_absolute_url()))


class RevmoveCourseFromCartView(View, LoginRequiredMixin):
    http_method_names = ['post']

    def post(self, request, content_type, course_id, *args, **kwargs):
        content_types = {
            'course': Course,
        }
        if content_type not in content_types.keys():
            raise Http404()

        cart_item = get_object_or_404(CartItem, content_type = content_type, media_id = course_id)
        cart, created = Cart.objects.get_or_create(user = request.user, status = 'pending')
        if cart_item in cart.items.all():
            cart.items.remove(cart_item)
            cart_item.delete()

        return redirect(request.GET.get('next', cart_item.get_object().get_absolute_url()))


class CheckoutView(View, LoginRequiredMixin):
    template_name = 'cart/checkout.html'

    def dispatch(self, request, *args, **kwargs):
        cart, created = Cart.objects.get_or_create(user = request.user, status = 'pending')
        cart_courses = cart.items.all()
        self.total_price = 0
        for course in cart_courses:
            self.total_price += course.price

        self.context = {
            'cart_courses': cart_courses,
            'total_price': self.total_price,
        }
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        # TODO: add discount coupon
        order, created = Order.objects.get_or_create(user = request.user, status = 'pending')
        try:
            with transaction.atomic():
                order.total_price = self.total_price
                order.save()
                Cart.objects.filter(user = request.user, status = 'pending').update(status = 'paid')
        except:
            print('ERROR: In Checkout view in POST method in save order.')

        return render(request, self.template_name, self.context)
