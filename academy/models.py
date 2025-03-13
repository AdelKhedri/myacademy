from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from user.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from .managers import CommentManager
from django.db.models import Count, Sum


class Course(models.Model):
    name = models.CharField(_("نام"), max_length=300)
    category = models.ManyToManyField('Category', blank=True, related_name='courses', verbose_name=_('دسته بندی'))
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
        return self.seasions.annotate(lessons_count = Count('lessons')).aggregate(count = Sum('lessons_count'))['count'] or 0
    
    def get_final_price(self):
        return int(self.price_with_discount + (self.price // 100 * self.tax) if self.price_with_discount else self.price + (self.price // 100 * self.tax))

    def get_absolute_url(self):
        return reverse('academy:course-details', args=[self.pk])

    def get_purch_url(self):
        return reverse('academy:cart-add', args=[self.pk])

    def get_remove_from_cart(self):
        return reverse('academy:cart-remove', args=[self.pk])

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

    def get_active_courses_count(self):
        return self.courses.filter(is_active = True).count()

    def get_absolute_url(self):
        return reverse('academy:category', args=[self.slug])

    def __str__(self):
        return self.title


class Team(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('کاربر'))
    social_telegram = models.URLField(_('ادرس تلگرام'), blank=True)
    social_rubika = models.URLField(_('ادرس روبیکا'), blank=True)
    social_instagram = models.URLField(_('ادرس اینستاگرام'), blank=True)
    social_github = models.URLField(_('ادرس گیتهاب'), blank=True)
    image = models.ImageField(_('عکس کاربر'), blank=True, upload_to='users/team/profiles/', help_text='260px * 350px none background')
    position = models.TextField(_('سِمَت'), max_length=150)

    class Meta:
        verbose_name = 'عضو تیم'
        verbose_name_plural = 'اعضای تیم'
        ordering = ['id']

    def __str__(self):
        return self.user.__str__()


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


class MainPageCategoryAdd(models.Model):
    title = models.CharField(_('نام تبلیغاتی دسته بندی '), max_length=150)
    image = models.ImageField(_('عکس تبلیغاتی دسته بندی'), upload_to='categorys/images/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('دسته بندی'))

    class Meta:
        verbose_name = 'دسته بندی تبلیغاتی صفحه خانه'
        verbose_name_plural = 'دسته بندی های تبلیغاتی صفحه خانه'
        ordering = ['id']

    def __str__(self):
        return self.title


class MainPageCourseAdd(models.Model):
    title = models.CharField(_('نام تب محصولات '), max_length=150)
    courses = models.ManyToManyField(Course, verbose_name=_('دسته بندی'))

    class Meta:
        verbose_name = 'محصول تبلیغاتی صفحه خانه'
        verbose_name_plural = 'محصولات تبلیغاتی صفحه خانه'
        ordering = ['id']

    def __str__(self):
        return self.title


class Order(models.Model):
    status_types = (('pending', 'در انتظار پرداخت'),
                    ('paid', 'پرداخت شده'),
                    ('failed', 'ناموفق'),)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('دانشجو'))
    total_price = models.IntegerField(_('قیمت کل'))
    created_at = models.DateTimeField(_('زمان ساخت سبد خرید'), auto_now_add=True)
    status = models.CharField(_('وضعت پرداخت'), max_length=7, default='pending')

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبد های خرید'
        ordering = ['pk']

    def __str__(self):
        return f'{self.id} - {self.user.__str__()} - {self.get_status_display()}'


class OrderItem(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name=_('دوره'))
    price = models.IntegerField(_('قیمت'))


    class Meta:
        verbose_name = 'ایتم خرید اری شده'
        verbose_name_plural = 'ایتم های خریداری شده'

    def __str__(self):
        return self.course.__str__()
