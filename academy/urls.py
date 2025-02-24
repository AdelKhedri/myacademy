from django.urls import path
from .views import RegisterView, ActivateRegisterdAccountView, LoginView, Home, ForgotPasswordView


app_name = 'academy'
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/active-account/', ActivateRegisterdAccountView.as_view(), name='active-account'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('', Home, name = 'home')
]