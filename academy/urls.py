from django.urls import path
from .views import (RegisterView, ActivateRegisterdAccountView, LoginView, Home, ForgotPasswordView, ConfirmForgotPasswordView,
                    LogoutView, CourseFilterView, CourseCategoryView)


app_name = 'academy'
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('register/active-account/', ActivateRegisterdAccountView.as_view(), name='active-account'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('forgot-password/confirm/', ConfirmForgotPasswordView.as_view(), name='confirm-forgot-password'),
    path('courses', CourseFilterView.as_view(), name='courseslist'),
    path('category/<slug:category_slug>', CourseCategoryView.as_view(), name='category'),
    path('', Home, name = 'home')
]
