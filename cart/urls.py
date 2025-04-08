from django.urls import path
from .views import AddCourseToCartView, CheckoutView, RevmoveCourseFromCartView

app_name = 'cart'
urlpatterns = [
    path('add/<str:content_type>/<int:course_id>/', AddCourseToCartView.as_view(), name='cart-add'),
    path('remove/<str:content_type>/<int:course_id>/', RevmoveCourseFromCartView.as_view(), name='cart-remove'),
    path('checkout/', CheckoutView.as_view(), name='cart-checkout'),
]