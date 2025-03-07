from django.urls import path
from .views import ProfileView, ChangePasswordView, CourseAddView, CourseUpdateView, MyCourseView, MyCourseNotPublishedView, CourseDeleteView


app_name = 'user'
urlpatterns = [
    path('', ProfileView.as_view(), name = 'profile'),
    path('change-password/', ChangePasswordView.as_view(), name = 'change-password'),
    path('course/add/', CourseAddView.as_view(), name='course-add'),
    path('course/<int:pk>/update/', CourseUpdateView.as_view(), name='course-update'),
    path('course/<int:pk>/delete/', CourseDeleteView.as_view(), name='course-delete'),
    path('my-course/', MyCourseView.as_view(), name='my-courses'),
    path('my-course/pending/', MyCourseNotPublishedView.as_view(), name='my-courses-not-published'),
]
