from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    """
    Custom User model manager for email and phone_number unique
    """
    def create_user(self, email, phone_number, password, **extra_fields):
        if not email:
            raise ValidationError("ایمیل باید وارد شود.")
        # if not phone_number:
        #     raise ValidationError("ایمیل باید وارد شود.")
        # if not email:
        #     raise ValidationError("ایمیل باید وارد شود.")
        elif not password:
            raise ValidationError("پسورد باید وارد شود.")
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, phone_number, password, **extra_fields):
        from .models import Profile

        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        user = self.create_user(email, phone_number, password, **extra_fields)
        Profile.objects.create(user = user)
        return user
