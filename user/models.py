from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .validators import validate_phone_number, validate_username
from .managers import UserManager


class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(_('ایمیل'), unique=True)
    phone_number = models.CharField(_('شماره تلفن'), max_length=11, unique=True, validators=[validate_phone_number])
    username = models.CharField(_('نام کاربری'), max_length=100, unique=True, validators=[validate_username])
    is_active = models.BooleanField(_('اجازه ورود'), default=False)
    is_teacher = models.BooleanField(_('معلم'), default=False)
    balance = models.IntegerField(_('موجودی'), default=0)

    REQUIRED_FIELDS = ['email', 'phone_number']
    objects = UserManager()

    def __str__(self):
        return self.get_full_name() if self.get_full_name() else self.username


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('کاربر'))
    picture = models.ImageField('users/profile', blank=True)
    aboute = models.TextField(_('درباره'), blank=True)

    class Meta:
        verbose_name = 'پروفایل'
        verbose_name_plural = 'پروفایل ها'

    def __str__(self):
        return self.user.__str__()


class OTPCode(models.Model):
    code = models.IntegerField(_('کد'))
    phone_number = models.CharField(_('شماره تلفن'), max_length=11, validators=[validate_phone_number], unique=True)
    expire_time = models.DateTimeField(_('زمان ارسال کد'))
    code_types = (('register', 'ثبت نام'),('forgot-password', 'فراموشی رمز عبور'))
    code_type = models.CharField(_('نوع کد تایید'), choices=code_types, max_length=15)

    class Meta:
        verbose_name = 'کد تایید '
        verbose_name_plural = 'کد های تایید '

    def __str__(self):
        return '{}:{}:{}'.format(self.phone_number, self.code, self.expire_time)
