from django.contrib import admin
from .models import OTPCode, User, Profile
from django.contrib.auth.admin import UserAdmin


@admin.register(User)
class UserRegister(UserAdmin):
    list_display = ['username', 'email', 'phone_number', 'is_active', 'is_mentor', 'is_superuser', 'balance']
    search_fields = ['email', 'username', 'phone_number']
    ordering = ['id']

    fieldsets = (
        (
            None,
            {'fields': [('email', 'username'), 'password']}
        ),
        (
            'اطلاعات شخصی',
            {'fields': ('phone_number',)}
        ),
        (
            'مجوز ها',
            {'fields': [('is_active', 'is_superuser', 'is_staff', 'is_mentor'), 'groups', 'user_permissions']}
        ),
        (
            'تاریخ ها',
            {'fields': [('date_joined', 'last_login')]}
        ),
    )

    add_fieldsets = [
        (
            None,
            {
                'fields': ['username', 'email', 'phone_number', 'password1', 'password2']
            }
        )
    ]


@admin.register(Profile)
class ProfileRegister(admin.ModelAdmin):
    list_display = [field.name for field in Profile._meta.fields]
    list_select_related = ['user']


@admin.register(OTPCode)
class OTPCodeRegister(admin.ModelAdmin):
    list_display = [field.name for field in OTPCode._meta.fields]
    list_filter = ['code_type']
