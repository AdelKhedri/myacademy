from django.urls import path
from .views import (Home, CourseFilterView, CourseCategoryView, CourseDetailsView, BookmarkView)


app_name = 'academy'
urlpatterns = [
    path('courses', CourseFilterView.as_view(), name='courseslist'),
    path('category/<slug:category_slug>', CourseCategoryView.as_view(), name='category'),
    path('bookmark/<str:content_type>/<int:course_id>/', BookmarkView.as_view(), name='bookmarker'),
    path('courses/<int:course_id>', CourseDetailsView.as_view(), name='course-details'),
    path('', Home.as_view(), name = 'home'),
]
