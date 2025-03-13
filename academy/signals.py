from django.db.models.signals import pre_save, m2m_changed
from django.dispatch import receiver
from django.forms import ValidationError
from .models import MainPageCourseAdd, MainPageCategoryAdd

@receiver(pre_save, sender=MainPageCourseAdd)
def limit_course_instance(sender, instance, **kwargs):
    if sender.objects.count() >= 4:
        raise ValidationError('تعداد تب های محصولات تبلیغاتی صفحه اصلی نمیتواند بیشتر از4 تب باشد')

@receiver(pre_save, sender=MainPageCategoryAdd)
def limit_category_instance(sender, instance, **kwargs):
    if sender.objects.count() >= 4:
        raise ValidationError('تعداد دسته بندی های تبلیغاتی صفحه اصلی نمیتواند بیشتر از4 دسته باشد.')

@receiver(m2m_changed, sender=MainPageCourseAdd.courses.through)
def limit_courses_count(sender, instance, action, **kwargs):
    if action in ['pre_add', 'pre_set'] and instance.courses.count() + len(kwargs.get('pk_set', [])) > 6:
        raise ValidationError('تعداد محصولات هر تب نمیتواند بیشتر از 6 محصول باشد.')
