from django.contrib import admin
from .models import Course, Seasion, Lesson, Category, Comment
from django.utils.html import format_html

@admin.register(Course)
class CourseRegister(admin.ModelAdmin):
    list_display = ['name', 'get_category', 'teacher', 'get_final_price', 'is_active', 'get_thumbnail']
    list_filter = ['is_active', 'is_askable', 'is_certificate']
    list_select_related = ['teacher',]
    filter_horizontal = ['category', 'seasions', 'related_course']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('category', 'seasions', 'related_course')

    @admin.display
    def get_thumbnail(self, obj):
        return format_html(f'</img style="width:70px;heigth:70px;" src="{obj.thumbnail.url}">')

    @admin.display
    def get_category(self, obj):
        return format_html(f'<span class="">{obj.category.name if obj.category.name else ""}</span>')


@admin.register(Seasion)
class SeasionRegister(admin.ModelAdmin):
    list_display = [field.name for field in Seasion._meta.fields]
    filter_horizontal = ['lessons']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('lessons')


@admin.register(Lesson)
class LessonRegister(admin.ModelAdmin):
    list_display = [field.name for field in Lesson._meta.fields]
    list_select_related = ['teacher']


@admin.register(Category)
class CategoryRegister(admin.ModelAdmin):
    list_display = [field.name for field in Category._meta.fields]


@admin.register(Comment)
class CommentRegister(admin.ModelAdmin):
    list_display = [field.name for field in Comment._meta.fields]
    list_select_related = ['user', 'parent']
