from django.urls import path
from .views import ProfileView, ChangePasswordView, ProductAddView, ProductUpdateView


app_name = 'user'
urlpatterns = [
    path('', ProfileView.as_view(), name = 'profile'),
    path('change-password/', ChangePasswordView.as_view(), name = 'change-password'),
    path('product/add/', ProductAddView.as_view(), name='product-add'),
    path('product/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
]
