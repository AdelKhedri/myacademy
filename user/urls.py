from django.urls import path
from .views import (LoginView, LogoutView, RegisterView, ActivateRegisterdAccountView, ForgotPasswordView, ConfirmForgotPasswordView)


app_name = 'user'
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('register/active-account/', ActivateRegisterdAccountView.as_view(), name='active-account'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('forgot-password/confirm/', ConfirmForgotPasswordView.as_view(), name='confirm-forgot-password'),
]
