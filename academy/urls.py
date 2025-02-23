from django.urls import path
from .views import RegisterView, LoginView, Home


app_name = 'academy'
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('', Home, name = 'home')
]