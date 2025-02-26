from random import randint
from django import forms
from user.models import Profile, User, OTPCode
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta


class RecaptchaFrom(forms.Form):
    recaptcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'password-input p-relative'}), label='پسورد')
    password2 = forms.CharField(max_length=100, widget=forms.PasswordInput(attrs={'class': 'password-input p-relative'}), label='تکرار پسورد')
    accept_rules = forms.BooleanField(widget=forms.CheckboxInput, label='پذیرش قوانین')

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number']

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise ValidationError('passwords dont match')
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        Profile.objects.create(user=user)
        return user

    def send_otp_code_to_number(self):
        code = randint(12121, 98989)
        otp = OTPCode.objects.create(phone_number = self.cleaned_data['phone_number'], expire_time = timedelta(minutes=4) + timezone.now(), code = code, code_type = 'register')
        # add send code statement here
        return True if otp else False


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='نام کاربری')
    password = forms.CharField(max_length=150, widget=forms.PasswordInput, label='پسورد')


class ChangePasswordForgotPasswordFrom(forms.Form):
    password1 = forms.CharField(label='پسورد', widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور'}))
    password2 = forms.CharField(label='تکرار پسورد', widget=forms.PasswordInput(attrs={'placeholder': 'تکرار رمز عبور'}))
    code = forms.IntegerField(label='کد ارسال شده', widget=forms.NumberInput(attrs={'placeholder': 'کد ارسال شده'}))

    def clean(self):
        cleaned_data = self.cleaned_data
        password1, password2 = cleaned_data.get("password1", None), cleaned_data.get("password2", None)

        if (
            not password1
            or not password2
            or len(password1) < 7
            or password1.isnumeric()
            or password1.isalpha()
        ):
            raise ValidationError("لطفا پسورد قوی با توجه با نکات امنیتی انتخاب کنید.")
        if password1 != password2:
            raise ValidationError('پسورد ها با هم مطابقت ندارند.')
        return cleaned_data
