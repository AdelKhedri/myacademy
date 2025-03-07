from django.urls import path
from .views import ProfileView, ChangePasswordView, CourseAddView, CourseUpdateView


app_name = 'user'
urlpatterns = [
    path('', ProfileView.as_view(), name = 'profile'),
    path('change-password/', ChangePasswordView.as_view(), name = 'change-password'),
    path('course/add/', CourseAddView.as_view(), name='course-add'),
    path('course/<int:pk>/update/', CourseUpdateView.as_view(), name='course-update'),
]
