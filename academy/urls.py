from django.urls import path
from .views import RegisterView


urlpatterns = [
    path('login/', RegisterView.as_view(), name='login'),
]