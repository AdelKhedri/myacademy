from django.urls import path
from .views import RegisterView, ActivateRegisterdAccountView, LoginView, Home


app_name = 'academy'
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('', Home, name = 'home')
]