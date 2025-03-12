from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from user.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from .managers import CommentManager
from django.db.models import Count


class Course(models.Model):
    name = models.CharField(_("نام"), max_length=300)
    category = models.ManyToManyField('Category', blank=True, verbose_name=_('دسته بندی'))
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('مدرس'))
    description = models.TextField(_('درباره دوره'))
    seasions = models.ManyToManyField('Seasion', blank=True, verbose_name=_('فصل ها'))
    price= models.IntegerField(_('قیمت'), default=0)
    price_with_discount = models.IntegerField(_('قیمت با تخفیف'), blank=True, null=True)
    tax = models.DecimalField(_('مالیات'), max_digits=4, decimal_places=2, default=0.0, help_text='درصد مالیات')
    related_course = models.ManyToManyField('self', blank=True, verbose_name=_('دوره های مرتبط'))
    thumbnail = models.ImageField(_('عکس'), upload_to='courses/images/')
    time = models.TimeField(_('زمان'))
    skils_type = (('j', 'مبتدی'), ('m', 'متوسط'), ('s', 'پیشرفته'))
    difficulty_level = models.CharField(_('سظح مهارت'), default='j', choices=skils_type, max_length=1)
    is_certificate = models.BooleanField(_('دارای مدرک'), default=True)
    trailer = models.FileField(_('ویدیو معرفی'), blank=True, upload_to='courses/trailer/')
    is_askable = models.BooleanField(_('اجازه پرسش و پاسخ'), default=True)
    is_active = models.BooleanField(_('فعال'), help_text='وضعیت نمایش به دانشجو', default=False)
    updated_at = models.DateTimeField(_('اپدیت شده در'), auto_now=True)
    created_at = models.DateTimeField(_('زمان ساخت'), auto_now_add=True)


    class Meta:
        verbose_name = 'دوره'
        verbose_name_plural = 'دوره ها'
        ordering = ['is_active', 'created_at']

    def lessons_count(self):
        return self.seasions.annotate(lessons_count = Count('lessons')).aggregate(count = Count('lessons_count'))['count']
    
    def get_final_price(self):
        return self.price_with_discount + (self.price // 100 * self.tax) if self.price_with_discount else self.price + (self.price // 100 * self.tax)

    def get_absolute_url(self):
        return reverse('academy:course-details', args=[self.pk])

    def __str__(self):
        return self.name


class Comment(models.Model):
    comment_class = (('course', 'دوره'),)
    media_id = models.IntegerField(_('ایدی مدیا'))
    media_type = models.CharField(_('نوع'), default='course', max_length=10, choices=comment_class)
    message = models.TextField(_('پیام'))
    parent  = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name=_('کامنت والد'))
    created_at = models.DateTimeField(_('زمان ارسال'), auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('کاربر'))
    active = models.BooleanField(_('وضعیت'), default=False)
    objects = CommentManager()

    def get_media(self, obj):
        objects = {
            'course': Course,
        }
        return objects[obj].objects.get(id = self.media_id)
    
    class Meta:
        verbose_name = 'کامنت'
        verbose_name_plural = 'کامنت ها'
        ordering = ['active', 'created_at']

    def __str__(self):
        return f'{self.user.__str__()}:{self.pk}'


class Category(models.Model):
    title = models.CharField(_('موضوع'), max_length=250)
    slug = models.SlugField(_('سلاگ'), max_length=300, unique=True)

    class Meta:
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'
        ordering = ['title']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(_('نام درس'), max_length=200)
    description = models.TextField(_('درباره این قسمت'))
    file = models.FileField(_('فلیم'), upload_to='courses/lessons/files/')
    attached = models.FileField(_('پیوست'), blank=True)
    time = models.TimeField(_('زمان'), blank=True, null=True)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('مدرس'))
    is_free = models.BooleanField(_('رایگان'), default=False)

    class Meta:
        verbose_name = 'درس'
        verbose_name_plural = 'درس ها'
        ordering = ['title']

    def __str__(self):
        return self.title


class Seasion(models.Model):
    title = models.CharField(_('موضوع'), max_length=250)
    lessons = models.ManyToManyField(Lesson, blank=True, verbose_name=_('درس ها'))

    class Meta:
        verbose_name = 'فصل'
        verbose_name_plural = 'فصل ها'
        ordering = ['id']

    def __str__(self):
        return self.title


class PurchedCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('دانشجو'))
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name=_('دروه'))
    amount = models.IntegerField(_('قیمت'))
    time = models.DateTimeField(_('زمان خرید'), auto_now_add=True)

    class Meta:
        verbose_name = 'دروه خریداری شده'
        verbose_name_plural = 'دروه های خریداری شده'
        ordering = ['time']

    def __str__(self):
        return self.user.__str__()
