from django.apps import AppConfig
from django.core.signals import setting_changed

class AcademyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'academy'

    def ready(self):
        from .signals import limit_category_instance, limit_course_instance, limit_courses_count
        setting_changed.connect(limit_category_instance)
        setting_changed.connect(limit_course_instance)
        setting_changed.connect(limit_courses_count)
        return super().ready()