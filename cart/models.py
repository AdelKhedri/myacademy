from django.db import models
from user.models import User
from academy.models import Course
from django.utils.translation import gettext_lazy as _


class CartItem(models.Model):
    class ContentTypes(models.TextChoices):
        course = 'course', 'دوره ویدیویی'
        files = 'files', 'فایل'

    content_type = models.CharField(_("نوع دوره"), choices=ContentTypes.choices, default=ContentTypes.course, max_length=6)
    media_id = models.IntegerField(_("ایدی دوره"))
    price = models.IntegerField(_("قیمت"))

    class Meta:
        verbose_name = 'آیتم سبد خرید'
        verbose_name_plural = 'آیتم های سبد خرید'

    def get_object(self):
        content_type = {
            'course': Course,
        }
        return content_type[self.content_type].objects.get(id=self.media_id) if self.content_type in content_type.keys() else None

    def __str__(self):
        return f'{self.content_type} : {self.media_id}'


class Cart(models.Model):
    status_list = (('created', 'ساخته شده'), ('pending', 'در انتظار'), ('paid', 'پرداخت شده'))
    status = models.CharField(_("وضعیت"), choices = status_list, default='created', max_length=7)
    items = models.ManyToManyField(CartItem, verbose_name=_("دوره ها"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("کاربر"))

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبد های خرید'

    def __str__(self):
        return self.user.__str__() + " : " + self.get_status_display()


class Order(models.Model):
    status_types = (('pending', 'در انتظار پرداخت'),
                    ('payed', 'پرداخت شده'),
                    ('failed', 'ناموفق'),)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('دانشجو'))
    total_price = models.IntegerField(_('قیمت کل'), blank=True, null=True)
    created_at = models.DateTimeField(_('زمان درخواست پرداخت'), auto_now_add=True)
    status = models.CharField(_('وضعت پرداخت'), choices=status_types, max_length=7, default='pending')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, verbose_name=_('سبد خرید'))
    payment_id = models.CharField(_("ای دی پرداخت"), max_length=100, blank=True)

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبد های خرید'
        ordering = ['pk']

    def __str__(self):
        return f'{self.id} - {self.user.__str__()} - {self.get_status_display()}'
