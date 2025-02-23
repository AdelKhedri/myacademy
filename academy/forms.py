from random import randint
from django import forms
from user.models import Profile, User, OTPCode
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django.core.exceptions import ValidationError


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
        otp = OTPCode.objects.create(phone_number = self.cleaned_data['phone_number'], code = code, code_type = 'register')
        # add send code statement here
        return True if otp else False


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, label='نام کاربری')
    password = forms.CharField(max_length=150, widget=forms.PasswordInput, label='پسورد')
